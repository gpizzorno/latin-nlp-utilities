"""Tests for DEPREL normalization helper functions ."""

from __future__ import annotations

from conllu_tools.evaluation.helpers import remove_deprel_subtype


def test_remove_deprel_subtype_with_base_relation() -> None:
    """Test remove_deprel_subtype with base relation (nmod)."""
    result = remove_deprel_subtype('nmod')
    assert result == 'nmod'


def test_remove_deprel_subtype_with_subtype() -> None:
    """Test remove_deprel_subtype with subtype (nmod:tmod)."""
    result = remove_deprel_subtype('nmod:tmod')
    assert result == 'nmod'


def test_remove_deprel_subtype_with_multiple_subtypes() -> None:
    """Test remove_deprel_subtype with multiple subtypes (obl:fake:extra)."""
    result = remove_deprel_subtype('obl:fake:extra')
    assert result == 'obl'


def test_remove_deprel_subtype_with_empty_string() -> None:
    """Test remove_deprel_subtype with empty string."""
    result = remove_deprel_subtype('')
    assert result == ''


def test_remove_deprel_subtype_various_relations() -> None:
    """Test remove_deprel_subtype with various relation types."""
    assert remove_deprel_subtype('root') == 'root'
    assert remove_deprel_subtype('advmod:emph') == 'advmod'
    assert remove_deprel_subtype('acl:relcl') == 'acl'
    assert remove_deprel_subtype('aux:pass') == 'aux'
    assert remove_deprel_subtype('advcl:abs') == 'advcl'
