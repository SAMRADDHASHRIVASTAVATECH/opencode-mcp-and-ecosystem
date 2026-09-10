from __future__ import annotations

from android_mcp.mcp_compat import create_mcp
from android_mcp.tools import register

INSTRUCTIONS = """\
Android Application Development MCP — standalone specialist for the app lifecycle.

Always call android_detect_environment (or android_plan) before build/device work.
This host may lack JDK 17 / Android SDK; scaffolding, inspect, security audit, and
crash/build-log analysis still work. Device/emulator/Gradle fail with DEPENDENCY_MISSING
and install hints instead of pretending.

Create: android_create_project (compose-app default, Kotlin DSL + version catalog).
Do not run unbounded adb shell. Mutations like install APK need confirm=true.
"""

mcp = create_mcp("android-development", INSTRUCTIONS)
register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
