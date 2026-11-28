"""«Ещё занятие» — extra practice in one tap once the lesson is over (owner, 2026-11-28).

A filtered sub-deck "English Trainer::Ещё занятие" (Anki's own mechanism, so it works on the phone too):
    1. today's mistakes            (rated:1:1)              — up to 30, random order
    2. reviews due in 1–3 days     (prop:due>=1 prop:due<=3) — up to 30, by due date
"Reschedule cards based on my answers" is ON: the answers go into the same cards' history and schedule —
the main progress. Nothing is invented and no grade is computed here (Anki grades).

The add-on keeps it honest:
    * while the main lesson still has cards, the sub-deck is emptied (it never takes cards from the lesson);
    * when the lesson is done, it is rebuilt — on the computer after the lesson / sync / start of Anki;
    * on a phone (AnkiDroid) the same deck is there after sync: one tap starts it; if it is empty there,
      «Пересобрать» (Rebuild) fills it from the phone's own answers of today.
Pure functions (col only) + hooks at the bottom.
"""
from __future__ import annotations

MAIN = "English Trainer"
NAME = MAIN + "::Ещё занятие"
_NOT = f'-deck:"{NAME}" -is:suspended -is:buried'
TERMS = [  # (search, limit, order)
    (f'deck:"{MAIN}" {_NOT} rated:1:1', 30, "RANDOM"),
    (f'deck:"{MAIN}" {_NOT} -is:new prop:due>=1 prop:due<=3', 30, "DUE"),
]


def _node_counts(col, did) -> int:
    node = col.sched.deck_due_tree(did)
    return (node.new_count + node.learn_count + node.review_count) if node else 0


def ensure(col) -> int | None:
    """The filtered sub-deck (created once, kept: its definition syncs to the phone). Returns its id."""
    main = col.decks.id_for_name(MAIN)
    if not main:
        return None
    did = col.decks.id_for_name(NAME)
    if did and col.decks.get(did).get("dyn"):
        return did
    from anki.decks_pb2 import Deck
    # created empty (adding a filtered deck through the scheduler fails when nothing matches yet)
    did = col.decks.new_filtered(NAME)
    deck = col.decks.get(did)
    deck["terms"] = [[search, limit, Deck.Filtered.SearchTerm.Order.Value(order)] for search, limit, order in TERMS]
    deck["resched"] = True
    col.decks.save(deck)
    col.sched.empty_filtered_deck(did)
    col.decks.select(col.decks.id_for_name(MAIN))   # new_filtered selects the new deck: give the main one back
    return did


def refresh(col) -> int:
    """Empty while the lesson has cards, fill once it is done. Returns the number of cards in the sub-deck."""
    did = ensure(col)
    if not did:
        return 0
    main = col.decks.id_for_name(MAIN)
    extra_now = len(col.find_cards(f'deck:"{NAME}"'))
    left = _node_counts(col, main) - (_node_counts(col, did) if extra_now else 0)
    if left > 0:
        if extra_now:
            col.sched.empty_filtered_deck(did)
        return 0
    if extra_now == 0:
        try:
            col.sched.rebuild_filtered_deck(did)
        except Exception:      # nothing to practise right now (FilteredDeckError) — the deck stays empty
            return 0
    return len(col.find_cards(f'deck:"{NAME}"'))


# ------------------------------------------------------------------------------------------------ hooks
def _install() -> None:
    try:
        from aqt import gui_hooks, mw
    except Exception:
        return

    def run(*_a) -> None:
        try:
            if mw.col and mw.state != "review":
                refresh(mw.col)
                if mw.state in ("deckBrowser", "overview"):
                    mw.deckBrowser.refresh() if mw.state == "deckBrowser" else mw.overview.refresh()
        except Exception as e:
            print("English Trainer extra:", e)

    def on_state(new_state, old_state, *_a) -> None:
        if old_state == "review" and new_state in ("overview", "deckBrowser"):
            run()

    gui_hooks.profile_did_open.append(run)
    gui_hooks.sync_did_finish.append(run)
    gui_hooks.state_did_change.append(on_state)


_install()
