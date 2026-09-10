"""Experience engine - the learning loop.

  record      -> store a raw Experience (action + outcome + error/fix)
  reflect     -> derive lesson(s) from an experience / session summary
  learn       -> explicitly add a durable lesson (manual or from reflect)
  retrieve    -> find relevant lessons for a new task (ranked)
  consolidate -> merge duplicates, update confidence, mark obsolete, promote strong
  promote     -> repeatedly-validated lessons become strong long-term lessons

Rules are deterministic and auditable. Lessons may be protected (never auto-
touched). No underlying model / safeguard / security config is modified.
"""
from __future__ import annotations

import re
import time
from difflib import SequenceMatcher

from . import model as M
from .errors import NotFound, ProtectedLesson, ValidationError
from .store import Store, gen_id


class ExperienceEngine:
    def __init__(self, store: Store):
        self.store = store
        self.memory_path = ""          # set by factory for reporting

    # ------------------------------------------------------------------ #
    # 1. RECORD
    # ------------------------------------------------------------------ #
    def record(self, *, action, outcome, detail="", error="", fix="", verdict="",
               category="general", tags=None, source=M.SOURCE_PATTERN,
               derive_lesson=False) -> dict:
        if outcome not in (M.OUTCOME_OK, M.OUTCOME_FAIL):
            raise ValidationError(f"outcome must be success|failure, got {outcome}")
        exp = M.Experience(action=action, outcome=outcome, detail=detail,
                           error=error, fix=fix, verdict=verdict,
                           category=category, tags=list(tags or []),
                           source=source, ts=M.now(), id=gen_id("exp"))
        self.store.put_experience(exp.dict())
        self.store.log("experience.create", "experience", exp.id,
                       after=exp.dict())
        result = {"experience": exp.dict()}
        if derive_lesson:
            result["lesson"] = self.reflect_on(exp)
        return result

    # ------------------------------------------------------------------ #
    # 2. REFLECT
    # ------------------------------------------------------------------ #
    def reflect_on(self, exp: M.Experience) -> dict:
        """Convert one experience into a lesson (or None if trivial)."""
        if exp.outcome == M.OUTCOME_FAIL and exp.error:
            stmt = f"Avoid: {exp.action} failed ({exp.error}). {exp.fix or 'Apply the fix and verify.'}"
        elif exp.outcome == M.OUTCOME_OK and exp.verdict:
            stmt = f"Do: {exp.action} works when {exp.verdict}"
        elif exp.outcome == M.OUTCOME_OK:
            return {"lesson_id": None, "created": False,
                    "reason": "successful action with no transferable insight recorded"}
        else:
            stmt = f"Avoid: {exp.action} caused a failure"
        lesson = self._upsert_lesson_by_statement(
            statement=stmt,
            detail=exp.fix or exp.verdict or exp.detail,
            category=exp.category,
            tags=exp.tags,
            source=exp.source,
            context=f"Trigger: {exp.action}",
            outcome=exp.outcome,
        )
        # link
        exp.lesson_id = lesson["id"]
        self.store.put_experience(exp.dict())
        return {"lesson_id": lesson["id"], "created": lesson["_created"],
                "lesson": lesson}

    def reflect_session(self, *, session_label="", outcome=M.OUTCOME_OK,
                        what_worked="", what_failed="", fix="", tags=None,
                        category="general") -> dict:
        """High-level reflection pass over a completed task/session."""
        produced = []
        if what_worked:
            lsn = self._upsert_lesson_by_statement(
                statement=_to_statement("Do", what_worked),
                detail=what_worked, category=category, tags=tags,
                source=M.SOURCE_SUCCESS, outcome=M.OUTCOME_OK)
            produced.append(lsn["id"])
        if what_failed:
            lsn = self._upsert_lesson_by_statement(
                statement=_to_statement("Avoid", what_failed) +
                          (f". {fix}" if fix else ""),
                detail=f"{what_failed}\nFix: {fix}" if fix else what_failed,
                category=category, tags=tags, source=M.SOURCE_REFLECTION,
                outcome=M.OUTCOME_FAIL)
            produced.append(lsn["id"])
        self.store.log("session.reflect", "session", session_label,
                       after={"produced": produced, "outcome": outcome})
        return {"session": session_label, "produced_lessons": produced,
                "count": len(produced)}

    # ------------------------------------------------------------------ #
    # 3. LEARN (explicit)
    # ------------------------------------------------------------------ #
    def learn(self, *, statement, detail="", category="general", tags=None,
              source=M.SOURCE_DISCOVERY, context="", author="user") -> dict:
        if not statement or not statement.strip():
            raise ValidationError("lesson statement is required")
        return self._create_lesson(
            statement=statement, detail=detail, category=category,
            tags=tags, source=source, context=context, author=author)

    def _create_lesson(self, *, statement, detail="", category="general", tags=None,
                       source=M.SOURCE_REFLECTION, context="", author="engine",
                       identity=None) -> dict:
        lsn = M.Lesson(
            id=gen_id("lsn"), statement=_clean(statement), category=category,
            detail=_clean(detail), tags=[t.lower() for t in (tags or [])],
            source=source, context=context, confidence=0.5,
            times_seen=1, times_validated=(1 if source == M.SOURCE_SUCCESS else 0),
            created=M.now(), updated=M.now(), version=1, author=author)
        self.store.log("lesson.create", "lesson", lsn.id, after=lsn.dict())
        out = lsn.dict()
        self.store.put_lesson(out)
        out["_created"] = True
        return out

    # internal: find-or-create by normalized statement; increments counters.
    def _upsert_lesson_by_statement(self, *, statement, detail, category, tags,
                                    source, context="", outcome=M.OUTCOME_OK) -> dict:
        identity = _clean(statement).lower()
        existing = self._find_by_identity(identity)
        if existing:
            return self._bump(existing, outcome=outcome, source=source)
        # create with a real identity column
        created = self._create_lesson(statement=statement, detail=detail,
                                      category=category, tags=tags, source=source,
                                      context=context)
        # fix identity if not stored
        return created

    def _find_by_identity(self, identity: str):
        for l in self.store.list_lessons():
            # ignore archived
            if l.get("status") in ("archived",):
                continue
            if _clean(l["statement"]).lower() == identity:
                return l
        return None

    def _bump(self, lesson: dict, *, outcome, source) -> dict:
        if lesson.get("protected"):
            raise ProtectedLesson(f"lesson {lesson['id']} is protected")
        l = dict(lesson)
        l["times_seen"] = int(l.get("times_seen", 0)) + 1
        if outcome == M.OUTCOME_OK or source in (M.SOURCE_SUCCESS, M.SOURCE_CORRECTION):
            l["times_validated"] = int(l.get("times_validated", 0)) + 1
        l["updated"] = M.now()
        l["version"] = int(l.get("version", 1)) + 1
        # promote to strong when validated enough times
        if (int(l.get("times_validated", 0)) >= 3 and
                l.get("status") in (M.ACTIVE, M.STRONG)):
            if l["status"] != M.STRONG:
                l["status"] = M.STRONG
                self.store.log("lesson.promote", "lesson", l["id"],
                               before=lesson, after=l)
        self._write_versioned(l, before=lesson)
        return {**l, "_created": False}

    def _write_versioned(self, l: dict, before: dict):
        self.store.log("lesson.update", "lesson", l["id"], before=before, after=l)
        self.store.put_lesson(l)

    # ------------------------------------------------------------------ #
    # 4. RETRIEVE
    # ------------------------------------------------------------------ #
    def retrieve(self, task: str, *, category="", tags=None, limit=8,
                 include_obsolete=False) -> dict:
        """Rank active/strong lessons relevant to a new task."""
        q = _tokens(task)
        qcat = (category or "").lower()
        want_tags = {t.lower() for t in (tags or [])}
        scored = []
        for l in self.store.list_lessons():
            if l.get("status") == M.OBSOLETE and not include_obsolete:
                continue
            if l.get("status") == M.ARCHIVED:
                continue
            if qcat and l.get("category", "").lower() != qcat:
                continue
            # build token set from lesson fields
            ltoks = _tokens(l["statement"] + " " + l.get("category", "") +
                            " " + " ".join(l.get("tags", [])) + " " +
                            l.get("detail", ""))
            overlap = len(q & ltoks)
            tag_boost = len(want_tags & {t for t in l.get("tags", [])})
            conf = float(l.get("confidence", 0.5))
            strong = 0.15 if l.get("status") == M.STRONG else 0.0
            if overlap or tag_boost:
                score = overlap * 2 + tag_boost * 3 + conf * 0.5 + strong
                scored.append((score, l))
        scored.sort(key=lambda x: -x[0])
        # fuzzy fallback: if no token match, use statement similarity
        if not scored:
            for l in self.store.list_lessons():
                if l.get("status") not in (M.ACTIVE, M.STRONG):
                    continue
                sim = SequenceMatcher(None, _clean(task).lower(),
                                      _clean(l["statement"]).lower()).ratio()
                if sim > 0.35:
                    scored.append((sim, l))
            scored.sort(key=lambda x: -x[0])
        top = [l for _, l in scored[:limit]]
        return {"task": task, "matches": top,
                "guidance": self._render_guidance(top, task)}

    def _render_guidance(self, lessons, task) -> str:
        if not lessons:
            return "No stored experience matches this task yet. Proceed with care " \
                   "and record the outcome to build memory."
        lines = ["Relevant experience from persistent memory for: " + task, ""]
        for l in lessons:
            mark = "[STRONG]" if l.get("status") == M.STRONG else "[v]"
            lines.append(f"{mark} {l['statement']}")
            if l.get("detail"):
                lines.append(f"      {l['detail']}")
            tags = " ".join("#" + t for t in l.get("tags", []))
            if tags:
                lines.append(f"      ({tags})")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # 5. CONSOLIDATE / maintain (daily cycle)
    # ------------------------------------------------------------------ #
    def consolidate(self, *, dry_run=False) -> dict:
        """Merge duplicate lessons, update confidence, archive obsolete, promote."""
        lessons = self.store.list_lessons()
        by_identity = {}
        stats = {"duplicates_merged": 0, "confidence_updated": 0,
                 "obsoleted": 0, "promoted": 0, "removed": 0, "dry_run": dry_run}
        kept = []
        for l in lessons:
            if l.get("status") == M.ARCHIVED:
                continue
            if l.get("protected"):
                kept.append(l); continue
            ident = _clean(l["statement"]).lower()
            if ident in by_identity:
                # duplicate -> merge counts into the canonical (highest validated)
                canon = by_identity[ident]
                canon["times_seen"] = int(canon.get("times_seen", 0)) + \
                    int(l.get("times_seen", 0))
                canon["times_validated"] = int(canon.get("times_validated", 0)) + \
                    int(l.get("times_validated", 0))
                canon["updated"] = max(canon.get("updated", 0), l.get("updated", 0))
                stats["duplicates_merged"] += 1
                if not dry_run:
                    self.store.log("lesson.delete", "lesson", l["id"],
                                   before=l)
                    self.store.delete_lesson_row(l["id"])
            else:
                by_identity[ident] = l
                kept.append(l)
        # update confidence from validation ratio and promote
        for l in kept:
            seen = max(int(l.get("times_seen", 0)), 1)
            val = int(l.get("times_validated", 0))
            conf = round(0.3 + 0.7 * (val / (seen + 2)), 3)
            if l.get("status") == M.STRONG:
                conf = max(conf, 0.8)
            if abs(conf - float(l.get("confidence", 0))) > 0.001:
                stats["confidence_updated"] += 1
                l["confidence"] = conf
            if val >= 3 and l.get("status") == M.ACTIVE:
                stats["promoted"] += 1
                l["status"] = M.STRONG
            if not dry_run:
                self.store.put_lesson(l)
        return stats

    def mark_obsolete(self, lesson_id: str, reason: str = "") -> dict:
        l = self.store.get_lesson(lesson_id)
        if not l:
            raise NotFound(f"no lesson {lesson_id}")
        if l.get("protected"):
            raise ProtectedLesson(f"lesson {lesson_id} is protected")
        before = dict(l)
        l["status"] = M.OBSOLETE
        l["meta"] = dict(l.get("meta") or {})
        l["meta"]["obsolete_reason"] = reason
        l["updated"] = M.now()
        l["version"] = int(l.get("version", 1)) + 1
        self._write_versioned(l, before=before)
        return l

    # ------------------------------------------------------------------ #
    # 6. stats / list / delete / export
    # ------------------------------------------------------------------ #
    def stats(self) -> dict:
        lessons = self.store.list_lessons()
        by_status = {}
        for l in lessons:
            s = l.get("status", M.ACTIVE)
            by_status[s] = by_status.get(s, 0) + 1
        return {"lessons_total": len(lessons), "by_status": by_status,
                "experiences": len(self.store.list_experiences(limit=100000)),
                "head_version": self.store.get_kv("head_version")}

    def list_lessons(self, status=None, category=""):
        lessons = self.store.list_lessons()
        out = []
        for l in lessons:
            if status and l.get("status") != status:
                continue
            if category and l.get("category", "").lower() != category.lower():
                continue
            out.append(l)
        return out

    def get_lesson(self, lesson_id):
        return self.store.get_lesson(lesson_id)

    def delete_lesson(self, lesson_id):
        """Archive (reversible) rather than hard-delete protected-free lessons."""
        l = self.store.get_lesson(lesson_id)
        if not l:
            raise NotFound(f"no lesson {lesson_id}")
        if l.get("protected"):
            raise ProtectedLesson(f"lesson {lesson_id} is protected")
        before = dict(l)
        l["status"] = M.ARCHIVED
        l["updated"] = M.now()
        l["version"] = int(l.get("version", 1)) + 1
        self._write_versioned(l, before=before)
        return {"archived": True, "lesson_id": lesson_id}

    def undo(self):
        return self.store.undo_last()

    # ------------------------------------------------------------------ #
    # 7. Improvement mode (cloud vs local) - thin wrappers over mode module
    # ------------------------------------------------------------------ #
    @property
    def mode(self) -> str:
        """'cloud' (memory only) or 'local' (memory + local model improvement)."""
        from . import mode as MO
        return MO.get_mode(self.store)

    def set_mode(self, mode: str) -> dict:
        from . import mode as MO
        return MO.set_mode(self.store, mode)

    def local_model(self) -> dict:
        from . import mode as MO
        return MO.get_local_model(self.store)

    def set_local_model(self, *, model="", base_model="") -> dict:
        from . import mode as MO
        return MO.set_local_model(self.store, model=model,
                                  base_model=base_model)


# ---------------------------------------------------------------------- #
def _clean(s) -> str:
    return " ".join(str(s or "").strip().split())


def _tokens(s) -> set:
    toks = set(re.findall(r"[a-z0-9_\-]{2,}", str(s).lower()))
    stop = {"the", "and", "for", "this", "that", "with", "from", "when", "what",
            "how", "why", "did", "was", "are", "not", "you", "your", "task",
            "about", "into", "have"}
    return toks - stop


def _to_statement(prefix, text) -> str:
    return f"{prefix}: {_clean(text)}"
