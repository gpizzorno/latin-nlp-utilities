# Matching

This guide covers pattern matching for finding linguistic structures in CoNLL-U annotated corpora.

## Overview

The matching module provides a pattern language for searching CoNLL-U data. You can find:

- Tokens matching specific POS tags, lemmas, or morphological features
- Sequential patterns of tokens (e.g., DET + ADJ + NOUN)
- Complex linguistic constructions with quantifiers and negation
- Matches based on substring patterns (contains, starts with, ends with)

## Quick Start

Find all nouns followed by a verb in a corpus:

```python
import conllu
from conllu_tools.matching import build_pattern, find_in_corpus

# Load corpus
with open('corpus.conllu', encoding='utf-8') as f:
    corpus = conllu.parse(f.read())

# Build and search for pattern
pattern = build_pattern('NOUN+VERB', name='noun-verb')
matches = find_in_corpus(corpus, [pattern])

# Print results
for match in matches:
    print(f"[{match.sentence_id}] {match.substring}")
    print(f"  Lemmata: {match.lemmata}")
```

## Basic Usage

### Building Patterns

The `build_pattern()` function parses a pattern string into a `SentencePattern` object:

```python
from conllu_tools.matching import build_pattern

# Simple UPOS pattern
noun_pattern = build_pattern('NOUN')

# Pattern with conditions
ablative_noun = build_pattern('NOUN:feats=(Case=Abl)')

# Multi-token sequence
det_noun = build_pattern('DET+NOUN')

# Named pattern for identification
pattern = build_pattern('NOUN+VERB', name='subject-verb')
```

### Searching a Corpus

Use `find_in_corpus()` to search for patterns across all sentences:

```python
from conllu_tools.matching import build_pattern, find_in_corpus

# Create multiple patterns
patterns = [
    build_pattern('NOUN+VERB', name='noun-verb'),
    build_pattern('DET+NOUN', name='det-noun'),
]

# Search corpus
matches = find_in_corpus(corpus, patterns)

# Group results by pattern
for match in matches:
    print(f"Pattern '{match.pattern_name}': {match.substring}")
```

### Working with Match Results

Each `MatchResult` provides access to matched content:

```python
for match in matches:
    # Pattern identification
    print(f"Pattern: {match.pattern_name}")
    print(f"Sentence: {match.sentence_id}")
    
    # Matched text
    print(f"Text: {match.substring}")      # "una scala"
    print(f"Forms: {match.forms}")          # ['una', 'scala']
    print(f"Lemmata: {match.lemmata}")      # ['unus', 'scalae']
    
    # Access individual tokens
    for token in match.tokens:
        print(f"  {token['form']} ({token['upos']})")
```

## Pattern Syntax

### Token Patterns

The basic structure of a token pattern is:

```regexp
UPOS:attribute=value
```

The UPOS tag comes first, followed by optional attribute conditions separated by colons.

#### UPOS Matching

Match tokens by their universal part-of-speech tag:

```python
# Single UPOS
pattern = build_pattern('NOUN')

# Multiple UPOS options (OR)
pattern = build_pattern('NOUN|VERB')

# Any UPOS (wildcard)
pattern = build_pattern('*')
```

Valid UPOS tags: `ADJ`, `ADP`, `ADV`, `AUX`, `CCONJ`, `DET`, `INTJ`, `NOUN`, `NUM`, `PART`, `PRON`, `PROPN`, `PUNCT`, `SCONJ`, `SYM`, `VERB`, `X`

#### Attribute Conditions

Add conditions on token attributes using UD/CoNLL-U field names:

```python
# Match by lemma
pattern = build_pattern('NOUN:lemma=rex')

# Match by form
pattern = build_pattern('VERB:form=est')

# Match by head
pattern = build_pattern('NOUN:head=0')  # Root nouns

# Match by dependency relation
pattern = build_pattern('*:deprel=nsubj')
```

Available attributes: `id`, `form`, `lemma`, `xpos`, `feats`, `head`, `deprel`, `deps`, `misc`

#### Multiple Values (OR)

Use pipes to match any of several values:

```python
# Lemma is either 'rex' or 'regina'
pattern = build_pattern('NOUN:lemma=rex|regina')

# UPOS is NOUN or PROPN
pattern = build_pattern('NOUN|PROPN')
```

#### Morphological Features

Match on the `feats` column using parentheses with comma-separated conditions:

```python
# Singular ablative noun
pattern = build_pattern('NOUN:feats=(Number=Sing,Case=Abl)')

# Ablative or dative noun
pattern = build_pattern('NOUN:feats=(Case=Abl|Dat)')

# Multiple feature conditions
pattern = build_pattern('VERB:feats=(Mood=Sub,Tense=Pres)')
```

#### Match Type Modifiers

Control how string values are matched using `<` and `>`:

```python
# Exact match (default)
pattern = build_pattern('NOUN:form=a')

# Contains
pattern = build_pattern('NOUN:form=<ae>')   # Form contains 'ae'

# Starts with
pattern = build_pattern('NOUN:form=<ab')    # Form starts with 'ab'

# Ends with  
pattern = build_pattern('NOUN:form=um>')    # Form ends with 'um'
```

#### Negation

Use `!` to negate conditions:

```python
# Not a noun
pattern = build_pattern('!NOUN')

# Noun not in singular
pattern = build_pattern('NOUN:feats=(Number=!Sing)')

# Form does not contain 'ae'
pattern = build_pattern('*:form=!<ae>')
```

#### Quantifiers

Use regex-style quantifiers to match multiple consecutive tokens:

