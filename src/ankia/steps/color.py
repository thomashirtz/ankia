"""Fill tone-colored fields from LLM pinyin (alignment only)."""
from __future__ import annotations

from ankia.color.align import color_hanzi, color_synonyms, nfc
from ankia.schemas.card import Card


def color_card(card: Card) -> Card:
    warnings = list(card.warnings)

    colored, warn = color_hanzi(card.word_simplified, card.word_pinyin)
    card.word_simplified_colored = colored
    if warn:
        warnings.append(warn)

    colored, warn = color_hanzi(card.word_traditional, card.word_pinyin)
    card.word_traditional_colored = colored
    if warn:
        warnings.append(warn)

    colored, warn = color_hanzi(card.sentence_simplified, card.sentence_pinyin)
    card.sentence_simplified_colored = colored
    if warn:
        warnings.append(warn)

    colored, warn = color_hanzi(card.definition_simplified, card.definition_pinyin)
    card.definition_simplified_colored = colored
    if warn:
        warnings.append(warn)

    syn_colored, syn_warns = color_synonyms(card.synonyms)
    card.synonyms_colored = syn_colored
    warnings.extend(syn_warns)

    simp = nfc(card.word_simplified)
    card.hint = simp[0] if simp else ""
    card.warnings = warnings
    return card
