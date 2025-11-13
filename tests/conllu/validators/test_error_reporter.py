"""Tests for error_reporter.py - Error reporting utilities for CoNLL-U validation."""

import pytest

from nlp_utilities.conllu.validators.error_reporter import ErrorEntry, ErrorReporter


def test_error_entry_creation() -> None:
    """Test ErrorEntry dataclass creation with all fields."""
    entry = ErrorEntry(
        alt_id='test-sent-1',
        testlevel=2,
        error_type='test-error',
        testid='test-001',
        msg='This is a test error',
        node_id='5',
        line_no=10,
        tree_counter=1,
    )

    assert entry.alt_id == 'test-sent-1'
    assert entry.testlevel == 2
    assert entry.error_type == 'test-error'
    assert entry.testid == 'test-001'
    assert entry.msg == 'This is a test error'
    assert entry.node_id == '5'
    assert entry.line_no == 10
    assert entry.tree_counter == 1


def test_error_entry_str_with_all_fields() -> None:
    """Test ErrorEntry string formatting with all fields present."""
    entry = ErrorEntry(
        alt_id='sent-42',
        testlevel=3,
        error_type='invalid-upos',
        testid='upos-001',
        msg='Invalid UPOS tag',
        node_id='7',
        line_no=15,
        tree_counter=2,
    )

    result = str(entry)
    assert 'Line 15' in result
    assert 'Sentence sent-42' in result
    assert '[L3 invalid-upos upos-001]' in result
    assert 'Invalid UPOS tag' in result


def test_error_entry_str_with_missing_line_no() -> None:
    """Test ErrorEntry string formatting when line_no is None."""
    entry = ErrorEntry(
        alt_id='sent-1',
        testlevel=1,
        error_type='test-error',
        testid='test-1',
        msg='Test message',
        node_id='1',
        line_no=None,
        tree_counter=1,
    )

    result = str(entry)
    assert 'Line' not in result or 'Line None' not in result
    assert 'Sentence sent-1' in result
    assert '[L1 test-error test-1]' in result
    assert 'Test message' in result


def test_error_entry_str_with_missing_alt_id() -> None:
    """Test ErrorEntry string formatting when alt_id is None."""
    entry = ErrorEntry(
        alt_id=None,
        testlevel=2,
        error_type='test-error',
        testid='test-2',
        msg='Test message',
        node_id='2',
        line_no=5,
        tree_counter=1,
    )

    result = str(entry)
    assert 'Line 5' in result
    assert 'Sentence None' not in result or result.count('Sentence') == 0
    assert '[L2 test-error test-2]' in result
    assert 'Test message' in result


def test_error_entry_str_with_all_optional_none() -> None:
    """Test ErrorEntry string formatting with all optional fields as None."""
    entry = ErrorEntry(
        alt_id=None,
        testlevel=1,
        error_type='error',
        testid='id',
        msg='message',
        node_id=None,
        line_no=None,
        tree_counter=None,
    )

    result = str(entry)
    assert '[L1 error id]' in result
    assert 'message' in result


def test_error_reporter_init(error_reporter: ErrorReporter) -> None:
    """Test ErrorReporter initialization with empty state."""
    assert error_reporter.errors == []
    assert error_reporter.error_counter == {}
    assert error_reporter.tree_counter == 0
    assert error_reporter.sentence_id is None
    assert error_reporter.sentence_mapid == {}


def test_error_reporter_init_creates_new_instance() -> None:
    """Test that each ErrorReporter instance is independent."""
    reporter1 = ErrorReporter()
    reporter2 = ErrorReporter()

    reporter1.warn('Error 1', 'test-error')
    reporter2.warn('Error 2', 'test-error')

    assert reporter1.get_error_count() == 1
    assert reporter2.get_error_count() == 1
    assert reporter1.errors != reporter2.errors


def test_reset_clears_errors(error_reporter: ErrorReporter) -> None:
    """Test that reset() clears the errors list."""
    error_reporter.warn('Test error', 'test-error')
    assert error_reporter.get_error_count() == 1

    error_reporter.reset()
    assert error_reporter.get_error_count() == 0
    assert error_reporter.errors == []


def test_reset_clears_error_counter(error_reporter: ErrorReporter) -> None:
    """Test that reset() clears the error counter."""
    error_reporter.warn('Error 1', 'error-type-1')
    error_reporter.warn('Error 2', 'error-type-2')
    assert len(error_reporter.error_counter) == 2

    error_reporter.reset()
    assert error_reporter.error_counter == {}


