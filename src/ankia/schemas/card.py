from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass, field, fields
from typing import Any


TSV_COLUMNS: OrderedDict[str, str] = OrderedDict(
    [
        ("word_simplified", "Simplified"),
        ("word_simplified_colored", "SimplifiedColored"),
        ("word_traditional", "Traditional"),
        ("word_traditional_colored", "TraditionalColored"),
        ("word_pinyin", "Pinyin"),
        ("word_meaning", "Meaning"),
        ("hint", "Hint"),
        ("sentence_simplified", "SentenceSimplified"),
        ("sentence_simplified_colored", "SentenceSimplifiedColored"),
        ("sentence_meaning", "SentenceMeaning"),
        ("sentence_pinyin", "SentencePinyin"),
        ("synonyms", "Synonyms"),
        ("synonyms_colored", "SynonymsColored"),
        ("definition_simplified", "DictionarySimplified"),
        ("definition_simplified_colored", "DictionarySimplifiedColored"),
        ("definition_pinyin", "DictionaryPinyin"),
        ("definition_meaning", "DictionaryMeaning"),
    ]
)


@dataclass
class Card:
    """Flashcard state, filled step by step (extract → construct → color)."""

    word_simplified: str = ""
    word_traditional: str = ""
    word_pinyin: str = ""
    word_meaning: str = ""

    sentence_simplified: str = ""
    sentence_pinyin: str = ""
    sentence_meaning: str = ""

    synonyms: str = ""

    definition_simplified: str = ""
    definition_pinyin: str = ""
    definition_meaning: str = ""

    word_simplified_colored: str = ""
    word_traditional_colored: str = ""
    sentence_simplified_colored: str = ""
    synonyms_colored: str = ""
    definition_simplified_colored: str = ""
    hint: str = ""

    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Card:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
