"""Factories for conllu test data generation."""

from __future__ import annotations

from typing import Any


class EnhancedDepsFactory:
    """Factory for creating enhanced dependency structures."""

    @classmethod
    def create_deps_string(cls, *head_deprel_pairs: tuple[int, str]) -> str:
        """Create DEPS string from head-deprel pairs.

        Args:
            head_deprel_pairs: Tuples of (head_id, deprel)

        Returns:
            DEPS column string (e.g., "1:nsubj|3:obj")

        """
        if not head_deprel_pairs:
            return '_'
        return '|'.join(f'{head}:{deprel}' for head, deprel in head_deprel_pairs)

    @classmethod
    def create_with_shared_heads(cls, token_count: int = 5) -> list[dict[str, Any]]:
        """Create tokens with shared heads in enhanced deps.

        Args:
            token_count: Number of tokens to create

        Returns:
            List of token dictionaries with enhanced dependencies

        """
        tokens = []
        for i in range(1, token_count + 1):
            # Each token (except root) has basic dep on previous and enhanced dep on root
            head = 0 if i == 1 else i - 1
            deprel = 'root' if i == 1 else 'dep'
            deps = '0:root' if i == 1 else f'{i - 1}:dep|0:root'  # Shared head with root

            token = {
                'id': i,
                'form': f'word{i}',
                'lemma': f'word{i}',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': head,
                'deprel': deprel,
                'deps': deps,
                'misc': '_',
            }
            tokens.append(token)
        return tokens

    @classmethod
    def create_disconnected_graph(cls) -> list[dict[str, Any]]:
        """Create enhanced dependency graph with disconnected components.

        Returns:
            List of token dictionaries with disconnected enhanced graph

        """
        return [
            {
                'id': 1,
                'form': 'word1',
                'lemma': 'word1',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': 0,
                'deprel': 'root',
                'deps': '0:root',  # Only connected to root in enhanced graph
                'misc': '_',
            },
            {
                'id': 2,
                'form': 'word2',
                'lemma': 'word2',
                'upostag': 'NOUN',
                'xpostag': '_',
                'feats': '_',
                'head': 1,
                'deprel': 'dep',
                'deps': '_',  # No enhanced deps - disconnected!
                'misc': '_',
            },
        ]
