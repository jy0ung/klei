"""
Lab module — Autonomous model creation via Autoresearch-style experiment loop.

The Lab can:
1. Generate synthetic training data from interactions
2. Fine-tune a specialized model on user-specific tasks
3. Run Autoresearch-style experiments (modify → train → evaluate → keep/revert)
4. Benchmark with fixed-time-budget experiments
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from haki.config import config
from haki.organism import Organism

logger = logging.getLogger(__name__)


@dataclass
class ExperimentResult:
    id: str
    description: str
    status: str  # "success", "failed", "aborted"
    val_bpb: float | None = None
    val_loss: float | None = None
    training_seconds: float = 0.0
    peak_vram_mb: float = 0.0
    total_tokens: int = 0
    num_params: float = 0.0
    description_text: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "val_bpb": self.val_bpb,
            "val_loss": self.val_loss,
            "training_seconds": self.training_seconds,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, str) else self.created_at,
        }


class Lab(Organism):
    """
    Autonomous model creation lab.

    Follows the Autoresearch pattern:
    1. Modify training code/config with an experimental idea
    2. Run fixed-budget training
    3. Evaluate (val_bpb or val_loss)
    4. Keep if improved, revert if worse
    5. Repeat indefinitely
    """

    def __init__(self):
        super().__init__("Lab")
        self._lab_dir = config.lab_dir
        self._lab_dir.mkdir(parents=True, exist_ok=True)
        self._results: list[ExperimentResult] = []
        self._best_val_bpb: float | None = None
        self._best_model_path: Path | None = None
        self._running = False

    async def initialize(self) -> None:
        """Set up lab environment."""
        (self._lab_dir / "experiments").mkdir(exist_ok=True)
        (self._lab_dir / "models").mkdir(exist_ok=True)
        (self._lab_dir / "data").mkdir(exist_ok=True)
        (self._lab_dir / "logs").mkdir(exist_ok=True)
        self.pulse("initialized")
        logger.info("Lab initialized at %s", self._lab_dir)

    async def create_training_data_from_memory(self, allow_seed: bool = True) -> Path:
        """
        Generate synthetic fine-tuning data from memory graph interactions.
        Creates instruction-response pairs. Optionally seeds baseline pairs
        when history is thin.
        """
        from haki.memory import memory
        interactions = await memory.get_recent_interactions(n=1000)

        data_path = self._lab_dir / "data" / "training.jsonl"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with open(data_path, "w", encoding="utf-8") as f:
            for ix in interactions:
                if ix.get("user_input") and ix.get("assistant_output"):
                    entry = {
                        "instruction": ix["user_input"],
                        "response": ix["assistant_output"],
                        "source": "interaction",
                    }
                    f.write(json.dumps(entry) + "\n")
                    count += 1

            # Seed minimal domain pairs if under threshold
            if allow_seed and count < config.lab_min_training_pairs:
                for pair in self._seed_training_pairs():
                    f.write(json.dumps(pair) + "\n")
                    count += 1

        self.pulse("create_training_data", output_bytes=data_path.stat().st_size if data_path.exists() else 0)
        logger.info("Generated %d training pairs (seed=%s).", count, allow_seed)
        return data_path

    def _seed_training_pairs(self) -> list[dict[str, str]]:
        """Baseline instruction pairs so Lab can operate before real history exists."""
        return [
            {
                "instruction": "What is Haki?",
                "response": "Haki is a cognitive OS with brain, memory, wiki, self-healing, and model lab.",
                "source": "seed",
            },
            {
                "instruction": "How do I check system health?",
                "response": "Run `haki health` or ask the brain for status; health monitors brain, memory, rag, wiki, disk, bus.",
                "source": "seed",
            },
            {
                "instruction": "Explain the becoming philosophy.",
                "response": "To exist is to be in motion — Haki treats modules as living organisms that adapt, not static components.",
                "source": "seed",
            },
            {
                "instruction": "How does Kaizen apply to Haki?",
                "response": "Record small continuous improvements with `haki kaizen add`, fix root causes, measure, and compound.",
                "source": "seed",
            },
            {
                "instruction": "What should I do before fine-tuning?",
                "response": "Chat to accumulate interactions, or use seed pairs; then run `haki lab` with enough training pairs.",
                "source": "seed",
            },
        ]

    def training_pair_count(self, data_path: Path | None = None) -> int:
        path = data_path or (self._lab_dir / "data" / "training.jsonl")
        if not path.exists() or path.stat().st_size == 0:
            return 0
        with open(path, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())

    async def fine_tune_model(self, model_id: str | None = None, epochs: int = 1,
                               time_budget_seconds: int | None = None,
                               allow_seed: bool = True) -> ExperimentResult:
        """
        Fine-tune a small model on collected interaction data.
        Uses PEFT/LoRA for efficient training.
        """
        exp_id = str(uuid.uuid4())[:8]
        result = ExperimentResult(
            id=exp_id,
            description=f"fine-tune-{model_id or config.narrow_model_id}",
            status="running",
        )

        # Kaizen: fail fast before heavy imports if no training data
        data_path = await self.create_training_data_from_memory(allow_seed=allow_seed)
        pair_count = self.training_pair_count(data_path)
        if pair_count == 0:
            result.status = "failed"
            result.description_text = "No training data available — interact more first"
            self.error()
            self._results.append(result)
            await self._save_results()
            return result

        if pair_count < config.lab_min_training_pairs:
            result.status = "failed"
            result.description_text = (
                f"Need at least {config.lab_min_training_pairs} training pairs "
                f"(have {pair_count})"
            )
            self.error()
            self._results.append(result)
            await self._save_results()
            return result

        try:
            import torch
            from transformers import (
                AutoModelForCausalLM, AutoTokenizer,
                TrainingArguments, Trainer,
            )
            from peft import LoraConfig, get_peft_model, TaskType
            from datasets import load_dataset
        except Exception as e:
            result.status = "failed"
            result.description_text = f"Training deps unavailable: {e}"
            self.error()
            self._results.append(result)
            await self._save_results()
            return result

        model_id = model_id or config.base_model_id or config.narrow_model_id
        output_dir = self._lab_dir / "models" / exp_id
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            start = time.perf_counter()
            use_cuda = config.lab_gpu and torch.cuda.is_available()

            # Load model
            tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=config.models_dir)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if use_cuda else torch.float32,
                device_map="auto" if use_cuda else "cpu",
                cache_dir=config.models_dir,
                low_cpu_mem_usage=True,
            )

            # Apply LoRA (target modules common to Llama/Qwen/Smol families)
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,
                lora_alpha=16,
                lora_dropout=0.05,
                target_modules=["q_proj", "v_proj"],
            )
            model = get_peft_model(model, lora_config)

            # Load dataset
            dataset = load_dataset("json", data_files=str(data_path), split="train")

            def tokenize_fn(examples):
                prompts = [f"### Instruction:\n{inst}\n\n### Response:\n{resp}"
                          for inst, resp in zip(examples["instruction"], examples["response"])]
                return tokenizer(prompts, truncation=True, max_length=256, padding="max_length")

            tokenized = dataset.map(tokenize_fn, batched=True)

            training_args = TrainingArguments(
                output_dir=str(output_dir),
                num_train_epochs=epochs,
                per_device_train_batch_size=1,
                gradient_accumulation_steps=4,
                logging_steps=10,
                save_steps=50,
                save_total_limit=1,
                fp16=use_cuda,
                max_steps=int(time_budget_seconds / 10) if time_budget_seconds else -1,
                report_to=[],
            )

            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized,
            )

            trainer.train()

            # Evaluate
            eval_result = trainer.evaluate()
            result.val_loss = eval_result.get("eval_loss")
            result.training_seconds = time.perf_counter() - start
            result.status = "success"

            # Calculate val_bpb approximation
            if result.val_loss is not None:
                import math
                result.val_bpb = result.val_loss / math.log(2)

            # Save LoRA adapter
            adapter_dir = output_dir / "adapter"
            model.save_pretrained(str(adapter_dir))
            tokenizer.save_pretrained(str(adapter_dir))

            # Track best + self-replace brain
            if result.val_bpb is not None and (
                self._best_val_bpb is None or result.val_bpb < self._best_val_bpb
            ):
                self._best_val_bpb = result.val_bpb
                self._best_model_path = adapter_dir
                result.description_text = "NEW BEST"
                self.adapt("new best model", {"val_bpb": result.val_bpb, "path": str(adapter_dir)})
                if config.lab_auto_promote:
                    promote = await self.promote_to_brain(
                        adapter_dir,
                        val_bpb=result.val_bpb,
                        base_model=model_id,
                        description=result.description,
                    )
                    result.description_text = f"NEW BEST + PROMOTED gen={promote.get('generation')}"
            else:
                result.description_text = "experiment completed (not better)"

            # Log VRAM
            if use_cuda:
                result.peak_vram_mb = torch.cuda.max_memory_allocated() / 1024 / 1024

            self.pulse("fine_tune", output_bytes=int(result.training_seconds * 1000))

        except Exception as e:
            logger.error("Fine-tune experiment %s failed: %s", exp_id, e)
            result.status = "failed"
            result.description_text = str(e)
            self.error()

        self._results.append(result)
        await self._save_results()
        return result

    async def promote_to_brain(
        self,
        adapter_path: Path,
        val_bpb: float | None = None,
        base_model: str | None = None,
        description: str = "",
    ) -> dict:
        """Replace the living brain with this adapter (self-evolution)."""
        from haki.brain import brain
        return await brain.promote_adapter(
            adapter_path=adapter_path,
            val_bpb=val_bpb,
            base_model=base_model or config.base_model_id,
            description=description,
        )

    async def evolve_once(self, epochs: int = 1) -> ExperimentResult:
        """
        One self-evolution cycle: train on memory → maybe replace active brain.
        This is the Autoresearch-style 'use myself to improve myself' step.
        """
        await self.initialize()
        idea = self._generate_idea(len(self._results))
        result = await self.fine_tune_model(
            model_id=config.base_model_id,
            epochs=epochs,
            time_budget_seconds=config.lab_time_budget_seconds,
            allow_seed=True,
        )
        result.description = idea
        self.pulse("evolve_once")
        return result

    async def evolve_loop(self, max_experiments: int = 10) -> list[ExperimentResult]:
        """Run multiple self-evolution cycles; each may replace the brain."""
        import asyncio
        self._running = True
        out: list[ExperimentResult] = []
        for i in range(max_experiments):
            if not self._running:
                break
            logger.info("Self-evolution %d/%d", i + 1, max_experiments)
            result = await self.evolve_once(epochs=1)
            out.append(result)
            await asyncio.sleep(0.5)
        self._running = False
        return out

    async def run_autoresearch_loop(self, max_experiments: int = 100) -> None:
        """
        Autoresearch-style experiment loop.
        Generates ideas → train → evaluate → promote if better → repeat.
        """
        await self.evolve_loop(max_experiments=max_experiments)

    def _generate_idea(self, index: int) -> str:
        """Generate an experimental idea (placeholder for LLM-based generation)."""
        ideas = [
            "baseline (no changes)",
            "increase LoRA rank to 16",
            "increase LoRA alpha to 32",
            "add gradient clipping",
            "increase learning rate",
            "add warmup steps",
            "use cosine schedule",
            "target k_proj + q_proj + v_proj",
            "increase dropout to 0.1",
            "double batch size",
        ]
        return ideas[index % len(ideas)]

    async def _save_results(self) -> None:
        """Persist experiment results to TSV."""
        results_path = self._lab_dir / "results.tsv"
        with open(results_path, "w") as f:
            f.write("id\tval_bpb\tstatus\tdescription\ttraining_seconds\n")
            for r in self._results:
                f.write(f"{r.id}\t{r.val_bpb or ''}\t{r.status}\t{r.description}\t{r.training_seconds:.1f}\n")

    def get_results(self) -> list[ExperimentResult]:
        return list(self._results)

    def get_best_model(self) -> Path | None:
        return self._best_model_path

    def stop(self) -> None:
        self._running = False


import asyncio

# Singleton
lab = Lab()
