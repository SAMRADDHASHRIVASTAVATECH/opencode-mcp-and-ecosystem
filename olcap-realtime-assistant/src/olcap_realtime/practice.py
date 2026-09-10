"""Interview / practice + workspace + meeting engines (spec 16, 17, 38, 39).

Question classification and structured scaffolding are deterministic rule-based
logic (not faked model output). Answer/hint generation can optionally use the
reasoning model; without one it returns MODEL_UNAVAILABLE rather than inventing.

NO hidden overlays or anti-detection functionality is included: this is for
authorized interview *practice*, not prohibited live assessments.
"""
from __future__ import annotations

import re

QUESTION_TYPES = {"behavioral", "technical", "coding", "system_design",
                  "follow_up", "unknown"}

BEHAVIORAL = {"tell me about yourself", "why do you want", "strengths", "weakness",
              "conflict", "team", "fail", "challenge", "leadership", "situation",
              "tell me about a time", "describe a time", "motivated", "feedback",
              "priority", "deadline", "mistake", "difficult", "collaborate",
              "communication", "achievement", "pressure", "goal"}
TECHNICAL = {"what is", "explain", "difference between", "how does", "database",
             "api", "rest", "http", "thread", "memory", "sql", "tcp", "oop",
             "polymorphism", "inheritance", "cache", "index", "function",
             "variable", "synchronization", "deadlock", "complexity of",
             "data structure", "algorithm"}
CODING = {"code", "implement", "write a function", "write program", "leetcode",
          "two sum", "reverse", "linked list", "array", "sort", "binary search",
          "tree", "graph", "string", "recursion", "dynamic programming", "o(n",
          "time complexity", "solve"}
SYSTEM_DESIGN = {"design", "architecture", "system design", "scale", "distributed",
                 "how would you build", "microservices", "load balancer"}


def classify_question(q: str) -> dict:
    ql = (q or "").lower()
    scores = {"behavioral": 0, "technical": 0, "coding": 0, "system_design": 0}
    for w in BEHAVIORAL:
        if w in ql:
            scores["behavioral"] += 1
    for w in TECHNICAL:
        if w in ql:
            scores["technical"] += 1
    for w in CODING:
        if w in ql:
            scores["coding"] += 1
    for w in SYSTEM_DESIGN:
        if w in ql:
            scores["system_design"] += 1
    best = max(scores, key=scores.get)
    qtype = best if scores[best] > 0 else "unknown"
    if qtype == "unknown" and ql.endswith("?"):
        qtype = "technical"
    if re.search(r"why|how (do|would|did)|tell me about a time", ql) and \
            scores["behavioral"] >= scores["coding"]:
        qtype = "behavioral"
    # coding keywords trump when present
    if scores["coding"] > 0:
        qtype = "coding"
    if scores["system_design"] > scores["coding"] and scores["system_design"] >= 2:
        qtype = "system_design"
    return {"question_type": qtype, "question": q, "scores": scores}


def _key_points(qtype, question):
    if qtype == "behavioral":
        return ["Use the STAR structure (Situation, Task, Action, Result).",
                "Give a concrete example, not a hypothetical.",
                "State the outcome and what you learned."]
    if qtype == "coding":
        return ["Clarify input constraints and expected complexity first.",
                "State your approach and a brute force before optimizing.",
                "Walk through a small example, then edge cases."]
    if qtype == "system_design":
        return ["Clarify requirements and scale (users, QPS, data).",
                "Start with an outline: components + data flow.",
                "Discuss bottlenecks and how to handle failure."]
    if qtype == "technical":
        return ["Answer the core concept precisely first.",
                "Give a short concrete example.",
                "Connect to trade-offs or common pitfalls."]
    return ["Restate the question to confirm understanding.",
            "Structure a clear, concise response."]


