from ankia.color.align import color_hanzi, color_synonyms, nfc, parse_pinyin_syllables


def test_polyphone_cizhong():
    html, warn = color_hanzi("刺中", "cì zhòng")
    assert warn is None
    assert 'tone-4">中' in html
    assert 'tone-4">刺' in html


def test_nfc_combining_marks():
    raw = "ci\u0300"
    assert parse_pinyin_syllables(raw) != parse_pinyin_syllables(nfc(raw)) or nfc(raw) != raw
    assert "ì" in nfc(raw)


def test_synonyms():
    colored, warns = color_synonyms("射中 (shè zhòng) - hit")
    assert "tone-" in colored
    assert not warns
