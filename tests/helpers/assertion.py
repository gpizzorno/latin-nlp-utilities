"""Assertion helper functions for CoNLL-U validator tests."""

import json
from pathlib import Path
from typing import Any

from conllu_tools.evaluation.base import Score
from conllu_tools.validation.error_reporter import ErrorReporter


def assert_error_contains(
    reporter: ErrorReporter,
    type_or_id: str | None = None,
    message: str | None = None,
) -> None:
    """Check if error list contains specific error_id, test_id, or message content.

    At least one of type_or_id or message must be provided.

    Arguments:
        reporter: Instance of ErrorReporter from validator
        type_or_id: The error_type or test_id to search for
        message: Substring to search for in error message

    Raises:
        AssertionError: If error_id not found or message not in message
        ValueError: If neither type_or_id nor message is provided

    """
    if message is None and type_or_id is None:
        msg = 'At least one of type_or_id or message must be provided.'
        raise ValueError(msg)

    if reporter.get_error_count() == 0:
        msg = 'No errors found in validator output.'
        raise AssertionError(msg)

    matching_errors = []

    if type_or_id is not None:
        matching_errors = [e for e in reporter.errors if e[3].error_type == type_or_id or e[3].testid == type_or_id]

    if not matching_errors:
        error_list = [f'{e[3].error_type} ({e[3].testid})' for e in reporter.errors]
        msg = f"'{type_or_id}' not found in errors. Errors: {error_list}"
        raise AssertionError(msg)

    if message is not None:
        matching_errors = [e for e in matching_errors if message in e[3].msg]
        if not matching_errors:
            msg = (
                f"Message '{message}' not found in any error messages. Messages: {[e[3].msg for e in reporter.errors]}"
            )
            raise AssertionError(msg)


def assert_no_errors_of_type(reporter: ErrorReporter, error_id: str) -> None:
    """Assert that errors list doesn't contain specific error type.

    Arguments:
        reporter: Instance of ErrorReporter from validator
        error_id: The error_type that should not be present

    Raises:
        AssertionError: If error_id is found in errors

    """
    matching_errors = [e for e in reporter.errors if e[3].error_type == error_id]

    if matching_errors:
        msg = (
            f"Found {len(matching_errors)} error(s) of type '{error_id}' "
            f'when none were expected. Errors: {matching_errors}'
        )
        raise AssertionError(msg)


def assert_error_count(
    reporter: ErrorReporter,
    expected_count: int,
    type_or_id: str | None = None,
) -> None:
    """Assert exact number of errors (optionally filtered by error_type or test_id).

    Arguments:
        reporter: Instance of ErrorReporter from validator
        expected_count: Expected number of errors
        type_or_id: Optional error_type or test_id to filter by

    Raises:
        AssertionError: If error count doesn't match expected

    """
    if reporter.get_error_count() == 0 and expected_count != 0:
        msg = 'No errors found in validator output.'
        raise AssertionError(msg)

    error_list = [f'{e[3].error_type} ({e[3].testid})' for e in reporter.errors]

    if type_or_id is not None:
        filtered_errors = [e for e in reporter.errors if e[3].error_type == type_or_id or e[3].testid == type_or_id]
        actual_count = len(filtered_errors)
        if actual_count != expected_count:
            msg = f"Expected {expected_count} '{type_or_id}' error(s), but found {actual_count}. Errors: {error_list}"
            raise AssertionError(msg)
    else:
        actual_count = reporter.get_error_count()
        if actual_count != expected_count:
            msg = f'Expected {expected_count} total error(s), but found {actual_count}. Errors: {error_list}'
            raise AssertionError(msg)


def assert_valid_conllu(validator: Any, conllu_text: str) -> None:
    """Assert that CoNLL-U text validates without errors.

    Arguments:
        validator: ConlluValidator instance
        conllu_text: CoNLL-U formatted text to validate

    Raises:
        AssertionError: If validation produces any errors

    """
    errors = validator.validate_string(conllu_text)

    if errors:
        error_summary = '\n'.join(f'  - {e.get("error_type")}: {e.get("msg")}' for e in errors)
        msg = f'Expected valid CoNLL-U but found {len(errors)} error(s):\n{error_summary}'
        raise AssertionError(msg)


def assert_score_equals(
    actual: Score,
    expected: Score,
    tolerance: float = 1e-6,
) -> None:
    """Assert Score objects are equal within tolerance.

    Args:
        actual: Actual Score object
        expected: Expected Score object
        tolerance: Tolerance for floating point comparisons

    Raises:
        AssertionError: If scores don't match

    """
    assert actual.gold_total == expected.gold_total, (
        f'gold_total mismatch: {actual.gold_total} != {expected.gold_total}'
    )
    assert actual.system_total == expected.system_total, (
        f'system_total mismatch: {actual.system_total} != {expected.system_total}'
    )
    assert actual.correct == expected.correct, f'correct mismatch: {actual.correct} != {expected.correct}'
    assert actual.aligned_total == expected.aligned_total, (
        f'aligned_total mismatch: {actual.aligned_total} != {expected.aligned_total}'
    )

    # Check computed properties with tolerance
    assert abs(actual.precision - expected.precision) < tolerance, (
        f'precision mismatch: {actual.precision} != {expected.precision}'
    )
    assert abs(actual.recall - expected.recall) < tolerance, f'recall mismatch: {actual.recall} != {expected.recall}'
    assert abs(actual.f1 - expected.f1) < tolerance, f'f1 mismatch: {actual.f1} != {expected.f1}'

    # Check aligned_accuracy (can be None)
    if actual.aligned_accuracy is not None and expected.aligned_accuracy is not None:
        assert abs(actual.aligned_accuracy - expected.aligned_accuracy) < tolerance, (
            f'aligned_accuracy mismatch: {actual.aligned_accuracy} != {expected.aligned_accuracy}'
        )
    else:
        assert actual.aligned_accuracy == expected.aligned_accuracy, (
            f'aligned_accuracy mismatch: {actual.aligned_accuracy} != {expected.aligned_accuracy}'
        )


def assert_scores_match_baseline(
    actual: dict[str, Score],
    baseline_path: Path,
    tolerance: float = 1e-6,
) -> None:
    """Assert evaluation scores match baseline JSON.

    Args:
        actual: Dictionary of metric name to Score
        baseline_path: Path to baseline JSON file
        tolerance: Tolerance for floating point comparisons

    Raises:
        AssertionError: If scores don't match baseline

    """
    with baseline_path.open('r') as f:
        baseline = json.load(f)

    for metric_name, score in actual.items():
        assert metric_name in baseline, f'Metric {metric_name} not found in baseline'

        baseline_metric = baseline[metric_name]

        # Compare precision, recall, F1
        if 'precision' in baseline_metric:
            assert abs(score.precision - baseline_metric['precision']) < tolerance, (
                f'{metric_name} precision mismatch: {score.precision} != {baseline_metric["precision"]}'
            )
        if 'recall' in baseline_metric:
            assert abs(score.recall - baseline_metric['recall']) < tolerance, (
                f'{metric_name} recall mismatch: {score.recall} != {baseline_metric["recall"]}'
            )
        if 'f1' in baseline_metric:
            assert abs(score.f1 - baseline_metric['f1']) < tolerance, (
                f'{metric_name} f1 mismatch: {score.f1} != {baseline_metric["f1"]}'
            )
