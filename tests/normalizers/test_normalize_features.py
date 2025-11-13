"""Tests for normalize_features function."""

from __future__ import annotations

from typing import Any

import pytest

from nlp_utilities.normalizers import normalize_features


def test_normalize_features_valid() -> None:
    """Test normalizing features with valid data."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1, 'Acc': 1},
                'verb': {'Nom': 0},
            },
        },
        'Gender': {
            'byupos': {
                'noun': {'Masc': 1, 'Fem': 1},
            },
        },
    }
    features = {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom', 'Gender': 'Masc'}


def test_normalize_features_string_input() -> None:
    """Test normalizing features with string input."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1},
            },
        },
    }
    features = 'Case=Nom|Number=Sing'
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom'}


def test_normalize_features_missing_upos_raises_error() -> None:
    """Test that missing UPOS raises ValueError."""
    with pytest.raises(ValueError, match='Must pass UPOS, FEATS, and a Feature set'):
        normalize_features(None, {}, {})


def test_normalize_features_missing_featset_raises_error() -> None:
    """Test that missing feature set raises ValueError."""
    with pytest.raises(ValueError, match='Must pass UPOS, FEATS, and a Feature set'):
        normalize_features('NOUN', {}, None)


def test_normalize_features_none_features() -> None:
    """Test with None features returns None."""
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    assert normalize_features('noun', None, featset) is None  # type: ignore [arg-type]


def test_normalize_features_empty_features() -> None:
    """Test with empty features dict."""
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    result = normalize_features('noun', {}, featset)
    assert result == {}


def test_normalize_features_empty_string() -> None:
    """Test with empty feature string."""
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    result = normalize_features('noun', '', featset)
    assert result == {}


def test_normalize_features_underscore_string() -> None:
    """Test with underscore feature string (CoNLL-U empty marker)."""
    featset = {'Case': {'byupos': {'noun': {'Nom': 1}}}}
    result = normalize_features('noun', '_', featset)
    assert result == {}


def test_normalize_features_filters_invalid_value() -> None:
    """Test that invalid feature values are filtered out."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1, 'Acc': 0},  # Acc is invalid (0)
            },
        },
    }
    features = {'Case': 'Acc'}
    result = normalize_features('noun', features, featset)
    assert result == {}


def test_normalize_features_filters_wrong_upos() -> None:
    """Test that features for wrong UPOS are filtered out."""
    featset = {
        'Case': {
            'byupos': {
                'verb': {'Nom': 1},  # Only valid for verb
            },
        },
    }
    features = {'Case': 'Nom'}
    result = normalize_features('noun', features, featset)
    assert result == {}


def test_normalize_features_filters_missing_attribute() -> None:
    """Test that features not in feature set are filtered out."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1},
            },
        },
    }
    features = {'Case': 'Nom', 'UnknownAttr': 'Value'}
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom'}


def test_normalize_features_multiple_valid_features() -> None:
    """Test normalizing multiple valid features."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1, 'Gen': 1, 'Dat': 1},
            },
        },
        'Gender': {
            'byupos': {
                'noun': {'Masc': 1, 'Fem': 1, 'Neut': 1},
            },
        },
        'Number': {
            'byupos': {
                'noun': {'Sing': 1, 'Plur': 1},
            },
        },
    }
    features = {'Case': 'Gen', 'Gender': 'Fem', 'Number': 'Plur'}
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Gen', 'Gender': 'Fem', 'Number': 'Plur'}


def test_normalize_features_mixed_valid_invalid() -> None:
    """Test normalizing with mix of valid and invalid features."""
    featset = {
        'Case': {
            'byupos': {
                'noun': {'Nom': 1, 'Acc': 1},
            },
        },
        'Gender': {
            'byupos': {
                'noun': {'Masc': 1, 'Fem': 0},  # Fem is invalid
            },
        },
    }
    features = {'Case': 'Nom', 'Gender': 'Fem'}
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom'}


def test_normalize_features_feature_not_in_upos() -> None:
    """Test feature that exists but not for the given UPOS."""
    featset = {
        'VerbForm': {
            'byupos': {
                'verb': {'Fin': 1, 'Inf': 1},
            },
        },
    }
    features = {'VerbForm': 'Fin'}
    result = normalize_features('noun', features, featset)
    assert result == {}


def test_normalize_features_upos_case_sensitive() -> None:
    """Test that UPOS matching is case-sensitive."""
    featset = {
        'Case': {
            'byupos': {
                'NOUN': {'Nom': 1},  # Uppercase UPOS
            },
        },
    }
    features = {'Case': 'Nom'}
    result = normalize_features('noun', features, featset)  # Lowercase
    assert result == {}


def test_normalize_features_complex_string_input() -> None:
    """Test with complex feature string."""
    featset = {
        'Case': {'byupos': {'noun': {'Nom': 1}}},
        'Gender': {'byupos': {'noun': {'Masc': 1}}},
        'Number': {'byupos': {'noun': {'Sing': 1}}},
    }
    features = 'Case=Nom|Gender=Masc|Number=Sing'
    result = normalize_features('noun', features, featset)
    assert result == {'Case': 'Nom', 'Gender': 'Masc', 'Number': 'Sing'}


def test_normalize_features_preserves_order() -> None:
    """Test that feature order is preserved in output."""
    featset = {
        'A': {'byupos': {'noun': {'Val': 1}}},
        'B': {'byupos': {'noun': {'Val': 1}}},
        'C': {'byupos': {'noun': {'Val': 1}}},
    }
    features = {'C': 'Val', 'A': 'Val', 'B': 'Val'}
    result = normalize_features('noun', features, featset)
    # Dict preserves insertion order in Python 3.7+
    assert result is not None
    assert list(result.keys()) == ['C', 'A', 'B']


def test_normalize_features_empty_byupos() -> None:
    """Test with empty byupos dict."""
    featset: dict[str, Any] = {
        'Case': {
            'byupos': {},
        },
    }
    features = {'Case': 'Nom'}
    result = normalize_features('noun', features, featset)
    assert result == {}
