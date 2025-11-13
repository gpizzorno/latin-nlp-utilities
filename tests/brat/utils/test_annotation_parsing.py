"""Tests for BRAT annotation parsing functions."""

from __future__ import annotations

from typing import Any

from nlp_utilities.brat.utils import format_annotation, parse_annotation_line


def test_parse_entity_annotation_valid() -> None:
    """Test parsing of valid entity annotation line."""
    line = 'T1\tNOUN 0 5\tWord'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['type'] == 'T'
    assert result['id'] == 1
    assert result['upos'] == 'NOUN'
    assert result['start'] == 0
    assert result['end'] == 5  # noqa: PLR2004
    assert result['form'] == 'Word'


def test_parse_entity_with_multi_token_form() -> None:
    """Test parsing entity with multi-token form."""
    line = 'T5\tNOUN 10 20\tMulti Word'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['form'] == 'Multi Word'


def test_parse_entity_with_special_chars() -> None:
    """Test parsing entity with special characters in form."""
    line = 'T3\tPUNCT 5 6\t.'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['form'] == '.'


def test_parse_entity_with_unicode() -> None:
    """Test parsing entity with Unicode characters."""
    line = 'T2\tNOUN 0 5\tναός'  # noqa: RUF001
    result = parse_annotation_line(line)
    assert result is not None
    assert result['form'] == 'ναός'


def test_parse_entity_with_punct_upos() -> None:
    """Test parsing entity with punctuation UPOS."""
    line = 'T10\tPUNCT 42 43\t,'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['upos'] == 'PUNCT'


def test_parse_entity_with_safe_typed_upos() -> None:
    """Test parsing entity with safe-typed UPOS."""
    line = 'T7\t_colon_ 0 1\t:'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['upos'] == '_colon_'


def test_parse_relation_annotation_valid() -> None:
    """Test parsing of valid relation annotation line."""
    line = 'R1\tpunct Arg1:T3 Arg2:T4'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['type'] == 'R'
    assert result['id'] == 1
    assert result['deprel'] == 'punct'
    assert result['head'] == 3  # noqa: PLR2004
    assert result['dep'] == 4  # noqa: PLR2004


def test_parse_relation_with_safe_typed_deprel() -> None:
    """Test parsing relation with safe-typed deprel."""
    line = 'R2\tnsubj_colon_pass Arg1:T1 Arg2:T2'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['deprel'] == 'nsubj_colon_pass'


def test_parse_relation_with_extended_deprel() -> None:
    """Test parsing relation with extended deprel."""
    line = 'R5\tobl_colon_arg Arg1:T10 Arg2:T11'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['deprel'] == 'obl_colon_arg'


def test_parse_line_insufficient_parts() -> None:
    """Test parsing line with insufficient parts."""
    line = 'T1'
    result = parse_annotation_line(line)
    assert result is None


def test_parse_line_empty() -> None:
    """Test parsing empty line."""
    line = ''
    result = parse_annotation_line(line)
    assert result is None


def test_parse_line_unknown_type() -> None:
    """Test parsing line with unknown annotation type."""
    line = 'X1\tSOMETHING 0 5\tData'
    result = parse_annotation_line(line)
    assert result is None


def test_parse_entity_zero_length_span() -> None:
    """Test parsing entity with zero-length span returns None (not supported)."""
    line = 'T8\tX 5 5\t'
    result = parse_annotation_line(line)
    # Zero-length spans result in empty form, which makes the annotation invalid
    assert result is None


def test_parse_entity_with_whitespace_in_form() -> None:
    """Test parsing entity with whitespace in form."""
    line = 'T9\tNOUN 0 10\tsome  text'
    result = parse_annotation_line(line)
    assert result is not None
    assert result['form'] == 'some  text'


def test_format_entity_annotation() -> None:
    """Test formatting entity annotation correctly."""
    ann: dict[str, Any] = {
        'type': 'T',
        'id': 1,
        'upos': 'NOUN',
        'start': 0,
        'end': 5,
        'form': 'Word',
    }
    result = format_annotation(ann)
    assert result == 'T1\tNOUN 0 5\tWord'


def test_format_relation_annotation() -> None:
    """Test formatting relation annotation correctly."""
    ann: dict[str, Any] = {
        'type': 'R',
        'id': 1,
        'deprel': 'punct',
        'head': 3,
        'dep': 4,
    }
    result = format_annotation(ann)
    assert result == 'R1\tpunct Arg1:T3 Arg2:T4'


def test_format_annotation_with_safe_types() -> None:
    """Test formatting annotation with safe types."""
    ann: dict[str, Any] = {
        'type': 'R',
        'id': 2,
        'deprel': 'nsubj_colon_pass',
        'head': 1,
        'dep': 2,
    }
    result = format_annotation(ann)
    assert result == 'R2\tnsubj_colon_pass Arg1:T1 Arg2:T2'


def test_format_annotation_with_special_chars() -> None:
    """Test formatting annotation with special characters in form."""
    ann: dict[str, Any] = {
        'type': 'T',
        'id': 3,
        'upos': 'PUNCT',
        'start': 5,
        'end': 6,
        'form': '.',
    }
    result = format_annotation(ann)
    assert result == 'T3\tPUNCT 5 6\t.'


def test_round_trip_parse_format_entity() -> None:
    """Test that parse → format → parse yields same result for entity."""
    line = 'T5\tVERB 10 15\ttest'
    parsed = parse_annotation_line(line)
    assert parsed is not None
    formatted = format_annotation(parsed)
    reparsed = parse_annotation_line(formatted)
    assert reparsed == parsed


def test_round_trip_parse_format_relation() -> None:
    """Test that parse → format → parse yields same result for relation."""
    line = 'R7\tnmod Arg1:T10 Arg2:T11'
    parsed = parse_annotation_line(line)
    assert parsed is not None
    formatted = format_annotation(parsed)
    reparsed = parse_annotation_line(formatted)
    assert reparsed == parsed
