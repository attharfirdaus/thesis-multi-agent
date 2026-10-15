"""Rule-based evidence check for PRD §6, step 4.

A score is only credible if the agent's quote really occurs in the student's analysis, so the
pipeline locates every quote in the stored text before anything is saved. Two rules shape this
module:

- *Tolerate the copying, not the invention.* A model reproducing a passage changes its line breaks,
  its dash and its quotation marks. Those are formatting differences, so they are matched through a
  normalised view of the text. A paraphrase is no longer the student's own words, so it must fail:
  when the normalised quote is absent this module returns `None` and the caller treats the score as
  unverified rather than guessing a span.
- *Offsets point into the original string.* The database stores `start_offset`/`end_offset` against
  the stored, already-redacted analysis text, and the detail view re-slices that same string to
  highlight the quote, so the mapping from the normalised view back to the original is kept
  character by character instead of recomputed approximately.
"""

# Quote glyphs a model substitutes freely (curly and guillemet forms) collapse to the ASCII pair.
# A comparison artefact only: the stored quote and the highlighted span keep the original glyph.
_QUOTES = str.maketrans(
    {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u00ab": '"', "\u00bb": '"'}
)
# A hyphen at the end of a line, and a soft hyphen, join the halves of a word that extraction split
# across lines. They are dropped *only* at a line break, so a genuine compound such as "well-known"
# survives inside a line.
_SOFT_HYPHEN = "\u00ad"
_LINE_BREAK_HYPHENS = "-\u2010\u2011\u00ad"


def _view(text: str) -> tuple[str, list[int]]:
    """`text` as comparison text, plus the original index of every character in it.

    The index list is the whole point: it lets `locate_quote` answer in offsets of the string it was
    given, whatever collapsing, folding or joining happened on the way.
    """
    out: list[str] = []
    origin: list[int] = []
    length = len(text)
    position = 0
    while position < length:
        char = text[position]
        if char in _LINE_BREAK_HYPHENS and position + 1 < length and text[position + 1].isspace():
            # Both the hyphen and the break it caused are dropped: the word continues on the next
            # line, so "kri-\ntis" has to collapse to "kritis" and not to "kri tis".
            position += 1
            while position < length and text[position].isspace():
                position += 1
            continue
        if char == _SOFT_HYPHEN:
            position += 1  # hyphenation hint, invisible in the text the student wrote
            continue
        if char.isspace():
            end = position
            while end < length and text[end].isspace():
                end += 1
            out.append(" ")
            origin.append(position)
            position = end
            continue
        folded = char.translate(_QUOTES).casefold()
        out.extend(folded)
        origin.extend([position] * len(folded))
        position += 1
    return "".join(out), origin


def normalise(value: str) -> str:
    """Comparison form: whitespace collapsed, ends stripped, case-folded, quote glyphs unified.

    Comparison only. The form is never stored and never returned as evidence, because the lecturer
    must see the student's own characters.
    """
    collapsed = _view(value)[0]
    return collapsed.strip()


def locate_quote(text: str, quote: str) -> tuple[int, int] | None:
    """Half-open `(start, end)` offsets of `quote` in `text`, or `None` when it is not there.

    `None` is a verdict, not an error: the caller records the score as unverified and asks synthesis
    to try again (PRD §6). Returning a nearby span instead would invent evidence.
    """
    needle = normalise(quote)
    if not needle:
        return None
    haystack, origin = _view(text)
    found = haystack.find(needle)
    if found < 0:
        return None
    # The last needle character's original index plus one, so `text[start:end]` covers the whole
    # match including any character whose case folding expanded into several comparison characters.
    return origin[found], origin[found + len(needle) - 1] + 1
