import hashlib
import json
from collections import OrderedDict
from pathlib import Path

from utilities.converters import upos_to_perseus


def load_lang_features(lang, additional_features):
    """Load language-specific features from a JSON file."""
    path = Path(__file__).parent
    with open(f'{path}/data/feats.json') as file:
        all_features_0 = json.load(file)

    featset = all_features_0['features'][lang]

    if additional_features:
        with open(f'{path}/{additional_features}') as file:
            xtra_features = json.load(file)
            for f_name, f_dict in xtra_features.items():
                featset[f_name] = f_dict

    return featset


def feature_string_to_dict(fstring):
    """Convert a feature string to a dictionary."""
    if not fstring or fstring == '_':
        return {}

    f_pairs = [i.split('=') for i in fstring.split('|')]
    return {i[0]: i[1] for i in f_pairs}


def feature_dict_to_string(fdict):
    """Convert a feature dictionary to a string."""
    if not fdict:
        return '_'

    sorted_features = OrderedDict(sorted(fdict.items(), key=lambda x: x[0].lower()))
    return '|'.join([f'{k}={v}' for k, v in sorted_features.items()])


def normalize_features(upos, features, featset):
    """Normalize features based on UPOS and a feature set."""
    if upos is None or featset is None:
        msg = 'Must pass UPOS, FEATS, and a Feature set'
        raise ValueError(msg)

    if features:
        output = {}

        if type(features) is not dict:
            features = feature_string_to_dict(features)

        for attr, value in features.items():
            if attr in featset:
                record = featset[attr]
                if upos in record['byupos'] and value in record['byupos'][upos] and record['byupos'][upos][value] != 0:
                    output[attr] = value

        return output

    return features


def normalize_xpos(upos, xpos):
    """Normalize XPOS based on UPOS."""
    if not upos or not xpos:
        msg = 'Must pass both UPOS and XPOS'
        raise ValueError(msg)

    validity_by_pos = {
        2: 'v',
        3: 'nvapm',
        4: 'v',
        5: 'v',
        6: 'v',
        7: 'nvapm',
        8: 'nvapm',
        9: 'a',
    }

    upos_tag = upos_to_perseus(upos)
    new_xpos = ''
    for i, val in enumerate(xpos[1:], start=2):
        new_xpos = new_xpos + val if upos_tag in validity_by_pos.get(i, '') else new_xpos + '-'

    return f'{upos_tag}{new_xpos}'


def get_md5(filepath):
    """Calculate the MD5 hash of a file."""
    return hashlib.md5(open(filepath, 'rb').read()).hexdigest()
