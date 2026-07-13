"""
Brain module — dual-tier model orchestration.

Architecture inspired by CognitiveOS:
- Narrow model (local, fast, tiny): handles simple queries, routing, real-time decisions
- Wide model (remote, capable): reasoning, complex tasks, knowledge-intensive work

The brain decides which tier to use for each query.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from haki.config import config

logger = logging.getLogger(__name__)


class TierChoice(str, Enum):
    NARROW = "narrow"
    WIDE = "wide"


@dataclass
class BrainResponse:
    text: str
    tier: TierChoice
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str | None = None


class Brain:
    """
    Dual-tier brain that routes queries between a small local model
    and a capable wide model.
    """

    def __init__(self):
        self._narrow_model = None
        self._narrow_tokenizer = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load narrow model, set up wide model client."""
        if self._initialized:
            return

        # Try to load local narrow model (optional — requires GPU)
        try:
            await self._load_narrow_model()
            logger.info("Narrow model loaded: %s", config.narrow_model_id)
        except Exception as e:
            logger.warning("Could not load narrow model: %s. Will use wide model only.", e)

        self._initialized = True

    async def _load_narrow_model(self) -> None:
        """Load the narrow (small local) model."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._narrow_tokenizer = AutoTokenizer.from_pretrained(
            config.narrow_model_id, cache_dir=config.models_dir
        )
        self._narrow_model = AutoModelForCausalLM.from_pretrained(
            config.narrow_model_id,
            torch_dtype=torch.float16 if config.lab_gpu and torch.cuda.is_available() else torch.float32,
            device_map="auto" if config.lab_gpu and torch.cuda.is_available() else "cpu",
            cache_dir=config.models_dir,
        )
        self._narrow_model.eval()

    def _is_simple_query(self, query: str) -> bool:
        """Heuristic: is this query simple enough for the narrow model?"""
        simple_keywords = ["time", "date", "weather", "hi ", "hello", "yes", "no", "ok",
                          "tell me", "what is", "who is", "status", "health"]
        q = query.lower().strip()
        # Short queries with common patterns → narrow
        if len(q.split()) <= 10:
            for kw in simple_keywords:
                if kw in q:
                    return True
        return False

    async def think(self, query: str, force_tier: TierChoice | None = None) -> BrainResponse:
        """
        Process a query and return a response.
        Uses heuristic routing unless force_tier is specified.
        """
        import time
        start = time.perf_counter()

        if force_tier == TierChoice.NARROW or (force_tier is None and self._is_simple_query(query)):
            result = await self._run_narrow(query)
        else:
            result = await self._run_wide(query)

        result.latency_ms = (time.perf_counter() - start) * 1000
        return result

    async def _run_narrow(self, query: str) -> BrainResponse:
        """Run query through the narrow (local small) model."""
        if self._narrow_model is None:
            # Fallback to wide model if narrow unavailable
            return await self._run_wide(query)

        try:
            import torch
            messages = [{"role": "user", "content": query}]
            input_ids = self._narrow_tokenizer.apply_chat_template(
                messages, return_tensors="pt"
            ).to(self._narrow_model.device)

            with torch.no_grad():
                output = self._narrow_model.generate(
                    input_ids, max_new_tokens=256, do_sample=False, pad_token_id=self._narrow_tokenizer.eos_token_id
                )

            text = self._narrow_tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
            return BrainResponse(text=text, tier=TierChoice.NARROW, model=config.narrow_model_id)
        except Exception as e:
            logger.warning("Narrow model failed: %s, falling back to wide", e)
            return await self._run_wide(query)

    async def _run_wide(self, query: str) -> BrainResponse:
        """Run query through the wide (remote LLM API) model."""
        if not config.llm_api_key:
            return BrainResponse(
                text="Wide model not configured. Set HAKI_LLM_API_KEY in env.",
                tier=TierChoice.WIDE,
                error="no_api_key",
            )

        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{config.llm_api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {config.llm_api_key}"},
                    json={
                        "model": config.llm_model,
                        "messages": [{"role": "user", "content": query}],
                        "max_tokens": 1024,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return BrainResponse(
                    text=text,
                    tier=TierChoice.WIDE,
                    tokens_in=usage.get("prompt_tokens", 0),
                    tokens_out=usage.get("completion_tokens", 0),
                    model=config.llm_model,
                )
        except Exception as e:
            logger.error("Wide model failed: %s", e)
            return BrainResponse(text=f"Error: {e}", tier=TierChoice.WIDE, error=str(e))

    @property
    def narrow_loaded(self) -> bool:
        return self._narrow_model is not None

    @property
    def wide_configured(self) -> bool:
        return bool(config.llm_api_key)


# Singleton
brain = Brain()
