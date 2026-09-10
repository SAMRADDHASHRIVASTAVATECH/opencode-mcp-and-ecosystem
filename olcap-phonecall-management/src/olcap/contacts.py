"""Contact resolver + context (spec sections 3, 5, caller information).

On-device, this is backed by Android ContactsContract via the bridge. In this
portable core we provide a deterministic lookup table (seeded from config/env)
and explicit ambiguity handling: if a name resolves to multiple contacts, we ask
for confirmation rather than guessing - never send a call to the wrong target.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class Contact:
    contact_id: str
    name: str
    numbers: list
    email: str = ""
    org: str = ""
    note: str = ""

    def dict(self):
        return {"contact_id": self.contact_id, "name": self.name,
                "numbers": self.numbers, "email": self.email, "org": self.org,
                "note": self.note}


class AmbiguousContact(Exception):
    def __init__(self, candidates):
        super().__init__("contact name is ambiguous; requires explicit confirmation")
        self.candidates = candidates


class ContactResolver:
    def __init__(self, provider=None):
        # provider may be an Android bridge with search_contacts(); if absent we
        # use a small local seed table for deterministic testing.
        self.provider = provider
        self._seed = self._load_seed()

    @staticmethod
    def _load_seed():
        raw = os.environ.get("OLCAP_CONTACTS")
        if raw:
            try:
                data = json.loads(raw)   # list of {id,name,numbers,...}
                return {c["contact_id"]: Contact(**{k: c.get(k, "") for k in
                       ("contact_id", "name", "numbers", "email", "org", "note")})
                        for c in data}
            except Exception:
                pass
        return {}

    def _all(self):
        if self.provider is not None and hasattr(self.provider, "contacts"):
            return self.provider.contacts()
        return list(self._seed.values())

    def search(self, query: str):
        q = query.strip().lower()
        out = []
        for c in self._all():
            name = c.name.lower()
            if q in name or any(q in normalize(n) for n in c.numbers):
                out.append(c.dict())
        return out

    def lookup_contact(self, name_or_number: str):
        """Resolve to a single contact. Raises AmbiguousContact when the name maps
        to multiple contacts. A number match returns the unique owner."""
        q = name_or_number.strip()
        hits = []
        for c in self._all():
            if any(normalize(n) == normalize(q) for n in c.numbers):
                return c.dict()          # exact number -> unique owner
            if c.name.lower() == q.lower():
                hits.append(c)
            elif q.lower() in c.name.lower():
                hits.append(c)
        if len(hits) == 1:
            return hits[0].dict()
        if len(hits) > 1:
            raise AmbiguousContact([c.dict() for c in hits])
        return None

    def identify_caller(self, number: str):
        for c in self._all():
            if any(normalize(n) == normalize(number) for n in c.numbers):
                return c.dict()
        return None

    def context(self, name_or_number: str):
        c = self.lookup_contact(name_or_number)
        if not c:
            return {"contact": None, "context": "unknown contact"}
        # Context is whatever authorised data is available on this device
        # (notes, org, recent interactions). Kept minimal & local.
        return {"contact": c,
                "context": f"{c['name']}" + (f", {c['org']}" if c["org"] else "")}


def normalize(n):
    import re
    return re.sub(r"[\s\-()]", "", n or "")
