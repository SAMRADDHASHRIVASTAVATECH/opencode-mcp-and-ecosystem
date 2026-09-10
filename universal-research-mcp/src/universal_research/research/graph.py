"""Knowledge graph (#40, #41). Nodes: question/subquestion/claim/evidence/
source/entity/term. Edges with typed relations."""
from __future__ import annotations

from ..models import Node, Edge, new_id


class KnowledgeGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, kind: str, label: str, data: dict = None,
                 node_id: str = "") -> str:
        if node_id and node_id in self.nodes:
            return node_id
        node_id = node_id or new_id(f"n_{kind[:3]}")
        self.nodes[node_id] = Node(id=node_id, kind=kind, label=label,
                                   data=data or {})
        return node_id

    def add_edge(self, src: str, dst: str, rel: str, weight: float = 1.0,
                 data: dict = None) -> str:
        if src not in self.nodes or dst not in self.nodes:
            return ""
        self.edges.append(Edge(src=src, dst=dst, rel=rel, weight=weight,
                               data=data or {}))
        return f"{src}->{dst}:{rel}"

    def upsert_source(self, url: str, title: str = "") -> str:
        for nid, n in self.nodes.items():
            if n.kind == "source" and n.data.get("url") == url:
                return nid
        return self.add_node("source", title or url, {"url": url})

    def relations_for(self, kind: str, label: str) -> list[str]:
        """All typed edges touching a node whose kind+label match."""
        ids = {nid for nid, n in self.nodes.items()
               if n.kind == kind and n.label == label}
        return [f"{e.src}:{e.rel}->{e.dst}" for e in self.edges
                if e.src in ids or e.dst in ids]

    def neighbors(self, node_id: str) -> list[dict]:
        out = []
        for e in self.edges:
            if e.src == node_id:
                out.append({"id": e.dst, "rel": e.rel,
                            "label": self.nodes[e.dst].label if e.dst in self.nodes else "",
                            "kind": self.nodes[e.dst].kind if e.dst in self.nodes else ""})
            elif e.dst == node_id:
                out.append({"id": e.src, "rel": e.rel,
                            "label": self.nodes[e.src].label if e.src in self.nodes else "",
                            "kind": self.nodes[e.src].kind if e.src in self.nodes else ""})
        return out

    def export(self) -> dict:
        return {"nodes": [n.to_dict() for n in self.nodes.values()],
                "edges": [e.to_dict() for e in self.edges],
                "n_nodes": len(self.nodes), "n_edges": len(self.edges)}

    def stats(self) -> dict:
        kinds = {}
        for n in self.nodes.values():
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
        rels = {}
        for e in self.edges:
            rels[e.rel] = rels.get(e.rel, 0) + 1
        return {"node_kinds": kinds, "edge_relations": rels,
                "n_nodes": len(self.nodes), "n_edges": len(self.edges)}
