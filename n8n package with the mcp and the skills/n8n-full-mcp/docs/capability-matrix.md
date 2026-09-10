# Capability gap matrix

| Capability | Official MCP | Public API | Local/offline | New extension | Status |
|---|---|---|---|---|---|
| Instance status/capabilities | Tool catalog/scopes | Endpoint/version dependent | config/artifacts | normalized registry, backend report | Implemented |
| Workflow list/search/get | Yes | Yes | JSON artifacts | semantic analysis | Implemented |
| Create/update | SDK code + atomic partial update (version-gated) | Yes | JSON create/replace | local validation/diff/approval | Implemented; official preferred |
| Publish/archive | Yes | API lifecycle endpoints | archive by file policy only | approval routing | Implemented where backend supports |
| Delete/activate/deactivate | partial official coverage | Yes | delete; active is artifact data | semantic tools + gate | Implemented with explicit backend errors |
| Execute/manual/production | Yes, exposed workflows | API varies | no live execution | approval + side-effect summary | Official route implemented |
| Test/pin data | 2.15+ | not equivalent | local structural validation only | safe-design warnings | Official route + offline validation |
| Node search/types/resources | Yes, version gated | internal/public availability varies | workflow JSON only | graph/expression analysis | Official + extension |
| Workflow node mutation | Atomic `update_workflow` | full workflow PUT | JSON replace | compare/validate | Live replace implemented; official atomic evolution delegated |
| Executions list/get | Yes | Yes | no execution engine | normalized diagnosis | Implemented |
| Retry/stop/delete execution | official varies | Yes | no | approval + duplicate-effect warning | REST route implemented |
| Data tables | search/create and current official tools | full table/row CRUD | artifact only | semantic resource route | REST/official discovery and mutations; instance capability decides |
| Credentials | metadata only; never secrets | schema/create/delete where scoped | references only | secret rejection/redaction | Safe metadata implemented; secrets delegated to n8n UI/API policy |
| Variables/tags/folders/projects | some current MCP tools | broad API | package metadata | generic semantic resource tools | Implemented where endpoint exists |
| Users/roles/permissions | scopes constrain MCP | API/enterprise dependent | no | report only | Read route; no fabricated admin endpoint |
| Community packages | not primary official MCP | API/self-hosted availability | installed local n8n only | approval-gated API route | Implemented where supported |
| Agents/AI assets | 2.34+ preview; call 2.35+ | evolving | workflow JSON analysis | capability reporting | Official passthrough via catalog, not duplicated |
| Backup/export/compare/document | package/export features | package/workflow API | JSON/n8np artifacts | compare/analyze | Compare/analyze implemented; backups are artifact operations |
| Cross-backend fallback | No need inside n8n MCP | N/A | artifacts | official → REST → offline | Implemented per operation |
| Approval | n8n permissions/consent | scopes | none | exact-plan, expiring, one-use | Implemented |
