# Security model

The system is an autonomous operator over real phones, so it is built to avoid
unintended targets, unauthorised destructive actions, credential leakage, and
network exposure.

## Device targeting (never the wrong phone)
- Every low-level command carries an explicit device target when the fleet has
  more than one device (§9).
- Device identity is kept as rich identifiers (serial, model, manufacturer,
  android_id, ip/port), **not** "Phone 1"/"Phone 2".
- Natural-language selection is resolved to deterministic `device_id`s before
  execution and **raises on ambiguity instead of guessing** (§28,
  `AmbiguousDeviceError`). A target that matches nothing raises
  `UnknownDeviceError`.

## Command safety (§27)
- Every command is associated with target device, operation, arguments,
  timeout, and (at the facade) a verification method.
- Free-form `shell()` runs through `safe_shell_command`, which refuses
  destructive host-affecting patterns (`rm -rf /`, `mkfs.`, `dd if=`,
  `/dev/` writes, fork bombs).
- `files` uses path normalisation that rejects `..` traversal.

## Destructive operations (§27, §37)
`uninstall`, `clear data`, `disable`, and host/device overwrites go through an
**authorizer**. The default policy denies (raises
`RequiresAuthorizationError`). To permit any, pass a policy
(`authorizer=lambda op, detail: …`). `AC_REQUIRE_AUTH_DESTRUCTIVE=false`
should only be used in a tightly controlled test lab.

## Network exposure (§20, §37)
- Wireless control prefers **authenticated Wireless Debugging** pairing
  (`adb pair`), which requires the six-digit code from the phone — not an
  unauthenticated service.
- No adb server port is exposed publicly; only the device-facing wireless
  debugging connection is used. We do not add firewall rules.
- No arbitrary remote shell / inbound TCP is opened by this package.

## Credentials & logs (§33)
- Secrets (pairing codes, keys) are never stored. Structured logs carry
  timestamp, device_id, operation, command, result, duration, verification,
  error, recovery — and `logging.redact()` scrubs obvious secrets from command
  text before it is written.
- `Settings.to_dict()` does not expose path secrets.

## Human-in-the-loop (§38)
The agent minimises human involvement, but when Android security requires it
(pairing confirmation, permission dialogs, unlock, OS restrictions, or explicit
destructive authorization) the system **stops at the exact required step,
explains it, waits, detects completion, then continues automatically** — it
does not ask a human to do things the system can do itself.

## Failure isolation (§25, §21)
A device going offline or rebooting is recovered independently and never
crashes or corrupts the other sessions.