def test_reset_clears_tree_counter(error_reporter: ErrorReporter) -> None:
    """Test that reset() resets the tree counter."""
    error_reporter.tree_counter = 5
    error_reporter.reset()
    assert error_reporter.tree_counter == 0


def test_reset_clears_sentence_id(error_reporter: ErrorReporter) -> None:
    """Test that reset() clears the sentence_id."""
    error_reporter.sentence_id = 'test-sentence'
    error_reporter.reset()
    assert error_reporter.sentence_id is None


def test_reset_preserves_sentence_mapid(error_reporter: ErrorReporter) -> None:
    """Test that reset() does NOT clear sentence_mapid (by design)."""
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}
    error_reporter.reset()
    # sentence_mapid is NOT reset in the current implementation
    # This test documents the current behavior
    assert error_reporter.sentence_mapid == {'sent-1': {'alt_id': 'sent-1', 'order': 1}}


def test_reset_allows_reuse(error_reporter: ErrorReporter) -> None:
    """Test that ErrorReporter can be reused after reset()."""
    error_reporter.warn('Error 1', 'error-1')
    error_reporter.reset()
    error_reporter.warn('Error 2', 'error-2')

    assert error_reporter.get_error_count() == 1
    assert error_reporter.errors[0][3].msg == 'Error 2'


def test_warn_basic(error_reporter: ErrorReporter) -> None:
    """Test warn() with minimal parameters."""
    error_reporter.warn('Test message', 'test-error')

    assert error_reporter.get_error_count() == 1
    assert error_reporter.errors[0][3].msg == 'Test message'
    assert error_reporter.errors[0][3].error_type == 'test-error'


def test_warn_with_all_parameters(error_reporter: ErrorReporter) -> None:
    """Test warn() with all parameters specified."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    error_reporter.warn(
        msg='Complete error',
        error_type='complete-error',
        testlevel=4,
        testid='comp-001',
        line_no=20,
        node_id='10',
    )

    assert error_reporter.get_error_count() == 1
    entry = error_reporter.errors[0][3]
    assert entry.msg == 'Complete error'
    assert entry.error_type == 'complete-error'
    assert entry.testlevel == 4
    assert entry.testid == 'comp-001'
    assert entry.line_no == 20
    assert entry.node_id == '10'


def test_warn_increments_error_counter(error_reporter: ErrorReporter) -> None:
    """Test that warn() increments error_counter for error types."""
    error_reporter.warn('Error 1', 'type-a')
    error_reporter.warn('Error 2', 'type-a')
    error_reporter.warn('Error 3', 'type-b')

    assert error_reporter.error_counter['type-a'] == 2
    assert error_reporter.error_counter['type-b'] == 1


def test_warn_extracts_alt_id_from_sentence_mapid(error_reporter: ErrorReporter) -> None:
    """Test that warn() extracts alt_id from sentence_mapid."""
    error_reporter.sentence_id = 'internal-id-42'
    error_reporter.sentence_mapid = {
        'internal-id-42': {'alt_id': 'external-id-99', 'order': 5},
    }

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.alt_id == 'external-id-99'


def test_warn_extracts_order_from_sentence_mapid(error_reporter: ErrorReporter) -> None:
    """Test that warn() extracts order from sentence_mapid."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {
        'sent-1': {'alt_id': 'sent-1', 'order': 7},
    }

    error_reporter.warn('Test', 'test-error')

    # order is stored as second element of the tuple
    order = error_reporter.errors[0][1]
    assert order == 7


def test_warn_with_missing_sentence_mapid(error_reporter: ErrorReporter) -> None:
    """Test warn() when sentence_id is not in sentence_mapid."""
    error_reporter.sentence_id = 'unknown-sentence'
    error_reporter.sentence_mapid = {'other-sentence': {'alt_id': 'other', 'order': 1}}

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.alt_id is None
    assert error_reporter.errors[0][1] == 0  # order defaults to 0


def test_warn_with_empty_sentence_mapid(error_reporter: ErrorReporter) -> None:
    """Test warn() when sentence_mapid is empty dict."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {}

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.alt_id is None


def test_warn_with_none_sentence_id(error_reporter: ErrorReporter) -> None:
    """Test warn() when sentence_id is None."""
    error_reporter.sentence_id = None
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.alt_id is None


def test_warn_stores_tree_counter(error_reporter: ErrorReporter) -> None:
    """Test that warn() stores current tree_counter value."""
    error_reporter.tree_counter = 3

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.tree_counter == 3


def test_warn_stores_none_tree_counter_when_zero(error_reporter: ErrorReporter) -> None:
    """Test that warn() stores None for tree_counter when it's 0."""
    error_reporter.tree_counter = 0

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.tree_counter is None


