# Matching Examples

Examples for finding linguistic patterns in CoNLL-U annotated corpora.

## Linguistic Patterns

```python
from conllu_tools.matching import build_pattern

# Ablative absolute
pattern = build_pattern('NOUN|DET:feats=(Case=Abl)+*{0,1}+VERB:feats=(Case=Abl,VerbForm=Part)')

# Genitive gerundive construction
pattern = build_pattern('NOUN+VERB:feats=(VerbForm=Ger,Case=Gen)+NOUN')

# Prepositional phrases
pattern = build_pattern('ADP+NOUN:feats=(Case=Acc)')
pattern = build_pattern('ADP+NOUN:feats=(Case=Abl)')
pattern = build_pattern('*:form=de+*:feats=(Case=Abl)')

# Subjunctive verbs
pattern = build_pattern('VERB:feats=(Mood=Sub)')

# Personal pronouns
pattern = build_pattern('PRON:feats=(PronType=Prs)')
```

## Syntactic Patterns

```python
# Subject-verb-object
pattern = build_pattern('*:deprel=nsubj+*{0,100}+VERB:deprel=root+*{0,100}+*:deprel=obj')

# Noun phrases with modifiers
pattern = build_pattern('DET+ADJ{0,2}+NOUN')

# Coordination
pattern = build_pattern('NOUN+CCONJ+NOUN')
```

## Morphological Patterns

```python
from conllu_tools.matching import build_pattern

# Singular nouns in the ablative or dative with -i or -e endings
pattern = build_pattern('NOUN:feats=(Number=Sing,Case=Abl|Dat):form=i|e>')

# Words containing diphthongs
pattern = build_pattern('*:form=<ae|oe>')
```

## See Also

- [Matching User Guide](../user_guide/matching.md) for detailed documentation
