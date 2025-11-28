"""UPOS-DEPREL compatibility validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import regex as re

from conllu_tools.constants import (
    ADVMOD_UPOS,
    CASE_UPOS,
    CC_UPOS,
    COP_UPOS,
    DET_UPOS,
    EXPL_UPOS,
    MARK_UPOS,
    NUMMOD_UPOS,
    PUNCT_DEPREL,
)

from .validation_mixin import BaseValidationMixin

if TYPE_CHECKING:
    import conllu


class UposDeprelValidationMixin(BaseValidationMixin):
    """Mixin providing UPOS-DEPREL compatibility validation methods."""

    def _validate_upos_deprel_compatibility(self, token: conllu.Token) -> None:
        """Validate that UPOS and DEPREL are compatible.

        Arguments:
            token: Token to validate

        """
        deprel = token['deprel'].split(':')[0]
        upos = token['upos']
        token_id = token['id']

        # Get children relations for some validations
        children_rels = self._get_children_relations(token)

        # Validate deprel-based constraints
        self._validate_deprel_upos(deprel, upos, token_id, children_rels)

        # Validate upos-based constraints
        self._validate_upos_deprel(upos, deprel, token_id)

    def _validate_deprel_upos(
        self,
        deprel: str,
        upos: str,
        token_id: Any,
        children_rels: set[str],
    ) -> None:
        """Validate deprel-to-upos constraints.

        Arguments:
            deprel: Dependency relation (base, without subtypes)
            upos: Universal part-of-speech tag
            token_id: Token ID for error reporting
            children_rels: Set of children dependency relations

        """
        # Validate each deprel-upos combination
        self._check_det_upos(deprel, upos, token_id)
        self._check_aux_upos(deprel, upos, token_id)
        self._check_punct_upos(deprel, upos, token_id)
        self._check_nummod_upos(deprel, upos, token_id)
        self._check_advmod_upos(deprel, upos, token_id, children_rels)
        self._check_expl_upos(deprel, upos, token_id)
        self._check_cop_upos(deprel, upos, token_id)
        self._check_case_upos(deprel, upos, token_id, children_rels)
        self._check_mark_upos(deprel, upos, token_id, children_rels)
        self._check_cc_upos(deprel, upos, token_id, children_rels)

    def _check_det_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check det deprel compatibility."""
        if deprel == 'det' and not re.match(DET_UPOS, upos):
            self.reporter.warn(
                f"'det' should be 'DET' or 'PRON' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-det',
                node_id=str(token_id),
            )

    def _check_aux_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check aux deprel compatibility."""
        if deprel == 'aux' and upos != 'AUX':
            self.reporter.warn(
                f"'aux' should be 'AUX' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-aux',
                node_id=str(token_id),
            )

    def _check_punct_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check punct deprel compatibility."""
        if deprel == 'punct' and upos != 'PUNCT':
            self.reporter.warn(
                f"'punct' must be 'PUNCT' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-punct',
                node_id=str(token_id),
            )

    def _check_nummod_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check nummod deprel compatibility."""
        if deprel == 'nummod' and not re.match(NUMMOD_UPOS, upos):
            self.reporter.warn(
                f"'nummod' should be 'NUM' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-nummod',
                node_id=str(token_id),
            )

    def _check_advmod_upos(
        self,
        deprel: str,
        upos: str,
        token_id: Any,
        children_rels: set[str],
    ) -> None:
        """Check advmod deprel compatibility."""
        if (
            deprel == 'advmod'
            and not re.match(ADVMOD_UPOS, upos)
            and 'fixed' not in children_rels
            and 'goeswith' not in children_rels
        ):
            self.reporter.warn(
                f"'advmod' should be 'ADV' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-advmod',
                node_id=str(token_id),
            )

    def _check_expl_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check expl deprel compatibility."""
        if deprel == 'expl' and not re.match(EXPL_UPOS, upos):
            self.reporter.warn(
                f"'expl' should normally be 'PRON' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-expl',
                node_id=str(token_id),
            )

    def _check_cop_upos(self, deprel: str, upos: str, token_id: Any) -> None:
        """Check cop deprel compatibility."""
        if deprel == 'cop' and not re.match(COP_UPOS, upos):
            self.reporter.warn(
                f"'cop' should be 'AUX' or 'PRON'/'DET' but it is '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-cop',
                node_id=str(token_id),
            )

    def _check_case_upos(
        self,
        deprel: str,
        upos: str,
        token_id: Any,
        children_rels: set[str],
    ) -> None:
        """Check case deprel compatibility."""
        if deprel == 'case' and re.match(CASE_UPOS, upos) and 'fixed' not in children_rels:
            self.reporter.warn(
                f"'case' should not be '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-case',
                node_id=str(token_id),
            )

    def _check_mark_upos(
        self,
        deprel: str,
        upos: str,
        token_id: Any,
        children_rels: set[str],
    ) -> None:
        """Check mark deprel compatibility."""
        if deprel == 'mark' and re.match(MARK_UPOS, upos) and 'fixed' not in children_rels:
            self.reporter.warn(
                f"'mark' should not be '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-mark',
                node_id=str(token_id),
            )

    def _check_cc_upos(
        self,
        deprel: str,
        upos: str,
        token_id: Any,
        children_rels: set[str],
    ) -> None:
        """Check cc deprel compatibility."""
        if deprel == 'cc' and re.match(CC_UPOS, upos) and 'fixed' not in children_rels:
            self.reporter.warn(
                f"'cc' should not be '{upos}'",
                'Syntax',
                testlevel=3,
                testid='rel-upos-cc',
                node_id=str(token_id),
            )

    def _validate_upos_deprel(self, upos: str, deprel: str, token_id: Any) -> None:
        """Validate upos-to-deprel constraints.

        Arguments:
            upos: Universal part-of-speech tag
            deprel: Dependency relation (base, without subtypes)
            token_id: Token ID for error reporting

        """
        # PUNCT must be punct or root
        if upos == 'PUNCT' and not re.match(PUNCT_DEPREL, deprel):
            self.reporter.warn(
                f"'PUNCT' must be 'punct' but it is '{deprel}'",
                'Syntax',
                testlevel=3,
                testid='upos-rel-punct',
                node_id=str(token_id),
            )

    def _get_children_relations(self, token: conllu.Token) -> set[str]:
        """Get the set of dependency relations of the token's children.

        Arguments:
            token: Token to get children relations for

        Returns:
            Set of dependency relation names (base names without subtypes)

        """
        children_rels = set()

        # Access the sentence this token belongs to
        if hasattr(self, 'current_sentence'):
            sentence = self.current_sentence
            token_id = token['id']

            for child_token in sentence:
                child_id = child_token['id']
                # Skip multiword tokens and self
                if isinstance(child_id, tuple) or child_id == token_id:
                    continue

                # Check if this child's head points to our token
                child_head = child_token.get('head')
                if child_head == token_id:
                    # Extract base deprel without subtypes
                    child_deprel = child_token.get('deprel', '').split(':')[0]
                    children_rels.add(child_deprel)

        return children_rels