```python
# Match exactly 2 adjectives
pattern = build_pattern('ADJ{2}')

# Match 0-3 tokens of any type (optional sequence)
pattern = build_pattern('*{0,3}')

# Match 1-5 adjectives
pattern = build_pattern('ADJ{1,5}')
```

### Sentence Patterns

Combine token patterns with `+` to match sequences:

```python
# Determiner followed by noun
pattern = build_pattern('DET+NOUN')

# Preposition phrase: ADP + accusative noun
pattern = build_pattern('ADP+NOUN:feats=(Case=Acc)')

# Subject-verb-object with gaps
pattern = build_pattern('*:deprel=nsubj+*{0,10}+VERB:deprel=root+*{0,10}+*:deprel=obj')

# Noun phrase with optional adjectives
pattern = build_pattern('DET+ADJ{0,2}+NOUN')
```

## Advanced Usage

### Manual Pattern Construction

For complex patterns, construct objects directly:

```python
from conllu_tools.matching import Condition, TokenPattern, SentencePattern

# Create conditions
case_nom = Condition(key='Case', values=['Nom'])
case_acc = Condition(key='Case', values=['Acc'])
feats_cond = Condition(key='feats', values=[case_nom, case_acc], match_any=True)
upos_cond = Condition(key='upos', values=['NOUN'])

# Create token pattern
noun_pattern = TokenPattern(conditions=[upos_cond, feats_cond])

# Create sentence pattern
pattern = SentencePattern(pattern=[noun_pattern], name='nom-or-acc-noun')
```

### Condition Types

The `Condition` class supports various match types:

```python
from conllu_tools.matching import Condition

# Exact match (default)
cond = Condition(key='lemma', values=['rex'])

# Contains
cond = Condition(key='form', values=['ae'], match_type='contains')

# Starts with
cond = Condition(key='form', values=['ab'], match_type='startswith')

# Ends with
cond = Condition(key='form', values=['um'], match_type='endswith')

# Negation
cond = Condition(key='upos', values=['NOUN'], negate=True)

# Match any of multiple values
cond = Condition(key='lemma', values=['rex', 'regina'], match_any=True)
```

### Nested Conditions

For dictionary-type attributes like `feats`, use nested conditions:

```python
from conllu_tools.matching import Condition

# Nested conditions for features
case_cond = Condition(key='Case', values=['Abl'])
number_cond = Condition(key='Number', values=['Sing'])

# All conditions must match
feats_all = Condition(key='feats', values=[case_cond, number_cond], match_any=False)

# Any condition matches
feats_any = Condition(key='feats', values=[case_cond, number_cond], match_any=True)
```

### Pattern Explanation

Get a human-readable explanation of a pattern:

```python
pattern = build_pattern('NOUN:feats=(Case=Abl,Number=Sing)+VERB')
print(pattern.explain())
# Output:
# This pattern matches a sequence of the following token patterns:
#   Token Pattern 1: Matches a token when 'upos' equals NOUN and ...
#   Token Pattern 2: Matches a token when 'upos' equals VERB
```

### Matching Individual Sentences

Apply patterns to single sentences:

```python
import conllu
from conllu_tools.matching import build_pattern

conllu_text = """# sent_id = example-1
# text = Rex magnam urbem videt.
1	Rex	rex	NOUN	_	Case=Nom|Gender=Masc|Number=Sing	4	nsubj	_	_
2	magnam	magnus	ADJ	_	Case=Acc|Gender=Fem|Number=Sing	3	amod	_	_
3	urbem	urbs	NOUN	_	Case=Acc|Gender=Fem|Number=Sing	4	obj	_	_
4	videt	video	VERB	_	Mood=Ind|Number=Sing|Person=3|Tense=Pres	0	root	_	_
5	.	.	PUNCT	_	_	4	punct	_	_

"""
sentence = conllu.parse(conllu_text)[0]

pattern = build_pattern('ADJ+NOUN', name='adj-noun')
matches = pattern.match(sentence)

for match in matches:
    print(f"Found: {match.substring}")  # "magnam urbem"
```

## Common Issues

### Pattern Not Matching

**Problem**: Pattern doesn't find expected matches.

**Solutions**:

1. Check UPOS tags match your corpus annotation:
```python
# Debug: print actual UPOS values
for token in sentence:
    print(f"{token['form']}: {token['upos']}")
```

2. Verify feature names and values:
```python
# Debug: print actual features
for token in sentence:
    print(f"{token['form']}: {token['feats']}")
```

3. Test simpler patterns first:
```python
# Start simple
pattern = build_pattern('NOUN')  # Does this match?
# Then add conditions
pattern = build_pattern('NOUN:feats=(Case=Abl)')
```

### Empty Feature Handling

**Problem**: Tokens with empty features (`_`) don't match feature conditions.

**Solution**: Feature conditions only match when features exist:

```python
# This won't match tokens with feats=_
pattern = build_pattern('NOUN:feats=(Case=Nom)')

# To also find nouns regardless of features, use alternation or separate patterns
nouns = build_pattern('NOUN', name='all-nouns')
nom_nouns = build_pattern('NOUN:feats=(Case=Nom)', name='nominative-nouns')
```

### Quantifier Behavior

**Problem**: Quantified patterns match more or fewer tokens than expected.

**Solution**: Quantifiers apply to the preceding token pattern only:

```python
# Matches: DET + (0-2 ADJ) + NOUN
pattern = build_pattern('DET+ADJ{0,2}+NOUN')

# NOT: (DET + ADJ){0,2} + NOUN
# Each token pattern is separate
```

## See Also

- [Loading](loading.md) - Loading CoNLL-U files
- [Validation](validation.md) - Validating CoNLL-U files
- {ref}`api_reference/matching` - Detailed matching API
