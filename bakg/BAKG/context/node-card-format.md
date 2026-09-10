# Node Card Format

Use this template when adding any new node to BAKG (the graph is designed to be extended). The same format is how existing domain knowledge is read.

```
### [NODE NAME]  [STATUS: REQ/OPT/SIT/ADV]
**DEF:** one-sentence definition
**WHY:** why it exists
**HOW:** mechanism (2–4 lines)
**USE:** when to use / **AVOID:** when not to
**OPT:** available options
**ALT:** alternatives
**PRO / CON:** advantages / disadvantages
**PRE:** prerequisites · **DEP:** dependencies
**AFF:** what it affects · **AFF-BY:** what affects it
**PARAM:** key parameters/settings
**FLOW:** workflow steps
**MIST:** common mistakes
**FAIL:** failure modes · **DIAG:** how to diagnose · **FIX:** fixes
**PERF:** optimization
**BEG / INT / ADV:** level knowledge
**PROD:** production considerations
**EDGES:** related nodes (inbound/outbound)
```

When a skill answers a user question, it should speak in this structure (at least DEF, WHY, HOW, USE/AVOID, PARAM, FLOW, FAIL/FIX, EDGES) so the user always gets: what it is, why it exists, how it works, when to use it, what can fail, and how to fix it.
