"""Example provider-token adapter."""

from __future__ import annotations

from catalyst.boundary.ports.provider_token_port import ProviderTokenMeasure


class ExampleProviderTokenizer:
    """Example adapter for model-token budget mapping."""

    def __init__(
        self,
        *,
        provider: str = "example",
        model_identity: str = "example-model",
        tokenizer_name: str = "character-window-estimate",
        characters_per_token: int = 4,
    ) -> None:
        if characters_per_token <= 0:
            raise ValueError("characters_per_token must be positive")
        self.provider = provider
        self.model_identity = model_identity
        self.tokenizer_name = tokenizer_name
        self.characters_per_token = characters_per_token

    def measure(self, text: str) -> ProviderTokenMeasure:
        tokens = (len(text) + self.characters_per_token - 1) // self.characters_per_token
        return ProviderTokenMeasure(
            token_count=tokens,
            provider=self.provider,
            model_identity=self.model_identity,
            tokenizer_name=self.tokenizer_name,
        )
