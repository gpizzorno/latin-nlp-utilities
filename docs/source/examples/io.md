# I/O Examples

Examples for converting between CoNLL-U and brat standoff formats.

## Round-trip Conversion

For a complete workflow where you start with CoNLL-U, annotate in brat, and return to CoNLL-U:

```python
from conllu_tools.io import conllu_to_brat, brat_to_conllu, load_language_data

# Step 1: Convert to brat
conllu_to_brat(
    conllu_filename='corpus.conllu',
    output_directory='for_annotation/',
    output_root=True,
    sents_per_doc=50
)
# This creates metadata.json with all the conversion parameters

# ... Manual annotation in brat ...

# Step 2: Convert back to CoNLL-U
feature_set = load_language_data('feats', language='la')
brat_to_conllu(
    input_directory='for_annotation/',
    output_directory='annotated_output/',
    feature_set=feature_set
)
# metadata.json automatically provides ref_conllu, output_root, and sents_per_doc!
```

## Important Notes

1. The `metadata.json` file simplifies round-trip conversion by storing parameters
2. If `metadata.json` is not present, you must provide `ref_conllu` and `output_root` explicitly
3. The reference CoNLL-U file should have the same sentences in the same order
4. Only dependency structure (HEAD/DEPREL) is modified; morphology comes from reference

## See Also

- [Conversion User Guide](../user_guide/conversion.md) for detailed documentation
