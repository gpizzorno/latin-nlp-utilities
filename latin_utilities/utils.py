import hashlib
import json
from collections import OrderedDict
from pathlib import Path

from latin_utilities.converters import upos_to_perseus
from latin_utilities.converters.ittb_to_perseus import (
    cas_to_case,
    cas_to_number,
    gen_to_gender,
    gen_to_number,
    gen_to_person,
    grnp_to_degree,
    mod_to_mood,
    mod_to_voice,
    tem_to_tense,
)
from latin_utilities.converters.proiel_converters import (
    to_case,
    to_degree,
    to_gender,
    to_mood,
    to_number,
    to_tense,
    to_voice,
)


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


def format_ittb_xpos(upos, xpos):
    """Format ITTB UPOS and XPOS as Perseus XPOS tag."""
    xpos_dict = {el[:3]: el[3] for el in xpos.split('|') if len(el) == 4}  # noqa: PLR2004

    # compile tags:
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = gen_to_person(xpos_dict['gen']) if 'gen' in xpos_dict else '-'  # 2: person

    # 3: number
    if 'cas' in xpos_dict:
        number = cas_to_number(xpos_dict['cas'])
    elif 'gen' in xpos_dict:
        number = gen_to_number(xpos_dict['gen'])
    else:
        number = '-'

    tense = tem_to_tense(xpos_dict['tem']) if 'tem' in xpos_dict else '-'  # 4: tense
    mood = mod_to_mood(xpos_dict['mod']) if 'mod' in xpos_dict else '-'  # 5: mood
    voice = mod_to_voice(xpos_dict['mod']) if 'mod' in xpos_dict else '-'  # 6: voice
    gender = gen_to_gender(xpos_dict['gen']) if 'gen' in xpos_dict else '-'  # 7: gender
    case = cas_to_case(xpos_dict['cas']) if 'cas' in xpos_dict else '-'  # 8: case

    # 9: degree
    ittb_t = xpos_dict.get('grn', xpos_dict.get('grp'))
    degree = grnp_to_degree(ittb_t) if ittb_t else '-'

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'


def format_proiel_xpos(upos, feats):
    """Format PROIEL UPOS and FEATS as Perseus XPOS tag."""
    feats_dict = feature_string_to_dict(feats)
    # compile tags:
    pos = upos_to_perseus(upos)  # 1: part of speech
    person = feats_dict.get('Person', '-')  # 2: person
    number = to_number(feats_dict.get('Number')) if 'Number' in feats_dict else '-'  # 3: number
    tense = to_tense(feats_dict.get('Tense')) if 'Tense' in feats_dict else '-'  # 4: tense
    mood = to_mood(feats_dict.get('Mood')) if 'Mood' in feats_dict else '-'  # 5: mood
    voice = to_voice(feats_dict.get('Voice')) if 'Voice' in feats_dict else '-'  # 6: voice
    gender = to_gender(feats_dict.get('Gender')) if 'Gender' in feats_dict else '-'  # 7: gender
    case = to_case(feats_dict.get('Case')) if 'Case' in feats_dict else '-'  # 8: case
    degree = to_degree(feats_dict.get('Degree')) if 'Degree' in feats_dict else '-'  # 9: degree

    return f'{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{degree}'


def format_llct_xpos(upos, xpos):
    """Format LLCT UPOS and XPOS as Perseus XPOS tag."""
    xpos_list = xpos.split('|')

    # ensure correct PoS tag
    xpos_list[0] = upos_to_perseus(upos)
    return ''.join(xpos_list)
