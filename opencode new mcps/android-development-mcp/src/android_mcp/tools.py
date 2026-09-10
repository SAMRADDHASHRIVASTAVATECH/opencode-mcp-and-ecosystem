"""Semantic Android MCP tools."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from android_mcp.components import KINDS, create_component
from android_mcp.config import SETTINGS
from android_mcp.diagnostics import analyze_build_log, analyze_crash
from android_mcp.env import detect, require_adb
from android_mcp.errors import DependencyMissing, NotFoundError, PolicyError, ValidationError
from android_mcp.gradle_adb import (
    GRADLE_TASKS,
    adb,
    gradle,
    inspect_apk,
    list_avds,
    list_devices,
    pick_serial,
    start_avd,
)
from android_mcp.inspect import find_root, inspect_project
from android_mcp.manifest_edit import modify_manifest
from android_mcp.results import run
from android_mcp.runner import run_cmd
from android_mcp.scaffold import TEMPLATES, create_project
from android_mcp.security import check_shell, check_overwrite, ensure_writable, require_confirm, safe_path
from android_mcp.security_audit import audit


def register(mcp: Any) -> None:
    @mcp.tool()
    def android_detect_environment() -> dict[str, Any]:
        """Detect JDK, Android SDK, platforms, build-tools, adb, emulator, Gradle, NDK. Never assumes tools exist."""
        return run(detect)

    @mcp.tool()
    def android_plan(goal: str, project: str | None = None) -> dict[str, Any]:
        """Research-before-action: inspect environment (and project if given) and return a sequenced plan of tools. Does not execute."""
        return run(_plan, goal=goal, project=project)

    @mcp.tool()
    def android_create_project(
        path: str,
        name: str,
        application_id: str,
        template: str = "compose-app",
        architecture: str = "mvvm",
        min_sdk: int | None = None,
        compile_sdk: int | None = None,
        target_sdk: int | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Create a Kotlin Android project (compose-app, views-app, library, multi-module) with version catalog.

        SDK versions default from installed platforms or 2026-safe values (compile/target 35, min 26).
        """
        return run(
            _create,
            path=path,
            name=name,
            application_id=application_id,
            template=template,
            architecture=architecture,
            min_sdk=min_sdk,
            compile_sdk=compile_sdk,
            target_sdk=target_sdk,
            overwrite=overwrite,
        )

    @mcp.tool()
    def android_inspect_project(path: str) -> dict[str, Any]:
        """Inspect Gradle modules, SDK levels, Compose vs XML, manifest components, architecture guess, catalog versions."""
        return run(lambda: inspect_project(safe_path(path, must_exist=True)))

    @mcp.tool()
    def android_create_module(project: str, module: str, kind: str = "library") -> dict[str, Any]:
        """Add an Android library (or application) module and include it in settings.gradle.kts."""
        return run(_add_module, project=project, module=module, kind=kind)

    @mcp.tool()
    def android_create_component(
        project: str,
        kind: str,
        name: str,
        module: str | None = None,
    ) -> dict[str, Any]:
        """Generate a component: activity, fragment, compose_screen, viewmodel, repository, service, broadcast_receiver, content_provider, room_entity, retrofit_api, notification."""
        return run(_component, project=project, kind=kind, name=name, module=module)

    @mcp.tool()
    def android_modify_manifest(
        project: str,
        add_permission: str | None = None,
        remove_permission: str | None = None,
        add_activity: str | None = None,
        exported_name: str | None = None,
        exported: bool | None = None,
    ) -> dict[str, Any]:
        """Add/remove permissions or activities; set android:exported on a component."""
        return run(
            _manifest,
            project=project,
            add_permission=add_permission,
            remove_permission=remove_permission,
            add_activity=add_activity,
            exported_name=exported_name,
            exported=exported,
        )

    @mcp.tool()
    def android_manage_dependencies(
        project: str,
        add_catalog_library: str | None = None,
        group: str | None = None,
        artifact: str | None = None,
        version: str | None = None,
        module: str | None = None,
    ) -> dict[str, Any]:
        """Add a library to gradle/libs.versions.toml and implementation() in a module build.gradle.kts."""
        return run(
            _deps,
            project=project,
            add_catalog_library=add_catalog_library,
            group=group,
            artifact=artifact,
            version=version,
            module=module,
        )

    @mcp.tool()
    def android_manage_resources(
        project: str,
        string_name: str | None = None,
        string_value: str | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        """Add a string resource (optionally localized, e.g. locale=es → values-es)."""
        return run(_res, project=project, string_name=string_name, string_value=string_value, locale=locale)

    @mcp.tool()
    def android_gradle(project: str, task: str = "assembleDebug", extra_args: list[str] | None = None) -> dict[str, Any]:
        """Run a Gradle task via wrapper: assembleDebug/Release, bundleRelease, test, lint, clean, dependencies, signingReport, tasks."""
        return run(_gradle, project=project, task=task, extra_args=extra_args)

    @mcp.tool()
    def android_analyze_build_failure(log: str) -> dict[str, Any]:
        """Map a Gradle/compiler log to likely cause and the next MCP tool to call."""
        return run(analyze_build_log, log=log)

    @mcp.tool()
    def android_devices() -> dict[str, Any]:
        """List connected emulators and physical devices (adb devices -l)."""
        return run(list_devices)

    @mcp.tool()
    def android_avd(
        action: str = "list",
        name: str | None = None,
        package: str | None = None,
        device: str = "pixel_6",
        headless: bool = True,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Manage AVDs: action=list|start|create. create needs name + system-image package and confirm=true."""
        return run(_avd, action=action, name=name, package=package, device=device, headless=headless, confirm=confirm)

    @mcp.tool()
    def android_app(
        action: str,
        apk: str | None = None,
        application_id: str | None = None,
        activity: str | None = None,
        permission: str | None = None,
        serial: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """App lifecycle: install, uninstall, launch, stop, clear, grant, revoke. install/uninstall/clear need confirm=true."""
        return run(
            _app,
            action=action,
            apk=apk,
            application_id=application_id,
            activity=activity,
            permission=permission,
            serial=serial,
            confirm=confirm,
        )

    @mcp.tool()
    def android_logcat(
        serial: str | None = None,
        package: str | None = None,
        filter: str | None = None,
        lines: int | None = None,
    ) -> dict[str, Any]:
        """Dump recent logcat (not a stream). Optionally filter by package or tag:level expression."""
        return run(_logcat, serial=serial, package=package, filter=filter, lines=lines)

    @mcp.tool()
    def android_screenshot(dest: str, serial: str | None = None) -> dict[str, Any]:
        """Capture a device screenshot to a sandbox path via adb exec-out screencap -p."""
        return run(_shot, dest=dest, serial=serial)

    @mcp.tool()
    def android_adb(args: list[str] | None = None, shell: str | None = None, serial: str | None = None) -> dict[str, Any]:
        """Allowlisted adb. Prefer dedicated tools. shell= is checked against the deny/allow lists. args= is a list of adb subcommands (devices, wait-for-device, …)."""
        return run(_adb_tool, args=args, shell=shell, serial=serial)

    @mcp.tool()
    def android_run_tests(project: str, kind: str = "unit") -> dict[str, Any]:
        """Run unit (test) or instrumented (connectedDebugAndroidTest) tests and parse JUnit XML if present."""
        return run(_tests, project=project, kind=kind)

    @mcp.tool()
    def android_analyze_crash(log: str) -> dict[str, Any]:
        """Parse logcat/tombstone text for FATAL EXCEPTION / ANR and suggest likely causes."""
        return run(analyze_crash, log=log)

    @mcp.tool()
    def android_profile(what: str = "meminfo", application_id: str | None = None, serial: str | None = None) -> dict[str, Any]:
        """dumpsys allowlist: meminfo, cpuinfo, gfxinfo, batterystats, activity, window, package."""
        return run(_profile, what=what, application_id=application_id, serial=serial)

    @mcp.tool()
    def android_security_audit(project: str) -> dict[str, Any]:
        """Static review: exported components, cleartext, debuggable, secrets, WebView JS, dangerous permissions."""
        return run(lambda: audit(safe_path(project, must_exist=True)))

    @mcp.tool()
    def android_inspect_artifact(path: str) -> dict[str, Any]:
        """Inspect APK/AAB: size, dex, manifest presence, apkanalyzer if installed, apksigner verify."""
        return run(lambda: inspect_apk(safe_path(path, must_exist=True)))

    @mcp.tool()
    def android_sdk(action: str = "status", package: str | None = None, confirm: bool = False) -> dict[str, Any]:
        """SDK manager: status (from detect), list (sdkmanager --list), install (needs ANDROID_MCP_ALLOW_SDK_INSTALL and confirm)."""
        return run(_sdk, action=action, package=package, confirm=confirm)


def _plan(goal: str, project: str | None) -> dict[str, Any]:
    env = detect()
    steps = []
    g = (goal or "").lower()
    steps.append({"tool": "android_detect_environment", "why": "Know JDK/SDK/adb before doing anything"})
    if project:
        steps.append({"tool": "android_inspect_project", "why": "Detect Compose vs Views, modules, SDK levels"})
    if any(k in g for k in ("create", "new app", "scaffold", "generate")):
        steps.append({"tool": "android_create_project", "args": {"template": "compose-app" if "xml" not in g and "view" not in g else "views-app"}})
    if any(k in g for k in ("build", "apk", "compile")):
        if not env.get("can_build"):
            steps.append({"tool": None, "why": "Install JDK 17 + SDK first", "missing": env.get("missing")})
        steps.append({"tool": "android_gradle", "args": {"task": "assembleDebug"}})
    if any(k in g for k in ("test",)):
        steps.append({"tool": "android_run_tests", "args": {"kind": "unit"}})
    if any(k in g for k in ("emulator", "avd")):
        steps.append({"tool": "android_avd", "args": {"action": "list"}})
    if any(k in g for k in ("install", "run on device", "launch")):
        steps.append({"tool": "android_devices"})
        steps.append({"tool": "android_app", "args": {"action": "install", "confirm": True}})
        steps.append({"tool": "android_app", "args": {"action": "launch"}})
        steps.append({"tool": "android_logcat"})
    if any(k in g for k in ("crash", "anr", "debug")):
        steps.append({"tool": "android_logcat"})
        steps.append({"tool": "android_analyze_crash"})
    if any(k in g for k in ("release", "bundle", "aab", "sign")):
        steps.append({"tool": "android_gradle", "args": {"task": "bundleRelease"}})
        steps.append({"tool": "android_inspect_artifact"})
    if any(k in g for k in ("security", "audit", "permission")):
        steps.append({"tool": "android_security_audit"})
    return {"goal": goal, "environment": {"can_build": env.get("can_build"), "missing": env.get("missing")}, "steps": steps}


def _create(**kw):
    ensure_writable()
    dest = safe_path(kw.pop("path"))
    return create_project(dest, **kw)


def _component(project, kind, name, module):
    ensure_writable()
    return create_component(safe_path(project, must_exist=True), kind, name, module)


def _manifest(project, add_permission, remove_permission, add_activity, exported_name, exported):
    ensure_writable()
    se = None
    if exported_name is not None and exported is not None:
        se = {"name": exported_name, "exported": exported}
    return modify_manifest(
        safe_path(project, must_exist=True),
        add_permission=add_permission,
        remove_permission=remove_permission,
        add_activity=add_activity,
        set_exported=se,
    )


def _add_module(project, module, kind):
    ensure_writable()
    if not re.match(r"^[a-z][a-z0-9_]*$", module or ""):
        raise ValidationError("module name must be lowercase identifier")
    root = find_root(safe_path(project, must_exist=True))
    settings = root / "settings.gradle.kts"
    if not settings.exists():
        raise NotFoundError("settings.gradle.kts not found")
    txt = settings.read_text(encoding="utf-8")
    inc = f'include(":{module}")'
    if inc not in txt:
        settings.write_text(txt.rstrip() + "\n" + inc + "\n", encoding="utf-8")
    from android_mcp.inspect import inspect_project as ip
    from android_mcp.scaffold import _write_android_library

    report = ip(root)
    app_id = report.get("application_id") or "com.example.app"
    files: list[str] = []
    ctx = {
        "application_id": app_id,
        "namespace": f"{app_id}.{module}",
        "package_path": f"{app_id.replace('.', '/')}/{module}",
        "name": module,
        **{k: str(v) for k, v in __import__("android_mcp.config", fromlist=["DEFAULTS"]).DEFAULTS.items()},
    }
    _write_android_library(root / module, ctx, files, module)
    return {"module": module, "files": files}


def _deps(project, add_catalog_library, group, artifact, version, module):
    ensure_writable()
    root = find_root(safe_path(project, must_exist=True))
    catalog = root / "gradle" / "libs.versions.toml"
    if not catalog.exists():
        raise NotFoundError("No gradle/libs.versions.toml")
    if not (add_catalog_library and group and artifact and version):
        raise ValidationError("Need add_catalog_library, group, artifact, version")
    key = add_catalog_library
    text = catalog.read_text(encoding="utf-8")
    if f"{key} =" not in text:
        if "[libraries]" not in text:
            text += "\n[libraries]\n"
        text = text.replace(
            "[libraries]",
            "[libraries]\n"
            + f'{key} = {{ group = "{group}", name = "{artifact}", version = "{version}" }}\n',
            1,
        )
        catalog.write_text(text, encoding="utf-8")
    report = inspect_project(root)
    mod = module or report.get("application_module") or "app"
    gfile = root / mod / "build.gradle.kts"
    if gfile.exists():
        gt = gfile.read_text(encoding="utf-8")
        alias = "libs." + key.replace("-", ".")
        line = f"    implementation({alias})\n"
        if alias not in gt and "dependencies {" in gt:
            gt = gt.replace("dependencies {", "dependencies {\n" + line, 1)
            gfile.write_text(gt, encoding="utf-8")
    return {"catalog": str(catalog), "library": key, "module": mod}


def _res(project, string_name, string_value, locale):
    ensure_writable()
    if not string_name or string_value is None:
        raise ValidationError("string_name and string_value required")
    root = find_root(safe_path(project, must_exist=True))
    report = inspect_project(root)
    mod = report.get("application_module") or "app"
    folder = "values" if not locale else f"values-{locale}"
    path = root / mod / "src/main/res" / folder / "strings.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        if f'name="{string_name}"' in txt:
            txt = re.sub(
                rf'<string name="{re.escape(string_name)}">[^<]*</string>',
                f'<string name="{string_name}">{string_value}</string>',
                txt,
            )
        else:
            txt = txt.replace("</resources>", f'    <string name="{string_name}">{string_value}</string>\n</resources>')
        path.write_text(txt, encoding="utf-8")
    else:
        path.write_text(
            f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="{string_name}">{string_value}</string>
</resources>
''',
            encoding="utf-8",
        )
    return {"path": str(path)}


def _gradle(project, task, extra_args):
    ensure_writable()
    mapped = GRADLE_TASKS.get(task, task)
    if task not in GRADLE_TASKS and not re.match(r"^[\w:\-]+$", task or ""):
        raise ValidationError("Suspicious Gradle task name")
    return gradle(safe_path(project, must_exist=True), mapped, extra=extra_args, timeout=SETTINGS.timeout)


def _avd(action, name, package, device, headless, confirm):
    if action == "list":
        return list_avds()
    if action == "start":
        if not name:
            raise ValidationError("name required")
        return start_avd(name, headless=headless)
    if action == "create":
        require_confirm(confirm, "create AVD")
        if not name or not package:
            raise ValidationError("name and system-image package required, e.g. system-images;android-35;google_apis;x86_64")
        from android_mcp.env import require_sdk_tool

        avd = require_sdk_tool("avdmanager")
        args = [avd, "create", "avd", "-n", name, "-k", package, "-d", device, "--force"]
        return run_cmd(args, input_text="no\n", timeout=120)
    raise ValidationError("action must be list, start, or create")


def _app(action, apk, application_id, activity, permission, serial, confirm):
    serial = pick_serial(serial)
    if action in {"install", "uninstall", "clear"}:
        require_confirm(confirm, action)
    if action == "install":
        if not apk:
            raise ValidationError("apk path required")
        p = safe_path(apk, must_exist=True)
        return adb(["install", "-r", "-t", str(p)], serial=serial, timeout=120)
    if action == "uninstall":
        if not application_id:
            raise ValidationError("application_id required")
        return adb(["uninstall", application_id], serial=serial)
    if action == "launch":
        if not application_id:
            raise ValidationError("application_id required")
        comp = f"{application_id}/{activity or '.MainActivity'}"
        return adb(["shell", "am", "start", "-n", comp], serial=serial)
    if action == "stop":
        if not application_id:
            raise ValidationError("application_id required")
        return adb(["shell", "am", "force-stop", application_id], serial=serial)
    if action == "clear":
        if not application_id:
            raise ValidationError("application_id required")
        return adb(["shell", "pm", "clear", application_id], serial=serial)
    if action == "grant":
        return adb(["shell", "pm", "grant", application_id, permission], serial=serial)
    if action == "revoke":
        return adb(["shell", "pm", "revoke", application_id, permission], serial=serial)
    raise ValidationError("action must be install|uninstall|launch|stop|clear|grant|revoke")


def _logcat(serial, package, filter, lines):
    n = lines or SETTINGS.logcat_lines
    args = ["logcat", "-d", "-t", str(n)]
    if filter:
        args.append(filter)
    r = adb(args, serial=pick_serial(serial), timeout=30)
    out = r.get("stdout") or ""
    if package:
        out = "\n".join(ln for ln in out.splitlines() if package in ln)
    r["stdout"] = out[-60_000:]
    return r


def _shot(dest, serial):
    ensure_writable()
    path = safe_path(dest)
    path.parent.mkdir(parents=True, exist_ok=True)
    r = adb(["exec-out", "screencap", "-p"], serial=pick_serial(serial), timeout=30)
    # run_cmd is text mode — screenshot needs binary. Use subprocess here.
    from android_mcp.env import require_adb
    import subprocess

    cmd = [require_adb()]
    s = pick_serial(serial)
    if s:
        cmd += ["-s", s]
    cmd += ["exec-out", "screencap", "-p"]
    proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        raise DependencyMissing("screencap failed", {"stderr": proc.stderr[-2000:]})
    path.write_bytes(proc.stdout)
    return {"path": str(path), "bytes": path.stat().st_size}


def _adb_tool(args, shell, serial):
    if shell:
        cmd = check_shell(shell)
        return adb(["shell", cmd], serial=pick_serial(serial))
    if not args:
        raise ValidationError("Provide args list or shell=")
    # only simple adb verbs
    allowed = {"devices", "wait-for-device", "get-state", "get-serialno", "version", "help", "logcat", "install", "uninstall", "pull", "push", "shell"}
    if args[0] not in allowed:
        raise PolicyError(f"adb subcommand not allowed: {args[0]}")
    if args[0] == "shell" and len(args) > 1:
        check_shell(" ".join(args[1:]))
    return adb(args, serial=pick_serial(serial))


def _tests(project, kind):
    ensure_writable()
    task = "testDebugUnitTest" if kind == "unit" else "connectedDebugAndroidTest"
    result = gradle(safe_path(project, must_exist=True), task, timeout=SETTINGS.timeout)
    root = find_root(safe_path(project))
    xmls = list(root.glob("**/build/test-results/**/*.xml"))[:20]
    result["junit_xml"] = [str(x) for x in xmls]
    return result


PROFILE = {"meminfo", "cpuinfo", "gfxinfo", "batterystats", "activity", "window", "package"}


def _profile(what, application_id, serial):
    if what not in PROFILE:
        raise ValidationError(f"what must be one of {sorted(PROFILE)}")
    args = ["shell", "dumpsys", what]
    if application_id and what in {"meminfo", "gfxinfo", "package"}:
        args.append(application_id)
    r = adb(args, serial=pick_serial(serial), timeout=40)
    r["stdout"] = (r.get("stdout") or "")[:20_000]
    return r


def _sdk(action, package, confirm):
    env = detect()
    if action == "status":
        return env
    sm = env.get("sdkmanager")
    if not sm:
        raise DependencyMissing("sdkmanager not found", env)
    if action == "list":
        return run_cmd([sm, "--list"], timeout=120)
    if action == "install":
        if not SETTINGS.allow_sdk_install:
            raise PolicyError("Set ANDROID_MCP_ALLOW_SDK_INSTALL=1 to install SDK packages")
        require_confirm(confirm, "sdk install")
        if not package or not re.match(r"^[\w.;\-]+$", package):
            raise ValidationError("package id like platforms;android-35")
        return run_cmd([sm, "--install", package], input_text="y\n", timeout=300)
    raise ValidationError("action status|list|install")
