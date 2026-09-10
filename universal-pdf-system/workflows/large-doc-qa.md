# Workflow: Large-document Q&A with citations (10,000+ pages)

**Goal:** answer questions about a very large PDF without ever loading it into a
model context, citing the page of every claim.

**Skills:** `pdf-document-state` (register+persist) → `pdf-chunk` →
`pdf-search`/`pdf-index` → `pdf-qa` → `pdf-provenance`.

## Steps
1. **Register** the document → stable `document_id`.
2. **Chunk & persist** page text + chunks into the SQLite knowledge store
   (one page at a time, resumable with a checkpoint).
3. (Optional) **build an index** for faster term retrieval.
4. **QA**: retrieve the few most relevant chunks by lexical overlap with the
   question, hand *only those* to the reasoning provider, require `[page N]`
   citations.
5. If no reasoning model is wired, return retrieved evidence + citations
   (degraded, never fabricated).

## Concrete calls
```python
from universal_pdf.core import state, chunk, qa, checkpoint

store = state.DocumentStore("knowledge/store.db")
did = store.register_document("huge.pdf")     # or reuse an existing id

ck = checkpoint.Checkpoint("knowledge/_chunk_ck.json")
def persist_page(page_no):                     # resumable per-page persist
    # page text already cached via chunk_document below; use chunk_document
    pass
chunk.chunk_document("huge.pdf", store_doc_id=did, page_store=store, per_page=True)

def model(prompt):            # your local/remote LLM callable
    return llm_generate(prompt)  # weak models OK: prompt is small & bounded

ans = qa.answer(did, "What is the refund policy for damaged goods?",
                store=store, reasoning=model)
print(ans.data["answer"])       # includes [page N] citations
print([c["page"] for c in ans.data["citations"]])
```
No sub-step passes more than a bounded context to the model. Re-running resumes
from the checkpoint instead of re-parsing the whole file.
