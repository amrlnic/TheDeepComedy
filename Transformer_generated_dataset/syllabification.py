# coding=utf-8

import re

# Syllabification module.
# A special thanks goes to Simona S., Italian linguist, teacher and friend, without whom this module could never exist.

# This module is used both for building the dataset and for computing metrics.
# IMPORTANT: the #, @ and § characters are used internally to correctly split syllables, the input string should not contain them.

# Splits a string along word boundaries (empty spaces and punctuation marks). If synalepha is True, doesn't split
# words which have a vowel boundary (eg. selva_oscura).
def split_words(str, synalepha=False):
    regex = re.compile(r"""[,.;:"“”«»?—'`‘’\s]*\s+[,.;:"“”«»?—'`‘’\s]*""")
    matches = regex.finditer(str)
    indexes = [0]

    for m in matches:
        begin = (m.start() - 1) if m.start() - 1 > 0 else 0
        end = m.end() + 1
        if _is_split_acceptable(str[begin: end], synalepha):
            indexes.append(begin + 1)

    return [str[i:j] for i,j in zip(indexes, indexes[1:]+[None])]

# Splits a single word into syllables.
def syllabify_word(str):
    return _perform_final_splits(_perform_initial_splits(str))

# Splits a block into words and then into syllables.
def syllabify_block(str, synalepha=False):
    words = split_words(str, synalepha)
    syllables = [syllabify_word(w) for w in words]
    return "#".join(syllables)

# Removes capitalization, punctuation marks and, optionally, diacritics (accents and dieresis).
def prettify(str, keep_diacritics=True):
    if keep_diacritics:
        out = _strip_spaces(_strip_punctuaction(str.lower()))
    else:
        out = _strip_spaces(_strip_punctuaction(_remove_diacritics(str.lower())))
    return out

# Removes hash characters from a string.
def strip_hashes(str):
    return re.sub("#", "", str)

# Determines if a split between two words is acceptable, ie. if there are no synalepha nor elision (eg. "l' amico" should be kept together).
# Heuristic: all apostrophes are considered a non-breakable point. This is not always the case (eg. "perch’ i’ fu’" should be split into "perch’ i’"-"fu’).
def _is_split_acceptable(str, synalepha=False):
    prev = str[0]
    next = str[len(str) - 1]
    vowel = re.compile(r"""[AEIOUaeiouàèéìòóùÈ]""")
    apostrophe = re.compile(r""".*['`‘’].*""")
    newline = re.compile(r""".*\n+.*""")

    out = newline.match(str) or \
          not (apostrophe.match(str) and (vowel.match(prev) or vowel.match(next)))

    if synalepha:
        out = out and not (vowel.match(prev) and vowel.match(next))

    return out

# Removes punctuation from a string.
def _strip_punctuaction(str):
    return re.sub(r"""[,.;:"“”!?«»—'`’]+""", "", str)

# Removes diacritic marks from a string.
def _remove_diacritics(str):
    out = re.sub(r"""[àä]""", "a", str)
    out = re.sub(r"""[èéë]""", "e", out)
    out = re.sub(r"""[ìï]""", "i", out)
    out = re.sub(r"""[òóö]""", "o", out)
    out = re.sub(r"""[ùü]""", "u", out)
    return out

# Removes spaces from a string.
def _strip_spaces(str):
    return re.sub(r"""\s+""", "", str)

# Performs the first (easy and unambiguous) phase of syllabification.
def _perform_initial_splits(str):
    return _split_hiatus(_split_dieresis(_split_double_cons(_split_multiple_cons(str))))

