"""ComfyUI runtime + client.

Manages a ComfyUI install (clone, python env, deps) and its lifecycle as a
subprocess on the host that runs generation. Provides an HTTP client to submit
workflows, monitor history and fetch output images. Real, but only exercisable
where ComfyUI actually runs (the target GPU machine).

ComfyUI generation is driven through *workflow JSON* files. Placeholders
{{prompt}} {{negative_prompt}} {{seed}} {{width}} {{height}} {{steps}} are
injected at submit time. We never claim to run a workflow that is not installed.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from ..config import Settings
from ..errors import (ComfyUIError, MissingDependency, PortInUse,
                      RuntimeNotRunning)
from ..backends.base import Backend, ImageResult


class ComfyRuntime:
    def __init__(self, settings: Settings):
        self.s = settings
        self.host = settings.comfyui_host
        self.port = settings.comfyui_port
        self._proc = None
        self.install_dir = self._default_install()

    def _default_install(self) -> Path:
        env = os.environ.get("OLCAP_COMFYUI_DIR")
        if env:
            return Path(env)
        return self.s.resolved_root().parent / "ComfyUI"

    def detect(self) -> dict:
        d = self.install_dir
        present = (d / "main.py").exists()
        return {"available": present, "dir": str(d), "installed": present,
                "running": self.is_running()}

    def install(self, *, venv: bool = True, job=None) -> dict:
        git = shutil.which("git")
        if not git:
            raise MissingDependency("git is required to install ComfyUI")
        d = self.install_dir
        if (d / "main.py").exists():
            return {"installed": True, "dir": str(d), "fresh": False}
        d.mkdir(parents=True, exist_ok=True)
        if job:
            job.append_log("cloning ComfyUI")
        subprocess.run([git, "clone",
                        "https://github.com/comfyanonymous/ComfyUI.git",
                        str(d)], check=True)
        py = self._python(d, venv)
        if job:
            job.append_log("installing ComfyUI requirements")
        subprocess.run([py, "-m", "pip", "install", "-r",
                        str(d / "requirements.txt")], check=True)
        subprocess.run([py, "-m", "pip", "install", "websocket-client"],
                       check=True)
        return {"installed": True, "dir": str(d), "fresh": True,
                "python": str(py)}

    def _python(self, d: Path, venv: bool) -> str:
        if not venv:
            return sys_python()
        pydir = d / "venv"
        if platform.system() == "Windows":
            py = pydir / "Scripts" / "python.exe"
        else:
            py = pydir / "bin" / "python"
        if not py.exists():
            subprocess.run([sys_python(), "-m", "venv", str(pydir)], check=True)
        return str(py)

    def start(self, *, model_dir: str | None = None, job=None) -> dict:
        det = self.detect()
        if not det["installed"]:
            raise MissingDependency(
                "ComfyUI not installed. Run install_runtime or point "
                "OLCAP_COMFYUI_DIR at an existing ComfyUI.")
        if self.is_running():
            return {"running": True, "url": self.url(), "fresh": False}
        if self._port_open():
            raise PortInUse(
                f"port {self.port} already in use but ComfyUI not responding "
                "as ours; set a different comfyui_port.")
        py = self._python(self.install_dir, venv=True)
        cmd = [py, str(self.install_dir / "main.py"),
               "--port", str(self.port), "--listen", self.host]
        if model_dir:
            cmd += ["--models-dir", str(model_dir)]
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        self._proc = subprocess.Popen(
            cmd, cwd=str(self.install_dir),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=flags)
        for _ in range(60):
            if job:
                job.append_log(f"waiting for ComfyUI on {self.url()}...")
            if self.health():
                return {"running": True, "url": self.url(), "fresh": True}
            time.sleep(1)
        raise ComfyUIError("ComfyUI did not become ready within 60s")

    def stop(self, *, graceful_timeout: float = 10) -> dict:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=graceful_timeout)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None
        return {"stopped": True}

    def is_running(self) -> bool:
        if self._proc and self._proc.poll() is None:
            return True
        return self._port_open()

    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _port_open(self) -> bool:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(0.5)
            return s.connect_ex((self.host, self.port)) == 0
        finally:
            s.close()

    def health(self) -> dict:
        try:
            r = urllib.request.urlopen(self.url() + "/system_stats", timeout=3)
            return r.status == 200
        except Exception:   # noqa: BLE001
            return False

    def logs(self, tail: int = 200) -> str:
        if not self._proc or not self._proc.stdout:
            return "(runtime not started by this process; no captured log)"
        try:
            import select
            if select.select([self._proc.stdout], [], [], 0)[0]:
                data = self._proc.stdout.read1(65536)
                return data.decode("utf-8", "replace")
        except Exception:   # noqa: BLE001
            pass
        return ""


def sys_python() -> str:
    return sys.executable


class ComfyBackend(Backend):
    """Backend that submits a workflow to a running ComfyUI and returns output."""
    name = "comfyui"
    display = "ComfyUI (external process)"

    def __init__(self, runtime: ComfyRuntime, workflows_dir: str):
        self.runtime = runtime
        self.workflows_dir = Path(workflows_dir)

    def probe(self) -> dict:
        up = self.runtime.health()
        det = self.runtime.detect()
        return {"available": up, "running": up, "installed": det["installed"],
                "url": self.runtime.url()}

    def supports_family(self, family_id: str) -> bool:
        if not self.runtime.health():
            return False
        return bool(self._workflow_for(family_id, "txt2img"))

    def _workflow_for(self, family, op):
        candidates = [
            self.workflows_dir / f"{family}.{op}.json",
            self.workflows_dir / f"{family}.json",
            self.workflows_dir / f"{op}.json",
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    def generate(self, plan) -> ImageResult:
        return self._run_workflow(plan, "txt2img")

    def image_to_image(self, plan):
        return self._run_workflow(plan, "img2img")

    def inpaint(self, plan):
        return self._run_workflow(plan, "inpaint")

    def upscale(self, plan):
        return self._run_workflow(plan, "upscale")

    def _run_workflow(self, plan, op) -> ImageResult:
        if not self.runtime.health():
            raise RuntimeNotRunning("ComfyUI is not running; call start_runtime")
        wf = self._workflow_for(plan.family, op)
        if not wf:
            raise ComfyUIError(
                f"no ComfyUI workflow installed for {plan.family}/{op}. Add a "
                f"workflow JSON to {self.workflows_dir}.")
        wf = _inject(wf, plan)
        prompt_id = self._submit(wf)
        return self._poll_output(prompt_id, plan)

    def _submit(self, workflow) -> str:
        data = json.dumps({"prompt": workflow}).encode()
        req = urllib.request.Request(self.runtime.url() + "/prompt", data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
        if "prompt_id" not in body:
            raise ComfyUIError("ComfyUI prompt rejected: %s"
                               % json.dumps(body)[:500])
        return body["prompt_id"]

    def _poll_output(self, prompt_id, plan, timeout: float = 1800) -> ImageResult:
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                hist = urllib.request.urlopen(
                    self.runtime.url() + "/history/" + prompt_id, timeout=10)
                h = json.loads(hist.read().decode())
            except Exception:   # noqa: BLE001
                time.sleep(1)
                continue
            if prompt_id in h:
                outputs = h[prompt_id].get("outputs", {})
                for node in outputs.values():
                    for img in node.get("images", []):
                        path = self._fetch_image(img, plan)
                        return ImageResult(
                            path=path, width=plan.params.get("width", 0),
                            height=plan.params.get("height", 0),
                            format="png", backend=self.name, model=plan.model,
                            quant=plan.quant, seed=plan.params.get("seed"),
                            metadata={"comfy_prompt_id": prompt_id})
                raise ComfyUIError("workflow finished with no image output")
            time.sleep(1)
        raise ComfyUIError("timed out waiting for ComfyUI output")

    def _fetch_image(self, img, plan) -> str:
        params = urllib.parse.urlencode(
            {"filename": img["filename"], "subfolder": img.get("subfolder", ""),
             "type": img.get("type", "output")})
        url = self.runtime.url() + "/view?" + params
        data = urllib.request.urlopen(url, timeout=60).read()
        outdir = Path(plan.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        target = outdir / (plan.filename or f"{plan.job_id}.png")
        target.write_bytes(data)
        return str(target)


def _inject(workflow_json_path: Path, plan) -> dict:
    wf = json.loads(workflow_json_path.read_text(encoding="utf-8"))
    repl = {"prompt": plan.params.get("prompt", ""),
            "negative_prompt": plan.params.get("negative_prompt", ""),
            "seed": plan.params.get("seed", -1),
            "width": plan.params.get("width", 1024),
            "height": plan.params.get("height", 1024),
            "steps": plan.params.get("steps", 30)}

    def rec(o):
        if isinstance(o, dict):
            return {k: rec(v) for k, v in o.items()}
        if isinstance(o, list):
            return [rec(x) for x in o]
        if isinstance(o, str):
            for k, v in repl.items():
                o = o.replace("{{" + k + "}}", str(v))
            return o
        return o
    return rec(wf)
