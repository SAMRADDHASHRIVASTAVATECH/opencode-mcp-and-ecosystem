# Known limitations & graceful-degradation map

The system is honest about what a general-purpose PDF stack can and cannot do.
Where a capability is limited, the relevant skill degrades (a `degraded`/`failed`
`Outcome` with a message) rather than reporting a false success.

## Functional limits (PDF-format realities)
- **True in-place content editing is limited.** PDFs store positioned content;
  arbitrarily re-flowing an existing paragraph is not generally possible.
  `pdf-edit` therefore uses *safe reconstruction/overlay* (delete + re-insert,
  watermark-style overlays) and documents this.
- **PDF → DOCX** cannot be authored faithfully from arbitrary PDFs by the
  default backends. It degrades unless `pandoc` is available (then routed via
  Markdown). Complex re-flow conversions (PDF→PPTX etc.) are **not** supported.
- **HTML → PDF** uses a pragmatic tag subset (headings/p/li/tables/img/links).
  Pixel-perfect complex HTML/CSS requires a browser engine and is out of scope;
  this is documented on the skill.
- **Redaction** removes underlying text where tooling supports true redaction
  (PyMuPDF `apply_redactions`) and then *verifies* no leaked term is selectable.
  Very complex overlapping vector graphics may not be fully removed in all edge
  cases — the leak check reports any residual text.
- **Digital signatures** are inspected at the field level. The default
  `pdf-sign` places a *visible* signature (image/stylized text) and clearly
  warns it is **not** a cryptographic PKCS#7 signature. Real cert-based signing
  requires external signing infrastructure (documented on the skill).
- **Compression** gives real size savings via structural cleanup + native image
  recompression. If the backend lacks image recompression it degrades to
  structural-only and reports savings honestly.

## Environment-dependent capabilities
| Capability | Default backend | When unavailable |
|---|---|---|
| Vision (interpret charts/images) | pluggable vision provider | skill returns `degraded` and relies on text/OCR |
| OCR / searchable layer | `ocrmypdf`; page text via tesseract | `degraded` with install instructions |
| PDF→DOCX | pandoc | `degraded` limitation |
| XLSX export | openpyxl | `degraded` message to install it |

## Scale notes
- Streaming extraction/mention-scan was verified on an 8,192-page PDF, holding
  one page in memory at a time (~29 s full scan on the test host). Genuinely
  10,000+ page files work but full scans are linear in page count.
- Whole-document abstractive operations always pass through chunking / bucket
  summaries; the engine never fills an LLM context with the whole file.

## Security / ethics note
Encryption, permission changes, redaction and signing must be applied only to
documents you own or are authorized to process.