def test_warn_default_testlevel(error_reporter: ErrorReporter) -> None:
    """Test that warn() uses default testlevel of 0."""
    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.testlevel == 0


def test_warn_default_testid(error_reporter: ErrorReporter) -> None:
    """Test that warn() uses default testid of 'some-test'."""
    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.testid == 'some-test'


def test_format_errors_empty_list(error_reporter: ErrorReporter) -> None:
    """Test format_errors() with no errors."""
    result = error_reporter.format_errors()
    assert result == []


def test_format_errors_single_error(error_reporter: ErrorReporter) -> None:
    """Test format_errors() with a single error."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}
    error_reporter.warn('Test error', 'test-error', testlevel=1, testid='test-1', line_no=5)

    result = error_reporter.format_errors()

    assert len(result) == 2  # sentence header + error
    assert 'sent-1:' in result[0]
    assert 'Line 5' in result[1]
    assert 'Test error' in result[1]


def test_format_errors_multiple_errors_same_sentence(error_reporter: ErrorReporter) -> None:
    """Test format_errors() with multiple errors in same sentence."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    error_reporter.warn('Error 1', 'error-1', testlevel=1, testid='test-1', line_no=1)
    error_reporter.warn('Error 2', 'error-2', testlevel=2, testid='test-2', line_no=2)
    error_reporter.warn('Error 3', 'error-3', testlevel=1, testid='test-3', line_no=3)

    result = error_reporter.format_errors()

    assert len(result) == 4  # sentence header + 3 errors
    assert 'sent-1:' in result[0]
    assert 'Error 1' in result[1]
    assert 'Error 2' in result[2]
    assert 'Error 3' in result[3]


def test_format_errors_multiple_sentences(error_reporter: ErrorReporter) -> None:
    """Test format_errors() with errors across multiple sentences."""
    error_reporter.sentence_mapid = {
        'sent-1': {'alt_id': 'sent-1', 'order': 1},
        'sent-2': {'alt_id': 'sent-2', 'order': 2},
    }

    error_reporter.sentence_id = 'sent-1'
    error_reporter.warn('Error in sent 1', 'error-1', line_no=1)

    error_reporter.sentence_id = 'sent-2'
    error_reporter.warn('Error in sent 2', 'error-2', line_no=5)

    result = error_reporter.format_errors()

    # Should have: sent-1 header, error, blank line, sent-2 header, error
    assert len(result) == 5
    assert 'sent-1:' in result[0]
    assert 'Error in sent 1' in result[1]
    assert result[2] == ''  # blank line between sentences
    assert 'sent-2:' in result[3]
    assert 'Error in sent 2' in result[4]


def test_format_errors_sorts_by_sentence_order(error_reporter: ErrorReporter) -> None:
    """Test that format_errors() sorts by sentence order."""
    error_reporter.sentence_mapid = {
        'sent-a': {'alt_id': 'sent-a', 'order': 3},
        'sent-b': {'alt_id': 'sent-b', 'order': 1},
        'sent-c': {'alt_id': 'sent-c', 'order': 2},
    }

    # Add errors in non-sequential order
    error_reporter.sentence_id = 'sent-a'
    error_reporter.warn('Error A', 'error-a', line_no=1)

    error_reporter.sentence_id = 'sent-b'
    error_reporter.warn('Error B', 'error-b', line_no=1)

    error_reporter.sentence_id = 'sent-c'
    error_reporter.warn('Error C', 'error-c', line_no=1)

    result = error_reporter.format_errors()

    # Should be sorted by order: sent-b (1), sent-c (2), sent-a (3)
    sentence_headers = [line for line in result if line.endswith(':')]
    assert sentence_headers[0] == 'sent-b:'
    assert sentence_headers[1] == 'sent-c:'
    assert sentence_headers[2] == 'sent-a:'


