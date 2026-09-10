# Security review

Trust boundaries: MCP client, host platform CLI, guest control endpoint, guest OS. The server never elevates privileges, bypasses authentication, disables host-key verification, exposes raw QMP, or accepts unrestricted host commands. Inputs are allowlisted and passed without a shell. Exact approval plans expose target VM, context, action/argv, affected files, resources, persistence, data-loss potential, mechanism and verification.

Credentials must remain outside arguments and logs. Use authorized SSH agents/key paths, strict known-hosts, or protected VirtualBox password files. Never pass passwords, tokens, or private key material. Redaction cannot reliably recognize every secret, so callers must not submit them.

Known limits: process-local approvals/jobs; SIGTERM cancellation may not stop grandchildren created by a native CLI; output truncation; TCP readiness is not authentication; no transactional rollback. Use disposable VMs and snapshots, independently verify state, and treat force poweroff, unregister, snapshot restore/delete, import/export, software changes, and network/security changes as consequential.
