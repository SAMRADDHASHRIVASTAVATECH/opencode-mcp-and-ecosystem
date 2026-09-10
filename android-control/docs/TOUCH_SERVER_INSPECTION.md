# Inspection: 62Bytes / Touch-Server (Touch — A PC Controller)

Date of inspection: 2026-09-07
Sources inspected:
- `https://github.com/62Bytes/Touch-Server` (cloned)
- `https://github.com/62Bytes/Touch-Client` (companion Android app)

## Purpose of the upstream project
"Touch — A PC Controller": an Android app (**Touch-Client**) that connects to a
Windows PC running **Touch-Server** over **Wi-Fi or USB-tethering** and lets the
**phone control the PC** (mouse, media/YouTube, slide shows, and layouts for
specific games — GTA V, Red Dead Redemption 2, Watch Dogs 2, plus optional
Xbox360 emulation via ViGEm).

## What is actually in the repository
Both `Touch-Server` and `Touch-Client` repos contain **only** `README.md` and
`LICENSE` (MIT). They are issue/release trackers, not source distributions:
- `Touch-Server`: 2 commits, ~136 KB total, no code.
- The Windows server is a closed, prebuilt `TouchServer.exe`.
- The Android client is a closed Play Store APK.

There is **no source code, no protocol spec, and no programmatic/agent API** to
reuse or embed.

## Evaluation against the scoped requirements
| Requirement (this system) | Provided by Touch-Server? |
|---|---|
| Windows agent → controls Android devices | **No — direction is reversed** (Android controls Windows) |
| View/stream Android screen on Windows | No |
| Touch/mouse on the Android device | No (it injects into the PC) |
| Keyboard into the Android device | No |
| File transfer both directions | No |
| Agent messaging | No |
| Multiple Android devices | No (single client → single server) |
| Clean agent-callable interface | No (manual GUI layouts/keymaps) |
| Source embeddable as a skill | No (closed binaries, no code) |

## Security note
The upstream README explicitly warns the data transfer is **not encrypted** and
should only be used on a trustworthy Wi-Fi network. That is a significant
concern for an agent-facing control channel and further argues against adopting
it as-is.

## Conclusion
Touch-Server is not a suitable base and cannot be "converted to an embedded
skill" of this system: it is the wrong direction (phone→PC), closed-source, and
lacks the required capabilities. Reused substrate for the Windows-agent→Android
direction remains **ADB (+ scrcpy for streaming)**, which `android-control`
already wraps. The one scoped capability absent from `android-control` —
**agent messaging** — has been added separately (see `engines/message.py`,
`high.AndroidFacade.send_message/receive_messages`).
