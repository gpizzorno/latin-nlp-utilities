"""Tests for Score class."""

from __future__ import annotations

import pytest
from conllu_tools.evaluation.base import Score

from tests.helpers.assertion import assert_score_equals


def test_score_creation(simple_score: Score) -> None:
    """Test Score creation with all fields."""
    assert simple_score.gold_total == 10
    assert simple_score.system_total == 10
    assert simple_score.correct == 8
    assert simple_score.aligned_total is None


def test_score_precision_calculation(simple_score: Score) -> None:
    """Test Score precision calculation (correct/system_total)."""
    # 8/10 = 0.8
    assert simple_score.precision == 0.8


def test_score_recall_calculation(simple_score: Score) -> None:
    """Test Score recall calculation (correct/gold_total)."""
    # 8/10 = 0.8
    assert simple_score.recall == 0.8


def test_score_f1_calculation(simple_score: Score) -> None:
    """Test Score F1 calculation (2*correct/(system_total+gold_total))."""
    # 2*8/(10+10) = 16/20 = 0.8
    assert simple_score.f1 == 0.8


def test_score_aligned_accuracy_calculation(score_with_aligned_total: Score) -> None:
    """Test Score aligned_accuracy calculation."""
    # 8/9 ≈ 0.8889
    assert score_with_aligned_total.aligned_accuracy is not None
    assert abs(score_with_aligned_total.aligned_accuracy - (8 / 9)) < 1e-6


def test_score_with_zero_totals() -> None:
    """Test Score with zero totals (division by zero handling)."""
    score = Score(gold_total=0, system_total=0, correct=0)
    assert score.precision == 0.0
    assert score.recall == 0.0
    assert score.f1 == 0.0


def test_score_with_none_values() -> None:
    """Test Score with None values."""
    score = Score(gold_total=None, system_total=None, correct=None)
    assert score.precision == 0.0
    assert score.recall == 0.0
    assert score.f1 == 0.0


def test_score_precision_when_system_total_zero() -> None:
    """Test Score precision when system_total=0."""
    score = Score(gold_total=10, system_total=0, correct=0)
    assert score.precision == 0.0


def test_score_recall_when_gold_total_zero() -> None:
    """Test Score recall when gold_total=0."""
    score = Score(gold_total=0, system_total=10, correct=0)
    assert score.recall == 0.0


def test_score_f1_when_both_totals_zero() -> None:
    """Test Score F1 when both totals=0."""
    score = Score(gold_total=0, system_total=0, correct=0)
    assert score.f1 == 0.0


def test_score_perfect(perfect_score: Score) -> None:
    """Test perfect Score (all correct)."""
    assert perfect_score.precision == 1.0
    assert perfect_score.recall == 1.0
    assert perfect_score.f1 == 1.0


def test_score_zero(zero_score: Score) -> None:
    """Test zero Score (none correct)."""
    assert zero_score.precision == 0.0
    assert zero_score.recall == 0.0
    assert zero_score.f1 == 0.0


def test_score_aligned_accuracy_none_when_no_aligned_total() -> None:
    """Test aligned_accuracy is None when aligned_total is None."""
    score = Score(gold_total=10, system_total=10, correct=8, aligned_total=None)
    assert score.aligned_accuracy is None


def test_score_aligned_accuracy_none_when_aligned_total_zero() -> None:
    """Test aligned_accuracy is None when aligned_total is 0."""
    score = Score(gold_total=10, system_total=10, correct=0, aligned_total=0)
    assert score.aligned_accuracy is None


def test_assert_score_equals_helper() -> None:
    """Test assert_score_equals helper function."""
    score1 = Score(gold_total=10, system_total=10, correct=8)
    score2 = Score(gold_total=10, system_total=10, correct=8)

    # Should not raise
    assert_score_equals(score1, score2)


def test_assert_score_equals_fails_on_mismatch() -> None:
    """Test assert_score_equals raises on mismatch."""
    score1 = Score(gold_total=10, system_total=10, correct=8)
    score2 = Score(gold_total=10, system_total=10, correct=9)

    with pytest.raises(AssertionError, match='correct mismatch'):
        assert_score_equals(score1, score2)


def test_score_with_different_gold_system_totals() -> None:
    """Test Score with different gold and system totals."""
    score = Score(gold_total=10, system_total=12, correct=8)

    # Precision: 8/12 = 0.6667
    assert abs(score.precision - (8 / 12)) < 1e-6

    # Recall: 8/10 = 0.8
    assert abs(score.recall - 0.8) < 1e-6

    # F1: 2*8/(10+12) = 16/22 = 0.7273
    assert abs(score.f1 - (16 / 22)) < 1e-6
