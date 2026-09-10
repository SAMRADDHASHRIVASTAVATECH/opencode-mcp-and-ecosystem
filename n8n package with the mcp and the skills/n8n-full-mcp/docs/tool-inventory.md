# Tool inventory

## Instance and control
`n8n_status`, `n8n_capabilities`, `official_mcp_tools`, `n8n_diagnose`, `operation_plan`, `operation_approve`.

## Workflow lifecycle/intelligence
`workflow_list`, `workflow_get`, `workflow_validate`, `workflow_analyze`, `workflow_compare`, `workflow_draft_from_description`, `workflow_create`, `workflow_update`, `workflow_delete`, `workflow_activate`, `workflow_deactivate`, `workflow_execute`, `workflow_test`.

## Executions
`execution_list`, `execution_get`, `execution_retry`, `execution_stop`, `execution_delete`.

## Other resources
`resource_list` for credentials/projects/tags/variables/data tables/users/community packages/folders. `resource_mutate` for approval-gated projects/tags/variables/data tables/community packages/folders.

Official n8n's entire evolving catalog is preserved through `official_mcp_tools` discovery and preferred adapter calls for mapped operations. Agent/node/data-table builder functionality should use the official catalog directly when available rather than stale duplicate schemas.
