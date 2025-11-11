"""Main validator class using conllu library for CoNLL-U validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import conllu
import regex as re

from nlp_utilities.constants import DEFAULT_WHITESPACE_EXCEPTIONS, UNIVERSAL_DEPRELS, UPOS_TAGS
from nlp_utilities.loaders import load_language_data, load_whitespace_exceptions

from .character_constraints import CharacterValidationMixin
from .content_validators import ContentValidationMixin
from .enhanced_deps import EnhancedDepsValidationMixin
from .error_reporter import ErrorReporter
from .feature_format import FeatureValidationMixin
from .format import FormatValidationMixin
from .language_content import LanguageContentValidationMixin
from .language_format import LanguageFormatValidationMixin
from .metadata import MetadataValidationMixin
from .misc_column import MiscValidationMixin
from .structure import StructureValidationMixin
from .unicode import UnicodeValidationMixin


class ConlluValidator(
    FormatValidationMixin,
    UnicodeValidationMixin,
    EnhancedDepsValidationMixin,
    MetadataValidationMixin,
    MiscValidationMixin,
    StructureValidationMixin,
    ContentValidationMixin,
    CharacterValidationMixin,
    LanguageFormatValidationMixin,
    LanguageContentValidationMixin,
    FeatureValidationMixin,
):
    """Validator for CoNLL-U files with configurable validation levels."""

    def __init__(  # noqa: PLR0913
        self,
        lang: str = 'ud',
        level: int = 2,
        add_features: str | None = None,
        add_deprels: str | None = None,
        add_auxiliaries: str | None = None,
        add_whitespace_exceptions: str | None = None,
        load_dalme: bool = False,  # noqa: FBT001
        sentence_concordance: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the validator.

        Args:
            lang: Language code for language-specific validation.
            level: Validation level (1-5).
            add_features: Path to additional features JSON file.
            add_deprels: Path to additional deprels JSON file.
            add_auxiliaries: Path to additional auxiliaries JSON file.
            add_whitespace_exceptions: Path to additional whitespace exceptions file.
            load_dalme: Whether to load DALME data.
            sentence_concordance: Mapping of sentence IDs to additional metadata.

        """
        self.lang = lang
        self.level = level
        self.reporter = ErrorReporter()

        if sentence_concordance:
            self.reporter.sentence_mapid = sentence_concordance

        # Initialize tag sets
        self.upos_tags = set(UPOS_TAGS)
        self.featdata: dict[str, Any] = {}
        self.depreldata: dict[str, Any] = {}
        self.auxdata: dict[str, Any] = {}
        self.tokens_w_space: list[re.Pattern] = DEFAULT_WHITESPACE_EXCEPTIONS
        self.universal_deprels: set[str] = set()

        # Track first occurrence of empty nodes for enhanced dependency validation
        self.line_of_first_empty_node: int | None = None

        # Track SpaceAfter=No across sentence boundaries for metadata validation
        self.spaceafterno_in_effect = False

        # Load universal dependency relations (level 2+)
        if level >= 2:  # noqa: PLR2004
            self.universal_deprels = UNIVERSAL_DEPRELS

        # Load language-specific data if level >= 4
        if level >= 4 and lang != 'ud':  # noqa: PLR2004
            self.featdata = load_language_data(
                'feats',
                language=None,
                additional_path=add_features,
                load_dalme=load_dalme,
            )['features']
            self.depreldata = load_language_data(
                'deprels',
                language=None,
                additional_path=add_deprels,
                load_dalme=load_dalme,
            )['deprels']
            self.auxdata = load_language_data(
                'auxiliaries',
                language=None,
                additional_path=add_auxiliaries,
                load_dalme=load_dalme,
            )['auxiliaries']
            self.tokens_w_space = load_whitespace_exceptions(add_whitespace_exceptions)

    def validate_file(self, filepath: str | Path) -> list[str]:
        """Validate a CoNLL-U file.

        Args:
            filepath: Path to the CoNLL-U file

        Returns:
            List of formatted error messages

        """
        filepath = Path(filepath)
        self.reporter.reset()

        with filepath.open('r', encoding='utf-8') as f:
            content = f.read()

        return self.validate_string(content)

    def validate_string(self, content: str) -> list[str]:
        """Validate CoNLL-U content from a string.

        Args:
            content: CoNLL-U content as string

        Returns:
            List of formatted error messages

        """
        self.reporter.reset()

        # Parse using conllu library
        try:
            sentences = conllu.parse(content)
        except conllu.exceptions.ParseException as e:
            self.reporter.warn(
                f'Failed to parse CoNLL-U file: {e!s}',
                'Format',
                testlevel=1,
                testid='parse-error',
            )
            return self.reporter.format_errors()

        # Validate each sentence
        for i, sentence in enumerate(sentences, 1):
            self.reporter.tree_counter = i
            self.reporter.sentence_id = sentence.metadata.get('sent_id')
            self._validate_sentence(sentence)

        return self.reporter.format_errors()

    def _validate_sentence(self, sentence: conllu.TokenList) -> None:
        """Validate a single sentence.

        Args:
            sentence: Parsed sentence from conllu library

        """
        self._validate_unicode(sentence)  # Level 1: Unicode
        self._validate_format(sentence)  # Level 1+2: Format
        self._validate_structure(sentence)  # Level 1+2: Structural

        if self.level < 2:  # noqa: PLR2004
            return

        self._validate_metadata(sentence)  # Level 2: Metadata
        self._validate_misc(sentence)  # Level 2: MISC column
        self._validate_character_constraints(sentence)  # Level 2: Character constraints
        self._validate_enhanced_dependencies(sentence)  # Level 2-3: Enhanced dependencies

        if self.level < 3:  # noqa: PLR2004
            return

        # Level 3: left-to-right relations, single subject, orphans, goes with span,
        # fixed span, projective punctuation, functional leaves
        self._validate_content(sentence)
        self._validate_feature_format(sentence)  # Level 4: Feature format and value

        if self.level < 4:  # noqa: PLR2004
            return

        # Level 4: Language-specific format
        self._validate_language_specific_format(sentence)

        if self.level < 5:  # noqa: PLR2004
            return

        # Level 5: Language-specific content
        self._validate_language_specific_content(sentence)
