"""DemoKaranaAgent — deterministic, rules-based stand-in for a future agent.

IMPORTANT: this is DEMO / SIMULATED agent behaviour. No LLM or model provider
is connected. Decisions are produced by deterministic rules over the actual
submitted answers; every decision carries an explicit, auditable trace.

The rooms service depends only on the `KaranaAgent` protocol below, so a real
agent can be dropped in later without touching room routes or UI.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Protocol

from .rooms_content import MISTAKE_BANK, RELAY_BANK

DEMO_LABEL = "[Karana demo agent — simulated, no AI model connected]"


class KaranaAgent(Protocol):
    async def resolve_relay(self, question: str, submissions: List[dict]) -> Dict[str, Any]:
        """Decide follow-up + explanation from independent submissions."""
        ...


class DemoKaranaAgent:
    """Rules-based interpretation of submitted answers.

    Response patterns:
      - agree:            every substantive submission contains the key concept
      - agree_incorrect:  substantive submissions agree with each other but NONE
                         contains the key concept (shared wrong idea — not a
                         diagnosed misconception, just an observed overlap)
      - disagree:         at least one submission has the key concept and at
                         least one clearly lacks it
      - unmatched:        the question does not correspond to any known relay
                         item — no bank answer is imposed
      - insufficient:     too few submissions, or too short / off-topic to judge

    Classification is keyword-substring based in BOTH English and Odia
    (item["keywords"] / item["keywords_or"]). A stable bank ID always wins over
    fuzzy matching: pass it as `bank_item_id`, or embed it in the question text.
    """

    min_chars_for_judgement = 15
    min_match_score = 2  # fuzzy token matches below this are treated as no match

    async def pick_relay_item(self, question: str, chapter_hint: str = "",
                              bank_item_id: Optional[str] = None) -> Optional[dict]:
        # 1. Stable ID beats everything — never guess when an ID is known.
        if bank_item_id:
            for item in RELAY_BANK:
                if item["id"] == bank_item_id:
                    return item
        q = question.lower()
        for item in RELAY_BANK:  # ID embedded in the question text
            if item["id"] in q:
                return item
        best: Optional[dict] = None
        best_score = 0
        for item in RELAY_BANK:
            score = 0
            for token in re.findall(r"[a-z]{4,}", item["question"].lower()):
                if token in q:
                    score += 1
            if chapter_hint and chapter_hint in item["chapter_hint"] + item["id"]:
                score += 2
            if score > best_score:
                best, best_score = item, score
        return best if best_score >= self.min_match_score else None

    def _is_correct(self, item: dict, content: str) -> bool:
        text = (content or "").lower()
        keywords = [k.lower() for k in item.get("keywords", [item["correct_answer"]])]
        keywords += item.get("keywords_or", [])
        return any(k in text for k in keywords if k)

    def _classify(self, item: dict, submissions: List[dict]) -> str:
        if len(submissions) < 2:
            return "insufficient"
        relevant = [s for s in submissions
                    if len(s.get("content", "") or "") >= self.min_chars_for_judgement]
        if len(relevant) < 2:
            return "insufficient"
        hits = sum(1 for s in relevant if self._is_correct(item, s["content"]))
        if hits == len(relevant):
            return "agree"
        if hits == 0:
            return "agree_incorrect"
        return "disagree"

    async def resolve_relay(self, question: str, submissions: List[dict],
                            chapter_hint: str = "",
                            bank_item_id: Optional[str] = None) -> Dict[str, Any]:
        item = await self.pick_relay_item(question, chapter_hint, bank_item_id)
        if item is None:
            # No known relay item matches this question. Be explicit — do NOT
            # silently substitute an unrelated bank question (defect D3).
            unresolved = [
                "This question is not in the demo relay bank, so there is no "
                "authoritative answer to compare against.",
                "The group should discuss the submitted answers directly; a "
                "teacher can add this question to the bank later.",
            ]
            trace = [
                {"step": "observe",
                 "detail": f"Observed {len(submissions)} independent submission(s)."},
                {"step": "match",
                 "detail": "No relay bank item matched this question "
                           f"(question={question!r}, chapter_hint={chapter_hint!r}); "
                           "no fallback item was selected."},
                {"step": "demo_note", "detail": DEMO_LABEL},
            ]
            return {
                "bank_id": None,
                "expected_answer": None,
                "explanation": None,
                "pattern": "unmatched",
                "followup": {"text": "This doubt is not in the demo answer bank yet. "
                                     "Read each other's answers below and discuss which "
                                     "one the lesson chunk supports."},
                "verification": None,
                "proceed_to_verification": False,
                "unresolved": unresolved,
                "trace": trace,
                "demo": True,
            }
        pattern = self._classify(item, submissions)
        followup = item["followups"].get(pattern)
        if followup is None:  # agree_incorrect has no banked follow-up yet
            followup = (f"Your answers agree with each other, but none of them mentions "
                        f"'{item['correct_answer']}'. Re-read the explanation below and "
                        "discuss where the key idea was missed — this is an observed "
                        "shared gap, not a diagnosed misconception.")
        need_verification = pattern in ("agree", "disagree", "agree_incorrect")
        unresolved: List[str] = []
        if pattern == "insufficient":
            unresolved.append("Responses were too brief or off-topic to compare — "
                              "the group still needs a shared answer.")
        if pattern in ("disagree", "agree_incorrect"):
            unresolved.append(f"Some members' answers did not mention '{item['correct_answer']}' — "
                              "confirm understanding during verification.")
        unresolved.append("New member questions raised in discussion were not recorded "
                          "as separate doubt-relay activities yet.")
        trace = [
            {
                "step": "observe",
                "detail": f"Observed {len(submissions)} independent submission(s); "
                          f"{sum(1 for s in submissions if len(s.get('content', '') or '') >= self.min_chars_for_judgement)} "
                          "were long enough to judge.",
            },
            {
                "step": "classify",
                "detail": f"Pattern = {pattern}: submissions were each classified "
                          f"against the key concept '{item['correct_answer']}' "
                          "(English and Odia keywords); agreement on a wrong "
                          "answer is reported as agree_incorrect, not as a "
                          "diagnosed misconception.",
            },
            {
                "step": "select_followup",
                "detail": f"Selected '{pattern}' follow-up because the response pattern "
                          f"was {pattern} (rule: unanimous→deepen, mixed→compare, "
                          "thin→ask for more evidence).",
            },
            {
                "step": "verify_gate",
                "detail": f"Enough evidence to move to verification: {need_verification}.",
            },
        ]
        if unresolved:
            trace.append({"step": "unresolved", "detail": "; ".join(unresolved)})
        trace.append({"step": "demo_note", "detail": DEMO_LABEL})
        return {
            "bank_id": item["id"],
            "expected_answer": item["expected_answer"],
            "explanation": item["explanation"],
            "pattern": pattern,
            "followup": {"text": followup},
            "verification": item["verification"] if need_verification else None,
            "proceed_to_verification": need_verification,
            "unresolved": unresolved,
            "trace": trace,
            "demo": True,
        }

    async def resolve_game(self, problem_id: str, submissions: List[dict]) -> Dict[str, Any]:
        item = next((m for m in MISTAKE_BANK if m["id"] == problem_id), MISTAKE_BANK[0])
        found = [s for s in submissions
                 if self._submission_points_to_line(s, item)]
        reasoned = [s for s in submissions if len(s.get("reasoning", "") or "") >= 20]
        trace = [
            {"step": "observe",
             "detail": f"{len(submissions)} submission(s); {len(found)} identified the seeded "
                       f"error on line {item['mistake_index'] + 1}; {len(reasoned)} gave a "
                       "reasoned explanation."},
            {"step": "reveal",
             "detail": "Revealing expected answer and explanation; no speed scoring — "
                       "participation and reasoning are what count."},
            {"step": "demo_note", "detail": DEMO_LABEL},
        ]
        return {
            "expected": {"mistake_index": item["mistake_index"],
                         "answer": item["expected_answer"],
                         "explanation": item["explanation"]},
            "followup": {"text": item["followup"]},
            "group_stats": {"found": len(found), "reasoned": len(reasoned),
                            "total": len(submissions)},
            "trace": trace,
            "demo": True,
        }

    def _submission_points_to_line(self, s: dict, item: dict) -> bool:
        line = s.get("mistake_line", "") or ""
        return str(item["mistake_index"]) in line
