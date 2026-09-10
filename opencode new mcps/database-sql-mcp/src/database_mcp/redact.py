from __future__ import annotations

import re

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

_PW = re.compile(r"(://[^:/?#]+):([^@/]+)@")


def redact_url(url: str) -> str:
    try:
        u = make_url(url)
        return u.render_as_string(hide_password=True)
    except ArgumentError:
        return _PW.sub(r"\1:***@", url)


def redact_error(msg: str) -> str:
    return _PW.sub(r"\1:***@", msg)