def test_format_errors_sorts_by_line_no_within_sentence(error_reporter: ErrorReporter) -> None:
    """Test that format_errors() sorts by line_no within a sentence."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    # Add errors with non-sequential line numbers
    error_reporter.warn('Error at line 10', 'error-1', line_no=10)
    error_reporter.warn('Error at line 2', 'error-2', line_no=2)
    error_reporter.warn('Error at line 5', 'error-3', line_no=5)

    result = error_reporter.format_errors()

    # Should be sorted by line_no: 2, 5, 10
    assert 'Line 2' in result[1]
    assert 'Line 5' in result[2]
    assert 'Line 10' in result[3]


def test_format_errors_handles_none_line_no(error_reporter: ErrorReporter) -> None:
    """Test format_errors() with None line_no values."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    error_reporter.warn('Error with no line', 'error-1', line_no=None)
    error_reporter.warn('Error with line', 'error-2', line_no=5)

    result = error_reporter.format_errors()

    # Errors with None line_no should sort first (treated as 0)
    assert len(result) == 3
    assert 'Error with no line' in result[1]
    assert 'Error with line' in result[2]


def test_format_errors_groups_by_sentence_id(error_reporter: ErrorReporter) -> None:
    """Test that format_errors() groups errors by sentence_id."""
    error_reporter.sentence_mapid = {
        'sent-1': {'alt_id': 'sent-1', 'order': 1},
    }

    error_reporter.sentence_id = 'sent-1'
    error_reporter.warn('Error 1', 'error-1', line_no=1)
    error_reporter.warn('Error 2', 'error-2', line_no=2)

    result = error_reporter.format_errors()

    # Should have one sentence header followed by both errors
    sentence_headers = [line for line in result if line.endswith(':')]
    assert len(sentence_headers) == 1
    assert sentence_headers[0] == 'sent-1:'


def test_format_errors_blank_line_between_sentences(error_reporter: ErrorReporter) -> None:
    """Test that format_errors() adds blank line between sentence groups."""
    error_reporter.sentence_mapid = {
        'sent-1': {'alt_id': 'sent-1', 'order': 1},
        'sent-2': {'alt_id': 'sent-2', 'order': 2},
    }

    error_reporter.sentence_id = 'sent-1'
    error_reporter.warn('Error 1', 'error-1')

    error_reporter.sentence_id = 'sent-2'
    error_reporter.warn('Error 2', 'error-2')

    result = error_reporter.format_errors()

    # Find blank line between sentence groups
    blank_lines = [i for i, line in enumerate(result) if line == '']
    assert len(blank_lines) > 0


def test_get_error_count_empty(error_reporter: ErrorReporter) -> None:
    """Test get_error_count() with no errors."""
    assert error_reporter.get_error_count() == 0


def test_get_error_count_single_error(error_reporter: ErrorReporter) -> None:
    """Test get_error_count() with one error."""
    error_reporter.warn('Test', 'test-error')
    assert error_reporter.get_error_count() == 1


def test_get_error_count_multiple_errors(error_reporter: ErrorReporter) -> None:
    """Test get_error_count() with multiple errors."""
    error_reporter.warn('Error 1', 'error-1')
    error_reporter.warn('Error 2', 'error-2')
    error_reporter.warn('Error 3', 'error-3')

    assert error_reporter.get_error_count() == 3


def test_get_error_count_after_reset(error_reporter: ErrorReporter) -> None:
    """Test get_error_count() after reset()."""
    error_reporter.warn('Error 1', 'error-1')
    error_reporter.warn('Error 2', 'error-2')
    error_reporter.reset()

    assert error_reporter.get_error_count() == 0


def test_populated_error_reporter_has_errors(populated_error_reporter: ErrorReporter) -> None:
    """Test that populated_error_reporter fixture has pre-loaded errors."""
    assert populated_error_reporter.get_error_count() > 0


def test_populated_error_reporter_format(populated_error_reporter: ErrorReporter) -> None:
    """Test formatting of populated_error_reporter fixture."""
    result = populated_error_reporter.format_errors()

    assert len(result) > 0
    assert any('test-sent-1:' in line for line in result)
    assert any('test-sent-2:' in line for line in result)


def test_populated_error_reporter_has_sentence_mapid(populated_error_reporter: ErrorReporter) -> None:
    """Test that populated_error_reporter has sentence_mapid configured."""
    assert len(populated_error_reporter.sentence_mapid) > 0
    assert 'test-sent-1' in populated_error_reporter.sentence_mapid


def test_warn_with_very_long_message(error_reporter: ErrorReporter) -> None:
    """Test warn() with very long error message."""
    long_message = 'x' * 1000
    error_reporter.warn(long_message, 'test-error')

    assert error_reporter.get_error_count() == 1
    assert error_reporter.errors[0][3].msg == long_message


