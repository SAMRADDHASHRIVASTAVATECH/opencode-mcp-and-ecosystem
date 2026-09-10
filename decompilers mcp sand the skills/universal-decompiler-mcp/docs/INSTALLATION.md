# On-demand installation
Use `find_tools_for_capability`, `plan_install_tool`, inspect source/version/argv/network/code-execution impact, approve, execute and then `verify_tool`. Managed packages go only under `DECOMPILER_TOOL_ROOT/installed`.

System packages and large release archives are deliberately manual unless a platform-specific pinned checksum recipe exists. This avoids silently downloading and executing moving GitHub releases. Offline mode continues with installed tools and reports exact missing capabilities.
