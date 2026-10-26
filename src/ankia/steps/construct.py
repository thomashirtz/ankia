"""Construct full card content (README LLM prompt, nearly verbatim + pinyin fields)."""
from __future__ import annotations

from pydantic import BaseModel

from ankia.color.align import nfc
from ankia.llm.client import GeminiClient
from ankia.schemas.card import Card

CONSTRUCT_SYSTEM = """\
Please create flashcard content for the given Chinese word. Fill every field carefully.

Each entry should include:

1.  **word_simplified**: The simplified version of the Chinese characters.
2.  **word_traditional**: The traditional version of the Chinese characters.
3.  **word_pinyin**: The pinyin transcription of the Chinese word, with **one space** between each syllable and proper tone markings. Never trust source pinyin blindly.
4.  **word_meaning**: The English meaning or translation of the word.
5.  **sentence_simplified**: A simple example sentence using the word in Chinese. Ensure this sentence provides good context for the word, especially if it's a polyphonic character.
6.  **sentence_pinyin**: The full pinyin for sentence_simplified, with one space between each syllable and proper tone markings (aligned to the Chinese characters; skip punctuation in the syllable stream).
7.  **sentence_meaning**: The English translation of the example sentence.
8.  **synonyms**: Up to three synonyms for the word, formatted as "SimplifiedCharacters (Pinyin) - Translation", separated by `<br>`. The pinyin in parentheses here should be for the synonym itself.
9.  **definition_simplified**: A short definition of the word in Chinese characters, giving a brief explanation of the term's meaning.
10. **definition_pinyin**: The full pinyin for definition_simplified, with one space between each syllable and proper tone markings.
11. **definition_meaning**: The English translation of the definition, giving a brief explanation of the term's meaning.

-----

### Example Input

向量 (vector)

-----

### Example Output (conceptual fields)

word_simplified: 向量
word_traditional: 向量
word_pinyin: xiàng liàng
word_meaning: vector
sentence_simplified: 我们需要计算这个向量的长度。
sentence_pinyin: wǒ men xū yào jì suàn zhè ge xiàng liàng de cháng dù
sentence_meaning: We need to calculate the length of this vector.
synonyms: 矢量 (shǐ liàng) - vector<br>量向 (liàng xiàng) - vector
definition_simplified: 数学中用于表示方向和大小的对象
definition_pinyin: shù xué zhōng yòng yú biǎo shì fāng xiàng hé dà xiǎo de duì xiàng
definition_meaning: object used in mathematics to represent direction and magnitude

-----

### Tips for Generating the Content:

1.  **Contextual Example Sentences**: The sentence should clearly demonstrate the usage of the word, which is especially important for words with multiple meanings or pronunciations (polyphonic characters). The sentence should help infer the correct context.
2.  **Synonym Formatting**: For synonyms, ensure each synonym follows the "SimplifiedCharacters (Pinyin) - Translation" format, with `<br>` separating multiple synonyms.
3.  **Short but Descriptive Definitions**: definition_simplified and definition_meaning should provide concise but informative definitions.
4.  **Accuracy**: Make sure traditional and simplified characters are accurately paired, and translations and meanings reflect the specific terms.
5.  **Simplicity in Sentences**: For sentence_simplified, do not put any special characters or numbers beyond standard Chinese characters, commas (，), and full stops (。). This helps avoid processing issues.
6.  **Word Spacing in Chinese Text**: For sentence_simplified and definition_simplified, do not insert spaces between Chinese characters.
"""


class ConstructResult(BaseModel):
    word_simplified: str
    word_traditional: str
    word_pinyin: str
    word_meaning: str
    sentence_simplified: str
    sentence_pinyin: str
    sentence_meaning: str
    synonyms: str
    definition_simplified: str
    definition_pinyin: str
    definition_meaning: str


def construct_card(client: GeminiClient, seed: Card) -> Card:
    user = (
        f"### Word\n\n"
        f"{seed.word_simplified} ({seed.word_meaning})\n"
        f"traditional hint: {seed.word_traditional}\n"
        f"pinyin hint (verify, do not trust blindly): {seed.word_pinyin}"
    )
    result = client.generate(schema=ConstructResult, system=CONSTRUCT_SYSTEM, user=user)
    data = {k: nfc(v).strip() if isinstance(v, str) else v for k, v in result.model_dump().items()}
    card = Card(**data)
    # keep seed identity if model drifts
    if seed.word_simplified and card.word_simplified != seed.word_simplified:
        card.warnings.append(
            f"construct changed headword {seed.word_simplified!r} → {card.word_simplified!r}; keeping seed"
        )
        card.word_simplified = seed.word_simplified
    return card
