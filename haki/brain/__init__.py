"""
Brain module — local-only tiny model that Lab can replace with better versions.

No cloud LLM API. The brain loads:
1. Base model (tiny, ~4GB-friendly, e.g. SmolLM2-360M)
2. Optional LoRA adapter from Lab's active_model.json (self-evolved)

Self-evolution path:
  interactions → Lab fine-tune → better val_bpb → promote adapter → brain.reload()
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from haki.config import config
from haki.organism import Organism

logger = logging.getLogger(__name__)


class TierChoice(str, Enum):
    """Kept for API compat; everything is LOCAL now."""
    LOCAL = "local"
    NARROW = "local"  # alias
    WIDE = "local"    # deprecated alias — never remote


@dataclass
class BrainResponse:
    text: str
    tier: TierChoice = TierChoice.LOCAL
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    adapter: str | None = None
    generation: int = 0
    error: str | None = None


class Brain(Organism):
    """
    Single local brain. Starts tiny, gets replaced by Lab when Lab finds better adapters.
    """

    def __init__(self):
        super().__init__("Brain")
        self._model = None
        self._tokenizer = None
        self._initialized = False
        self._base_model_id = config.base_model_id or config.narrow_model_id
        self._adapter_path: Path | None = None
        self._generation = 0
        self._best_val_bpb: float | None = None
        self._load_error: str | None = None

    async def initialize(self) -> None:
        """Load base model + active Lab adapter if present."""
        if self._initialized and self._model is not None:
            return

        registry = self._read_registry()
        if registry:
            self._base_model_id = registry.get("base_model", self._base_model_id)
            adapter = registry.get("adapter_path")
            self._adapter_path = Path(adapter) if adapter else None
            self._generation = int(registry.get("generation", 0))
            self._best_val_bpb = registry.get("val_bpb")

        try:
            await self._load_model(self._base_model_id, self._adapter_path)
            self._load_error = None
            logger.info(
                "Brain loaded base=%s adapter=%s gen=%s",
                self._base_model_id,
                self._adapter_path,
                self._generation,
            )
        except Exception as e:
            self._load_error = str(e)
            logger.warning("Could not load local brain model: %s", e)
            self._model = None
            self._tokenizer = None

        self._initialized = True
        self.pulse("initialized")

    def _read_registry(self) -> dict | None:
        path = config.active_model_registry
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to read active_model.json: %s", e)
            return None

    def _write_registry(self, data: dict) -> None:
        path = config.active_model_registry
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)  # atomic rename — no partial writes

    async def _load_model(self, base_id: str, adapter_path: Path | None) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        cache = config.models_dir
        cache.mkdir(parents=True, exist_ok=True)

        use_cuda = (not config.model_cpu) and torch.cuda.is_available() and config.lab_gpu
        dtype = torch.float16 if use_cuda else torch.float32
        device_map = "auto" if use_cuda else "cpu"

        self._tokenizer = AutoTokenizer.from_pretrained(base_id, cache_dir=cache)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        load_kwargs = {
            "cache_dir": cache,
            "torch_dtype": dtype,
            "device_map": device_map,
            "low_cpu_mem_usage": True,
        }
        if config.model_load_in_8bit and use_cuda:
            load_kwargs["load_in_8bit"] = True

        model = AutoModelForCausalLM.from_pretrained(base_id, **load_kwargs)

        if adapter_path and Path(adapter_path).exists():
            try:
                from peft import PeftModel
                model = PeftModel.from_pretrained(model, str(adapter_path))
                logger.info("Loaded LoRA adapter from %s", adapter_path)
            except Exception as e:
                logger.warning("Adapter load failed (%s); using base only", e)

        model.eval()
        self._model = model
        self._base_model_id = base_id
        self._adapter_path = adapter_path if adapter_path and Path(adapter_path).exists() else None

    async def reload(self) -> bool:
        """Hot-reload LoRA only — keeps base model in RAM (no re-download)."""
        if self._model is None or self._tokenizer is None:
            # No base loaded yet — full init
            self._initialized = False
            self._model = None
            self._tokenizer = None
            await self.initialize()
        elif self._adapter_path and Path(self._adapter_path).exists():
            # Base already in RAM — just swap LoRA
            try:
                from peft import PeftModel
                import torch
                self._model = PeftModel.from_pretrained(
                    self._model, str(self._adapter_path),
                )
                self._model.eval()
                logger.info("Hot-swapped LoRA adapter gen=%s", self._generation)
            except Exception as e:
                logger.warning("LoRA hot-swap failed (%s); using base", e)
                try:
                    self._model = self._model.base_model
                    self._model.eval()
                except Exception:
                    pass
        ok = self._model is not None
        if ok:
            self.adapt("reloaded active model", {
                "base": self._base_model_id,
                "adapter": str(self._adapter_path) if self._adapter_path else None,
                "generation": self._generation,
            })
        return ok

    async def promote_adapter(
        self,
        adapter_path: Path | str,
        val_bpb: float | None = None,
        base_model: str | None = None,
        description: str = "",
    ) -> dict:
        """Replace the living brain with a better Lab artifact."""
        adapter_path = Path(adapter_path)
        if not adapter_path.exists():
            return {"ok": False, "error": f"adapter missing: {adapter_path}"}

        if (
            val_bpb is not None
            and self._best_val_bpb is not None
            and val_bpb >= self._best_val_bpb
        ):
            return {
                "ok": False,
                "error": "not better",
                "current_val_bpb": self._best_val_bpb,
                "candidate_val_bpb": val_bpb,
            }

        new_gen = self._generation + 1
        base = base_model or self._base_model_id
        registry = {
            "base_model": base,
            "adapter_path": str(adapter_path),
            "val_bpb": val_bpb,
            "generation": new_gen,
            "description": description,
        }
        self._write_registry(registry)
        self._generation = new_gen
        self._best_val_bpb = val_bpb
        self._adapter_path = adapter_path

        reloaded = await self.reload()
        self.transform({
            "generation": new_gen,
            "adapter": str(adapter_path),
            "val_bpb": val_bpb,
        })
        self.pulse("promote", output_bytes=new_gen)
        return {"ok": reloaded, "generation": new_gen, "registry": registry}

    async def think(self, query: str, force_tier: TierChoice | None = None) -> BrainResponse:
        """Generate with the local (possibly self-evolved) model."""
        import time
        start = time.perf_counter()

        if not self._initialized:
            await self.initialize()

        if self._model is None or self._tokenizer is None:
            text = self._rule_fallback(query)
            result = BrainResponse(
                text=text,
                tier=TierChoice.LOCAL,
                model="rule-fallback",
                generation=self._generation,
                error=self._load_error or "model_not_loaded",
            )
        else:
            result = await self._generate(query)

        result.latency_ms = (time.perf_counter() - start) * 1000
        if result.error and result.model != "rule-fallback":
            self.error()
        else:
            self.pulse("think", input_bytes=len(query), output_bytes=len(result.text or ""))
        return result

    async def _generate(self, query: str) -> BrainResponse:
        try:
            import torch

            try:
                if hasattr(self._tokenizer, "apply_chat_template"):
                    messages = [{"role": "user", "content": query}]
                    encoded = self._tokenizer.apply_chat_template(
                        messages,
                        tokenize=True,
                        add_generation_prompt=True,
                        return_tensors="pt",
                    )
                    input_ids = encoded.input_ids if hasattr(encoded, "input_ids") else encoded
                else:
                    input_ids = self._tokenizer(query, return_tensors="pt").input_ids
            except Exception:
                input_ids = self._tokenizer(query, return_tensors="pt").input_ids

            if not hasattr(input_ids, "shape"):
                input_ids = self._tokenizer(query, return_tensors="pt").input_ids

            device = next(self._model.parameters()).device
            input_ids = input_ids.to(device)

            with torch.no_grad():
                output = self._model.generate(
                    input_ids=input_ids,
                    max_new_tokens=config.model_max_new_tokens,
                    do_sample=False,
                    pad_token_id=getattr(self._tokenizer, "eos_token_id", None),
                )

            text = self._tokenizer.decode(
                output[0][input_ids.shape[1]:], skip_special_tokens=True
            ).strip()
            label = self._base_model_id
            if self._adapter_path:
                label = f"{self._base_model_id}+adapter@gen{self._generation}"
            return BrainResponse(
                text=text or "(empty generation)",
                tier=TierChoice.LOCAL,
                model=label,
                adapter=str(self._adapter_path) if self._adapter_path else None,
                generation=self._generation,
                tokens_in=int(input_ids.shape[1]),
                tokens_out=int(output.shape[1] - input_ids.shape[1]),
            )
        except Exception as e:
            logger.error("Local generation failed: %s", e)
            return BrainResponse(
                text=self._rule_fallback(query),
                tier=TierChoice.LOCAL,
                model="rule-fallback",
                generation=self._generation,
                error=str(e),
            )

    def _rule_fallback(self, query: str) -> str:
        """Tiny non-neural brain so Haki stays usable while weights download / fail."""
        q = query.lower().strip()
        if any(w in q for w in ("hello", "hi ", "hey")):
            return (
                "Hello. I'm Haki's local brain (fallback mode). "
                "Once the tiny model loads, Lab can evolve and replace me with better versions of myself."
            )
        if "who are you" in q or "what are you" in q:
            return (
                "I'm Haki — a local-only cognitive OS. No cloud API. "
                "A small base model runs on this machine; the Lab fine-tunes LoRA adapters and promotes "
                "better ones into me so I improve myself."
            )
        if "health" in q or "status" in q:
            return (
                f"Brain status: loaded={self.local_loaded} base={self._base_model_id} "
                f"generation={self._generation} adapter={self._adapter_path} "
                f"load_error={self._load_error}"
            )
        if "evolve" in q or "lab" in q:
            return "Run `haki lab` or `haki evolve` to train a better adapter and replace the active brain if val_bpb improves."
        return (
            f"(local fallback) I heard: {query[:200]}. "
            "Model weights not loaded yet — try `haki brain` or wait for first download. "
            "After chat history builds, Lab will specialize me."
        )

    @property
    def local_loaded(self) -> bool:
        return self._model is not None

    @property
    def narrow_loaded(self) -> bool:
        return self.local_loaded

    @property
    def wide_configured(self) -> bool:
        return self.local_loaded or self._initialized

    def model_card(self) -> dict:
        return {
            "base_model": self._base_model_id,
            "adapter_path": str(self._adapter_path) if self._adapter_path else None,
            "generation": self._generation,
            "val_bpb": self._best_val_bpb,
            "loaded": self.local_loaded,
            "load_error": self._load_error,
            "mode": "local-only",
        }


# Singleton
brain = Brain()
