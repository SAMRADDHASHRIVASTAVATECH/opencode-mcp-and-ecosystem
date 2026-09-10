---
name: virtualization-master
description: Safely reason about and operate VMs through the virtualization-master MCP with explicit HOST/GUEST context, exact approval, readiness checks, and independent verification.
---
# Virtualization Master

1. Call `list_virtualization_platforms`; do not infer installation from documentation.
2. Call `list_vms`; if zero or multiple targets match, stop and request an exact platform and VM. Never guess.
3. Call `get_vm_capabilities`. Separate Level 1 host lifecycle from Level 2 guest operations.
4. For guest work, establish that the VM is powered on, then independently establish endpoint/control readiness with `wait_for_vm` and a harmless authenticated guest probe. Discover OS, shell, filesystem conventions, package manager, service manager, privileges and Internet availability before planning changes.
5. Create one structured `plan_operation`. Ensure the plan names HOST/GUEST context, target, exact argv/action, files, resource changes, persistent effects, data-loss potential, mechanism and verification. Reject mismatches.
6. Explain the plan and request explicit user approval. Only then call `approve_operation`, immediately followed by `execute_operation` with the returned short-lived token.
7. Poll `get_job`; inspect exit code and bounded stdout/stderr. Do not equate command issuance or exit zero with success. Re-list VM state or run operation-specific guest checks.
8. Diagnose with `diagnose_virtualization` by layer: host/platform, VM power/configuration, network endpoint, authentication/control mechanism, guest OS, application.

For software workflows: detect package manager, assess guest Internet requirements, snapshot when appropriate, transfer/create files through an approved guest mechanism, install dependencies with approval, run bounded build/tests, expose services deliberately, and verify from the intended network boundary. Never weaken authentication, firewalling, isolation, licensing, or guest/host security. Never submit secrets to tool arguments. Use disposable VMs for destructive testing.

If a requested operation is not accepted by `plan_operation`, report it as unsupported rather than inventing a command or using a host shell.
