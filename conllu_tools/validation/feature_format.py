"""Feature format and value validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import regex as re

from conllu_tools.constants import FEATURE_NAME_MATCHER, FEATURE_VALUE_MATCHER

from .helpers import get_alt_language
from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class FeatureValidationMixin(BaseValidationMixin):
    """Mixin providing feature format and value validation methods."""

    def _validate_feature_format(self, sentence: conllu.TokenList) -> None:
        """Validate feature format.

        Arguments:
            sentence: Parsed sentence

        """
        # Regex patterns for feature format validation
        feat_name_re = re.compile(FEATURE_NAME_MATCHER)
        feat_value_re = re.compile(FEATURE_VALUE_MATCHER)

        for token in sentence:
            # Skip multiword tokens (MWT range markers)
            if isinstance(token['id'], tuple):
                continue

            # Get FEATS
            feats_str = token.get('feats')
            if not feats_str or feats_str == '_':
                continue

            # conllu library parses FEATS into OrderedDict
            feats = token['feats']
            if not feats:
                continue

            # Check for repeated features
            self._check_repeated_features(token, feats, feats_str)

            # Check feature names and values format
            self._validate_feature_names_and_values(token, feats, feat_name_re, feat_value_re)

            # Check feature sorting
            self._check_feature_sorting(token, feats)

            # Check value sorting within each feature
            self._check_value_sorting(token, feats)

    def _check_repeated_features(
        self,
        token: conllu.Token,
        feats: dict[str, Any],
        feats_str: str,
    ) -> None:
        """Check for repeated feature names.

        Arguments:
            token: Token being validated
            feats: Parsed features dict
            feats_str: Original features string

        """
        feat_names = list(feats.keys())
        if len(feat_names) != len(set(feat_names)):
            self.reporter.warn(
                f"Repeated features are disallowed: '{feats_str}'",
                'Morpho',
                testlevel=2,
                testid='repeated-feature',
                node_id=str(token['id']),
            )

    def _validate_feature_names_and_values(
        self,
        token: conllu.Token,
        feats: dict[str, Any],
        feat_name_re: re.Pattern,
        feat_value_re: re.Pattern,
    ) -> None:
        """Validate feature name and value formats.

        Arguments:
            token: Token being validated
            feats: Parsed features dict
            feat_name_re: Compiled regex for feature names
            feat_value_re: Compiled regex for feature values

        """
        for feat_name, feat_values in feats.items():
            # Validate feature name format
            if not feat_name_re.match(feat_name):
                self.reporter.warn(
                    f"Invalid feature name: '{feat_name}'. "
                    'Should be of the form Feature or Feature[layer] and only contain [A-Za-z0-9].',
                    'Morpho',
                    testlevel=2,
                    testid='invalid-feature',
                    node_id=str(token['id']),
                )
                continue

            # Get values as list
            values = self._get_feature_values_as_list(feat_values)

            # Check for repeated values
            if len(values) != len(set(values)):
                self.reporter.warn(
                    f"Repeated feature values are disallowed in '{feat_name}={','.join(values)}'",
                    'Morpho',
                    testlevel=2,
                    testid='repeated-feature-value',
                    node_id=str(token['id']),
                )

            # Validate each value format
            for value in values:
                if not feat_value_re.match(value):
                    self.reporter.warn(
                        f"Spurious value '{value}' in '{feat_name}={value}'. "
                        'Must start with [A-Z0-9] and only contain [A-Za-z0-9].',
                        'Morpho',
                        testlevel=2,
                        testid='invalid-feature-value',
                        node_id=str(token['id']),
                    )

    def _get_feature_values_as_list(self, feat_values: Any) -> list[str]:
        """Convert feature values to list format.

        Arguments:
            feat_values: Feature values (can be str, set, or list)

        Returns:
            List of feature values

        """
        if isinstance(feat_values, set):
            return sorted(feat_values)  # For consistent ordering
        if isinstance(feat_values, list):
            return feat_values
        return [feat_values]

    def _check_feature_sorting(self, token: conllu.Token, feats: dict[str, Any]) -> None:
        """Check that features are sorted alphabetically.

        Arguments:
            token: Token being validated
            feats: Parsed features dict

        """
        feat_names = list(feats.keys())
        feat_names_lower = [f.lower() for f in feat_names]
        if feat_names_lower != sorted(feat_names_lower):
            # Reconstruct feature string for error message
            feat_str = '|'.join(f'{k}={",".join(v) if isinstance(v, (list, set)) else v}' for k, v in feats.items())
            self.reporter.warn(
                f"Morphological features must be sorted: '{feat_str}'",
                'Morpho',
                testlevel=2,
                testid='unsorted-features',
                node_id=str(token['id']),
            )

    def _check_value_sorting(self, token: conllu.Token, feats: dict[str, Any]) -> None:
        """Check that values within each feature are sorted.

        Arguments:
            token: Token being validated
            feats: Parsed features dict

        """
        for feat_name, feat_values in feats.items():
            if isinstance(feat_values, (set, list)) and len(feat_values) > 1:
                values = list(feat_values)
                values_lower = [v.lower() for v in values]
                if values_lower != sorted(values_lower):
                    self.reporter.warn(
                        f"If a feature has multiple values, these must be sorted: '{feat_name}={','.join(values)}'",
                        'Morpho',
                        testlevel=2,
                        testid='unsorted-feature-values',
                        node_id=str(token['id']),
                    )

    def _validate_feature_upos_compatibility(
        self,
        token: conllu.Token,
        feat_name: str,
        value: str,
        feature_record: dict[str, Any],
        upos: str,
    ) -> None:
        """Validate feature-value-UPOS compatibility (Level 4).

        Arguments:
            token: Token to validate
            feat_name: Feature name
            value: Feature value
            feature_record: Feature record from feats.json
            upos: UPOS tag

        """
        byupos = feature_record.get('byupos', {})

        # Check if feature is allowed with this UPOS
        if upos not in byupos:
            self.reporter.warn(
                f'Feature {feat_name} is not permitted with UPOS {upos} in language [{self.lang}]',
                'Morpho',
                testlevel=4,
                testid='feature-upos-not-permitted',
                node_id=str(token['id']),
            )
            return

        # Check if this specific value is allowed with this UPOS
        upos_values = byupos[upos]
        if value not in upos_values or upos_values[value] == 0:
            self.reporter.warn(
                f'Value {value} of feature {feat_name} is not permitted with UPOS {upos} in language [{self.lang}]',
                'Morpho',
                testlevel=4,
                testid='feature-value-upos-not-permitted',
                node_id=str(token['id']),
            )

    def _extract_base_feature_name(self, feat_name: str) -> str:
        """Extract base feature name without layered brackets.

        Arguments:
            feat_name: Feature name (e.g., "Person[psor]" or "Case")

        Returns:
            Base feature name (e.g., "Person" or "Case")

        """
        # Remove layered brackets: Person[psor] -> Person
        bracket_pos = feat_name.find('[')
        if bracket_pos > 0:
            return feat_name[:bracket_pos]
        return feat_name

    def _validate_feature_values(self, token: conllu.Token) -> None:
        """Validate feature values against language-specific data (Level 4).

        This method is used by multiple mixins to validate the feature values of a token.

        Arguments:
            token: Token to validate

        """
        if not token['feats']:
            return

        # Check for alternative language
        lang = get_alt_language(token) or self.lang

        lang_features = self.featdata.get(lang, {})
        if not lang_features:
            return

        upos = token['upos']

        for feat_name, feat_values in token['feats'].items():
            # Extract base feature name (remove layered brackets if present)
            base_feat_name = self._extract_base_feature_name(feat_name)

            # Check if feature is documented for this language
            if base_feat_name not in lang_features:
                self.reporter.warn(
                    f'Feature {feat_name} is not documented for language [{lang}]',
                    'Morpho',
                    testlevel=4,
                    testid='feature-unknown',
                    node_id=str(token['id']),
                )
                continue

            feature_record = lang_features[base_feat_name]

            # Check if feature is permitted
            if feature_record.get('permitted', 0) == 0:
                self.reporter.warn(
                    f'Feature {feat_name} is not permitted in language [{lang}]',
                    'Morpho',
                    testlevel=4,
                    testid='feature-not-permitted',
                    node_id=str(token['id']),
                )
                continue

            # Get allowed values for this feature
            allowed_values = (
                feature_record.get('uvalues', [])
                + feature_record.get('lvalues', [])
                + feature_record.get('unused_uvalues', [])
                + feature_record.get('unused_lvalues', [])
            )

            # Validate each value
            values = list(feat_values) if isinstance(feat_values, (set, list)) else [feat_values]

            for value in values:
                # Check if value is documented
                if value not in allowed_values:
                    self.reporter.warn(
                        f'Value {value} is not documented for feature {feat_name} in language [{lang}]',
                        'Morpho',
                        testlevel=4,
                        testid='feature-value-unknown',
                        node_id=str(token['id']),
                    )
                    continue

                # Check UPOS compatibility
                self._validate_feature_upos_compatibility(
                    token,
                    feat_name,
                    value,
                    feature_record,
                    upos,
                )