# Performs the second (difficult and heuristic) phase of syllabification.
def _perform_final_splits(str):
    cvcv = r"""(?i)([bcdfglmnpqrstvz][,.;:"“”«»?—'`‘’\s]*[aeiouàèéìóòùÈËÏ]+)([bcdfglmnpqrstvz]+[,.;:"“”«»?—'`‘’\s]*[aeiouàèéìóòùÈËÏ]+)"""
    vcv = r"""(?i)([aeiouàèéìóòùÈËÏ]+)([bcdfglmnpqrstvz]+[,.;:"“”«»?—'`‘’\s]*[aeiouàèéìóòùÈËÏ]+)"""
    vv = r"""(?i)(?<=[aeiouàèéìóòùÈËÏ])(?=[aeiouàèéìóòùÈËÏ])"""

    # Split the contoid vocoid - contoid vocoid case (eg. ca-ne). Deterministic.
    out = re.sub(cvcv, r"""\1#\2""", str)
    # Split the vocoid - contoid vocoid case (eg. ae-reo). Deterministic.
    out = re.sub(vcv, r"""\1#\2""", out)

    # Split the vocoid - vocoid case (eg. a-iuola). Heuristic.
    out = _clump_diphthongs(out)
    out = re.sub(vv, r"""#""", out)
    out = re.sub("§", "", out)

    return out

# Splits double consonants (eg. al-legro)
def _split_double_cons(str):
    doubles = re.compile(r"""(?i)(([bcdfglmnpqrstvz])(?=\2)|c(?=q))""")
    return "#".join(doubles.sub(r"""\1@""", str).split("@"))

# Splits multiple consonants, except: impure s (sc, sg, etc.), mute followed by liquide (eg. tr), digrams and trigrams.
def _split_multiple_cons(str):
    impures = re.compile(r"""(?i)(s(?=[bcdfghlmnpqrtvz]))""")
    muteliquide = re.compile(r"""(?i)([bcdgpt](?=[lr]))""")
    digrams = re.compile(r"""(?i)(g(?=li)|g(?=n[aeiou])|s(?=c[ei])|[cg](?=h[eèéiì])|[cg](?=i[aou]))""")
    trigrams = re.compile(r"""(?i)(g(?=li[aou])|s(?=ci[aou]))""")
    multicons = re.compile(r"""(?i)([bcdfglmnpqrstvz](?=[bcdfglmnpqrstvz]+))""")

    # Preserve non admissibile splits.
    out ="§".join(impures.sub(r"""\1@""", str).split("@"))
    out = "§".join(muteliquide.sub(r"""\1@""", out).split("@"))
    out = "§".join(digrams.sub(r"""\1@""", out).split("@"))
    out = "§".join(trigrams.sub(r"""\1@""", out).split("@"))
    # Split everything else.
    out = "#".join(multicons.sub(r"""\1@""", out).split("@"))

    return "".join(re.split("§", out))

# Splits dieresis.
def _split_dieresis(str):
    dieresis = re.compile(r"""(?i)([äëïöüËÏ](?=[aeiou])|[aeiou](?=[äëïöüËÏ]))""")
    return "#".join(dieresis.sub(r"""\1@""", str).split("@"))

# Splits SURE hiatuses only. Ambiguous ones are heuristically considered diphthongs.
def _split_hiatus(str):
    hiatus = re.compile(r"""(?i)([aeoàèòóé](?=[aeoàèòóé])|[rb]i(?=[aeou])|tri(?=[aeou])|[ìù](?=[aeiou]))""")
    return "#".join(hiatus.sub(r"""\1@""", str).split("@"))

# Prevents splitting of diphthongs and triphthongs.
def _clump_diphthongs(str):
    diphthong = r"""(?i)(i[,.;:"“”«»?—'`‘’\s]*[aeouàèéòóù]|u[,.;:"“”«»?—'`‘’\s]*[aeioàèéìòó]|[aeouàèéòóù][,.;:"“”«»?—'`‘’\s]*i|[aeàèé][,.;:"“”«»?—'`‘’\s]*u)"""
    diphthongsep = r"""(\{.[,.;:"“”«»?—'`‘’\s]*)(.\})"""
    triphthong = r"""(?i)(i[àèé]i|u[àòó]i|iu[òó])"""
    triphthongsep = r"""(\{.)(.)(.\})"""

    out = re.sub(triphthong, r"""{\1}""", str)
    out = re.sub(triphthongsep, r"""\1§\2§\3""", out)
    out = re.sub(diphthong, r"""{\1}""", out)
    out = re.sub(diphthongsep, r"""\1§\2""", out)
    out = re.sub(r"""[{}]""", "", out)

    return out