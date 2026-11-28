"""Quality Validation vocabulary: what was checked about an example, and by whom.

Each example keeps six checks separately (task contract 3.0, §3); none of them implies another:

    checks = {"source": "script",        # the quote was found verbatim in the downloaded source
              "context": "model"|None,   # the surrounding text is enough to tell the meaning
              "meaning": "model"|"auto-ru"|None,   # auto-ru = the source's Russian line contains this
                                                    # meaning's translation (a signal, not a verification)
              "translation": "model"|None,         # someone compared the Russian with the quote
              "grammar": "model"|"auto-pos"|None,  # auto-pos = a POS tagger agreed with the unit's part of speech
              "human": False}

status (derived, the names from the contract) lists only what was actually verified — by the model or a
human, never by a heuristic: source_verified, context_verified, meaning_verified, translation_verified,
grammar_verified, human_reviewed; plus needs_review when meaning or translation is not verified, and
rejected for examples kept only as a record. Nothing in this pipeline sets human_reviewed.
"""
from __future__ import annotations

CHECKS = ("source", "context", "meaning", "translation", "grammar", "human")
STATUS = {"source": "source_verified", "context": "context_verified", "meaning": "meaning_verified",
          "translation": "translation_verified", "grammar": "grammar_verified", "human": "human_reviewed"}
VERIFIED_BY = {"script": ("source",), "model": ("context", "meaning", "translation", "grammar"),
               "human": CHECKS}


def status(checks: dict, rejected: bool = False) -> list[str]:
    out = []
    for k in CHECKS:
        v = checks.get(k)
        if k == "human":
            if v is True:
                out.append(STATUS[k])
        elif v and (k in VERIFIED_BY.get(v, ()) or v == "human"):
            out.append(STATUS[k])
    if not ({"meaning_verified", "translation_verified"} <= set(out)) and "human_reviewed" not in out:
        out.append("needs_review")
    if rejected:
        out.append("rejected")
    return out


def coverage(examples: list[dict], meanings: list[dict]) -> str:
    """Unit state: full / partial / insufficient_authentic_data (no quota: just what is there)."""
    if not examples:
        return "insufficient_authentic_data"
    per_m = {m["id"]: sum(1 for e in examples if e.get("m") == m["id"]) for m in meanings}
    kinds = {(e.get("src") or ":").split(":")[0] if e.get("src") else e["id"].split("-")[1] for e in examples}
    if len(examples) >= 5 and all(n >= 1 for n in per_m.values()) and len(kinds) >= 2:
        return "full"
    return "partial"