class InterviewPracticeEngine:
    def __init__(self, reasoning=None):
        self.reasoning = reasoning

    def _model_ok(self) -> bool:
        if self.reasoning is None:
            return False
        avail = getattr(self.reasoning, "available", None)
        return True if avail is None else bool(avail)

    def _gen(self, msgs, **kw):
        """Return generated text or None if no reachable model."""
        if not self._model_ok():
            return None
        return self.reasoning.generate(msgs, **kw)

    def analyze_question(self, question: str) -> dict:
        cls = classify_question(question)
        return {"question_type": cls["question_type"],
                "question": question,
                "key_points": _key_points(cls["question_type"], question),
                "common_mistakes": _common_mistakes(cls["question_type"])}

    def generate_answer(self, question: str, context=None) -> dict:
        cls = classify_question(question)
        if not self._model_ok():
            return {"question_type": cls["question_type"], "question": question,
                    "suggested_answer": None,
                    "note": "no reachable reasoning model; provide a model for a "
                            "drafted answer"}
        msgs = self._msgs("You are an interview-practice coach. Answer concisely "
                          "in STAR/key-points structure and give a model response.",
                          context, question)
        return {"question_type": cls["question_type"], "question": question,
                "suggested_answer": self.reasoning.generate(msgs, max_tokens=400)}

    def generate_hint(self, question: str, context=None) -> dict:
        cls = classify_question(question)
        hints = ["Clarify constraints or the exact scope.",
                 "Think of the simplest correct approach first.",
                 "Consider time/space complexity and edge cases."]
        return {"question_type": cls["question_type"], "hints": hints,
                "question": question}

    def evaluate_answer(self, question: str, answer: str, context=None) -> dict:
        cls = classify_question(question)
        if not answer or len(answer) < 10:
            return {"score": 0.2, "feedback": "Answer is too short; give a "
                    "structured response.", "question_type": cls["question_type"]}
        # deterministic rubric on structure/length (not fake model output)
        score = min(1.0, 0.4 + 0.4 * min(1.0, len(answer) / 400))
        feedback = []
        if any(w in answer.lower() for w in ("because", "so", "therefore", "as a result")):
            score = min(1.0, score + 0.1)
        else:
            feedback.append("Explain the 'why', not just the 'what'.")
        if cls["question_type"] == "behavioral" and \
                not any(w in answer.lower() for w in ("situation", "task", "action", "result")):
            feedback.append("Use STAR structure for behavioral answers.")
        if not feedback:
            feedback.append("Good structure. Consider adding a concrete metric or "
                            "outcome.")
        return {"score": round(score, 2), "feedback": " ".join(feedback),
                "question_type": cls["question_type"]}

    # ---- coding practice (spec 38) ---- #
    def analyze_code(self, problem: str) -> dict:
        return {"problem": problem,
                "fields": ["problem understanding", "constraints", "approach",
                           "algorithm", "complexity", "edge_cases",
                           "implementation", "explanation"]}

    def generate_solution(self, problem: str, code=None, context=None) -> dict:
        if not self._model_ok():
            return {"problem": problem, "solution": None,
                    "note": "no reachable reasoning model"}
        msgs = self._msgs("You are a coding-practice coach. Produce: understanding, "
                          "constraints, approach, algorithm, complexity, edge cases, "
                          "implementation (Python), explanation.", context, problem)
        return {"problem": problem, "solution": self.reasoning.generate(msgs,
                                                                        max_tokens=700)}

    def explain_solution(self, code: str, context=None) -> dict:
        if not self._model_ok():
            return {"code": code, "explanation": None,
                    "note": "no reachable reasoning model"}
        msgs = self._msgs("Explain the following code step by step, complexity and "
                          "edge cases.", context, code)
        return {"explanation": self.reasoning.generate(msgs, max_tokens=500),
                "code": code}

    @staticmethod
    def _msgs(system, context, user):
        return [{"role": "system", "content": system},
                ({"role": "system", "content": "Context: " + str(context)} if context else None),
                {"role": "user", "content": user}]


def _common_mistakes(qtype):
    if qtype == "behavioral":
        return ["Generic or hypothetical answers without a real example.",
                "No result/outcome.",
                "Rambling without structure."]
    if qtype == "coding":
        return ["Jumping to code before clarifying constraints.",
                "Missing edge cases (empty, large, duplicates).",
                "Not stating complexity."]
    if qtype == "system_design":
        return ["Ignoring scale requirements.",
                "No clear data flow.",
                "Missing failure handling."]
    if qtype == "technical":
        return ["Too vague.",
                "No concrete example.",
                "Confusing related concepts."]
    return []


class WorkspaceEngine:
    """Combines screen + voice context into a reasoning request (spec 17, 39)."""
    def __init__(self, reasoning=None):
        self.reasoning = reasoning

    def _model_ok(self):
        if self.reasoning is None:
            return False
        avail = getattr(self.reasoning, "available", None)
        return True if avail is None else bool(avail)

    def understand(self, voice: str, screen_summary: str, active_app: str,
                   task: str = "") -> dict:
        combined = {
            "voice_context": voice,
            "screen_context": screen_summary,
            "active_application": active_app,
            "task": task,
        }
        if not self._model_ok():
            return {**combined, "guidance": None,
                    "note": "no reachable reasoning model"}
        msgs = [{"role": "system", "content": "You are a realtime workspace assistant. "
                 "Use the current screen and recent voice to give concise, useful, "
                 "next-action guidance."},
                {"role": "user", "content": str(combined)}]
        return {**combined, "guidance": self.reasoning.generate(msgs, max_tokens=350)}


class MeetingEngine:
    """Meeting assistance from a transcript (spec: meetings tools). Deterministic
    extraction helpers + optional generative summary."""
    def __init__(self, reasoning=None):
        self.reasoning = reasoning

    def _model_ok(self):
        if self.reasoning is None:
            return False
        avail = getattr(self.reasoning, "available", None)
        return True if avail is None else bool(avail)

    def summarize(self, transcript: str):
        if not self._model_ok():
            lines = [l for l in transcript.splitlines() if l.strip()]
            return {"summary": "Transcript (%d lines). Enable a reasoning model for "
                    "a generative summary." % len(lines),
                    "source": "deterministic"}
        msgs = [{"role": "system", "content": "Summarize this meeting transcript "
                 "concisely."}, {"role": "user", "content": transcript}]
        return {"summary": self.reasoning.generate(msgs, max_tokens=500),
                "source": "model"}

    def extract_actions(self, transcript: str):
        actions = [l for l in transcript.splitlines()
                   if re.search(r"\b(will|to|should|need to|action|todo|follow up)\b",
                                l.lower())]
        return {"actions": actions[:20]}

    def extract_decisions(self, transcript: str):
        decisions = [l for l in transcript.splitlines()
                     if re.search(r"\b(decided|we will|agreed|approved|confirmed)\b",
                                  l.lower())]
        return {"decisions": decisions[:20]}

    def extract_questions(self, transcript: str):
        qs = [l for l in transcript.splitlines() if l.strip().endswith("?")]
        return {"questions": qs[:20]}
