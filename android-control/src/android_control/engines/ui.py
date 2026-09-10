"""Semantic UI control engine (§13–14).

Where UI hierarchy / accessibility data is available we prefer semantic
targeting (text, resource-id, content-desc, class, bounds) over raw
coordinates. A vision/coordinate fallback is wired at a higher layer.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

from .. import errors
from ..config import Settings
from .base import EngineBase
from .input import InputEngine


class UINode:
    def __init__(self, attrs: Dict[str, str], depth: int = 0):
        self.text = attrs.get("text", "")
        self.resource_id = attrs.get("resource-id", "")
        self.content_desc = attrs.get("content-desc", "")
        self.class_ = attrs.get("class", "")
        self.package = attrs.get("package", "")
        self.checkable = attrs.get("checkable") == "true"
        self.clickable = attrs.get("clickable") == "true"
        self.enabled = attrs.get("enabled") == "true"
        self.focused = attrs.get("focused") == "true"
        self.selected = attrs.get("selected") == "true"
        self.visible = attrs.get("visible-to-user", "true") == "true"
        self.scrollable = attrs.get("scrollable") == "true"
        self.editable = attrs.get("editable") == "true" or \
            "EditText" in self.class_
        self.password = attrs.get("password") == "true"
        self.bounds = _parse_bounds(attrs.get("bounds", ""))
        self.depth = depth
        self.index = attrs.get("index", "")
        self.children: List["UINode"] = []

    @property
    def center(self) -> tuple:
        (x0, y0), (x1, y1) = self.bounds
        return (x0 + x1) // 2, (y0 + y1) // 2

    def semantic_text(self) -> str:
        return (self.text or self.content_desc or "").strip()

    def to_dict(self) -> dict:
        return {"text": self.text, "resource_id": self.resource_id,
                "content_desc": self.content_desc, "class": self.class_,
                "package": self.package, "clickable": self.clickable,
                "enabled": self.enabled, "focused": self.focused,
                "selected": self.selected, "editable": self.editable,
                "scrollable": self.scrollable, "bounds": self.bounds,
                "center": list(self.center) if self.bounds else [],
                "index": self.index}


def _parse_bounds(b: str):
    m = re.match(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]", b)
    if not m:
        return (0, 0), (0, 0)
    x0, y0, x1, y1 = (int(g) for g in m.groups())
    return (x0, y0), (x1, y1)


def _flatten(node: UINode) -> List[UINode]:
    out = [node]
    for c in node.children:
        out.extend(_flatten(c))
    return out


class UIEngine(EngineBase):
    def __init__(self, transport, settings: Settings, input_engine: InputEngine):
        super().__init__(transport, settings)
        self.input = input_engine

    # -- hierarchy ---------------------------------------------------------
    def hierarchy(self, serial: str, refresh: bool = True) -> UINode:
        """Dump and parse the accessibility window hierarchy into UINodes."""
        # Push uiautomator dump to a file then cat (robust to stdout limits).
        cmd = ("uiautomator dump /sdcard/ui.xml && cat /sdcard/ui.xml")
        res = self._shell(serial, cmd, timeout_s=self.settings.uiauto_timeout_ms // 1000 + 5)
        if not res.ok or "<hierarchy" not in res.stdout:
            # Fallback to stdout dump on some devices
            res = self._shell(serial, "uiautomator dump",
                              timeout_s=self.settings.uiauto_timeout_ms // 1000 + 5)
        xml = _strip_ui_prefix(res.stdout)
        if "<hierarchy" not in xml:
            raise errors.UnsupportedOperationError(
                f"UI hierarchy not available on {serial}")
        root = ET.fromstring(xml)
        return _parse_hierarchy(root)

    def tree(self, serial: str) -> List[dict]:
        root = self.hierarchy(serial)
        return [n.to_dict() for n in _flatten(root)]

    # -- finding -----------------------------------------------------------
    def find(self, serial: str, *, text: Optional[str] = None,
             resource_id: Optional[str] = None,
             content_desc: Optional[str] = None,
             cls: Optional[str] = None,
             text_contains: Optional[str] = None) -> List[UINode]:
        """Find nodes matching semantic criteria (substring tolerated for
        text/id/desc). Returns only enabled, visible nodes by default."""
        root = self.hierarchy(serial)
        found = []
        for n in _flatten(root):
            if not (n.enabled and n.visible):
                continue
            if text is not None and n.text != text:
                continue
            if text_contains is not None and text_contains not in n.text:
                continue
            if resource_id is not None and n.resource_id != resource_id:
                # accept suffix match for common ids
                if not n.resource_id.endswith(resource_id):
                    continue
            if content_desc is not None and content_desc not in n.content_desc:
                continue
            if cls is not None and cls not in n.class_:
                continue
            found.append(n)
        return found

    def find_one(self, serial: str, **kw) -> UINode:
        found = self.find(serial, **kw)
        if not found:
            raise errors.CommandFailedError(
                f"no UI element matched criteria on {serial}")
        # prefer the shallowest / smallest clickable match
        found.sort(key=lambda n: (n.depth, _area(n)))
        return found[0]

    def click_element(self, serial: str, **kw) -> None:
        """Click the first matching semantic element (or its clickable parent)."""
        node = self.find_one(serial, **kw)
        target = node if node.clickable else _closest_clickable(node)
        x, y = target.center
        self.input.tap(serial, x, y)

    def type_into(self, serial: str, text: str, **kw) -> None:
        """Focus an editable field and type text into it (semantically)."""
        node = self.find_one(serial, **kw)
        if not node.editable:
            # some nodes lack the flag; tap anyway then type
            pass
        x, y = node.center
        self.input.tap(serial, x, y)
        self.input.text(serial, text)

    def read_text(self, serial: str) -> List[str]:
        root = self.hierarchy(serial)
        seen = []
        for n in _flatten(root):
            t = n.semantic_text()
            if t and t not in seen:
                seen.append(t)
        return seen

    def scroll_to(self, serial: str, max_swipes: int = 6, **kw) -> bool:
        """Swipe-scroll until a matching element appears or max_swipes reached."""
        for _ in range(max_swipes):
            found = self.find(serial, **kw)
            if found:
                return True
            self.input.scroll(serial, "down", steps=2)
        return bool(self.find(serial, **kw))


def _area(n: UINode) -> int:
    (x0, y0), (x1, y1) = n.bounds
    return max(1, (x1 - x0) * (y1 - y0))


def _closest_clickable(node: UINode) -> UINode:
    cur = node
    # walk up through stored parents isn't available; approximate by re-dumping
    # parents is costly, so return the node itself if clickable else nearest.
    # We keep a parent pointer during parse instead:
    p = getattr(node, "_parent", None)
    while p is not None:
        if p.clickable:
            return p
        p = getattr(p, "_parent", None)
    return node


def _parse_hierarchy(root) -> UINode:
    top = root[0] if len(root) else root
    node = _node_from_et(top, depth=0)
    return node


def _node_from_et(el: ET.Element, depth: int, parent=None) -> UINode:
    n = UINode(el.attrib, depth=depth)
    n._parent = parent  # type: ignore[attr-defined]
    for child in list(el):
        n.children.append(_node_from_et(child, depth + 1, n))
    return n


def _strip_ui_prefix(xml: str) -> str:
    """Some builds emit XML with a leading filename line; uiautomator prints
    'UI hierchary dumped to: ...' then the xml on stdout. Take from the first
    '<' onward."""
    i = xml.find("<")
    if i > 0:
        xml = xml[i:]
    # drop any windows line-noise before first tag and rewind
    return xml


class UIHNode(UINode):
    pass
