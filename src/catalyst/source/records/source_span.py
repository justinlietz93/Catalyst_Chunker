"""Source span identity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    """A traceable region of a source record."""

    source_id: str
    start_byte: int | None
    end_byte: int | None
    start_char: int
    end_char: int
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    element_id: str | None = None

    def __post_init__(self) -> None:
        if self.start_char < 0 or self.end_char < self.start_char:
            raise ValueError("source span character offsets are invalid")
        if self.start_byte is not None and self.end_byte is not None:
            if self.start_byte < 0 or self.end_byte < self.start_byte:
                raise ValueError("source span byte offsets are invalid")

    @property
    def char_length(self) -> int:
        return self.end_char - self.start_char

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "page_number": self.page_number,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "element_id": self.element_id,
        }