def test_warn_with_special_characters_in_message(error_reporter: ErrorReporter) -> None:
    """Test warn() with special characters in error message."""
    message = 'Error with \'quotes\', "double quotes", and\nnewlines'
    error_reporter.warn(message, 'test-error')

    assert error_reporter.get_error_count() == 1
    assert error_reporter.errors[0][3].msg == message


def test_warn_with_unicode_in_message(error_reporter: ErrorReporter) -> None:
    """Test warn() with Unicode characters in error message."""
    message = 'Error with émojis: 🔥 and Greek: λόγος'
    error_reporter.warn(message, 'test-error')

    assert error_reporter.get_error_count() == 1
    assert error_reporter.errors[0][3].msg == message


def test_format_errors_with_duplicate_line_numbers(error_reporter: ErrorReporter) -> None:
    """Test format_errors() when multiple errors have same line_no."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}

    error_reporter.warn('Error A', 'error-a', line_no=5)
    error_reporter.warn('Error B', 'error-b', line_no=5)
    error_reporter.warn('Error C', 'error-c', line_no=5)

    result = error_reporter.format_errors()

    # All three errors should be present
    assert len(result) == 4  # header + 3 errors
    error_messages = [line for line in result if 'Error' in line and not line.endswith(':')]
    assert len(error_messages) == 3


def test_error_counter_multiple_types(error_reporter: ErrorReporter) -> None:
    """Test error_counter tracks multiple error types correctly."""
    error_reporter.warn('Error 1', 'type-a')
    error_reporter.warn('Error 2', 'type-b')
    error_reporter.warn('Error 3', 'type-a')
    error_reporter.warn('Error 4', 'type-c')
    error_reporter.warn('Error 5', 'type-a')

    assert error_reporter.error_counter['type-a'] == 3
    assert error_reporter.error_counter['type-b'] == 1
    assert error_reporter.error_counter['type-c'] == 1


def test_sentence_mapid_with_missing_order_key(error_reporter: ErrorReporter) -> None:
    """Test warn() when sentence_mapid entry is missing 'order' key."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {
        'sent-1': {'alt_id': 'sent-1'},  # Missing 'order' key
    }

    error_reporter.warn('Test', 'test-error')

    # Should default to 0 when order key is missing
    order = error_reporter.errors[0][1]
    assert order == 0


def test_sentence_mapid_with_missing_alt_id_key(error_reporter: ErrorReporter) -> None:
    """Test warn() when sentence_mapid entry is missing 'alt_id' key."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {
        'sent-1': {'order': 5},  # Missing 'alt_id' key
    }

    error_reporter.warn('Test', 'test-error')

    entry = error_reporter.errors[0][3]
    assert entry.alt_id is None


@pytest.mark.parametrize('testlevel', [0, 1, 2, 3, 4, 5])
def test_warn_with_different_testlevels(error_reporter: ErrorReporter, testlevel: int) -> None:
    """Test warn() with different testlevel values."""
    error_reporter.warn('Test', 'test-error', testlevel=testlevel)

    entry = error_reporter.errors[0][3]
    assert entry.testlevel == testlevel


@pytest.mark.parametrize('node_id', ['1', '5', '10', '1.1', '1-2', None])
def test_warn_with_different_node_ids(error_reporter: ErrorReporter, node_id: str | None) -> None:
    """Test warn() with different node_id formats."""
    error_reporter.warn('Test', 'test-error', node_id=node_id)

    entry = error_reporter.errors[0][3]
    assert entry.node_id == node_id


def test_format_errors_preserves_error_metadata(error_reporter: ErrorReporter) -> None:
    """Test that format_errors() doesn't lose error metadata."""
    error_reporter.sentence_id = 'sent-1'
    error_reporter.sentence_mapid = {'sent-1': {'alt_id': 'sent-1', 'order': 1}}
    error_reporter.warn(
        'Test error',
        'test-error',
        testlevel=3,
        testid='test-123',
        line_no=10,
        node_id='5',
    )

    result = error_reporter.format_errors()

    # Check that formatted output contains all metadata
    error_line = result[1]  # First line after header
    assert 'L3' in error_line
    assert 'test-error' in error_line
    assert 'test-123' in error_line
    assert 'Line 10' in error_line
    assert 'Test error' in error_line
