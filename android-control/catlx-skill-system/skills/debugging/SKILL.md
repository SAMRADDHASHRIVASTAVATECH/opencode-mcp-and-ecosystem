---
name: debugging
description: Diagnoses build, test, and runtime failures. Use when commands fail, tests go red, or the user pastes a stack trace.
---

# Debugging

1. Capture the **full** error (`se_diagnose` on the log).
2. Reproduce with the smallest command.
3. Classify: missing toolchain, dependency, logic, permissions, network, Android SDK, SQL policy.
4. Fix the cause, not the symptom (don't `except: pass`).
5. Re-run the same command.

Android crashes → `android_analyze_crash` / logcat.  
Gradle SDK errors → `android_analyze_build_failure`.  
SQL refused → Database MCP policy, not "the query is wrong" if it was `DROP DATABASE`.  
Windows printers → `win_diagnose_printer`.
