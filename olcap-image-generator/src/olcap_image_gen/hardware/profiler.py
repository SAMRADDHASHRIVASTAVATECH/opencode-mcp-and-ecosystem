"""Hardware profiler: populates a Profile with real detected values."""
from __future__ import annotations

import os
import platform
import shutil
import sys

from .profile import Profile


def detect() -> Profile:
    p = Profile()
    _system(p)
    _cpu(p)
    _ram(p)
    _storage(p)
    _software(p)
    _gpu(p)
    _recommend(p)
    return p


def _system(p: Profile):
    p.system["os"] = platform.system()
    p.system["architecture"] = platform.machine()
    p.system["platform"] = platform.platform()


def _cpu(p: Profile):
    try:
        import psutil
        p.cpu["physical_cores"] = psutil.cpu_count(logical=False)
        p.cpu["threads"] = psutil.cpu_count(logical=True)
        p.cpu["cores"] = p.cpu["physical_cores"] or p.cpu["threads"]
        p.cpu["model"] = _cpu_brand() or f"{platform.processor() or 'CPU'}"
    except Exception:   # noqa: BLE001
        p.cpu["model"] = platform.processor() or "unknown"
        p.cpu["cores"] = os.cpu_count()


def _cpu_brand() -> str | None:
    for m in ("platform",):
        try:
            if sys.platform.startswith("linux"):
                with open("/proc/cpuinfo", "r", encoding="utf-8",
                          errors="ignore") as f:
                    for line in f:
                        if line.lower().startswith("model name"):
                            return line.split(":", 1)[1].strip()
        except Exception:   # noqa: BLE001
            pass
    return None


def _ram(p: Profile):
    try:
        import psutil
        vm = psutil.virtual_memory()
        p.ram["total_gb"] = round(vm.total / (1024 ** 3), 2)
        p.ram["available_gb"] = round(vm.available / (1024 ** 3), 2)
        p.ram["used_gb"] = round(vm.used / (1024 ** 3), 2)
    except Exception:   # noqa: BLE001
        p.ram["total_gb"] = 0.0


def _storage(p: Profile):
    try:
        import psutil
        # use the root of the state dir or cwd
        parts = psutil.disk_partitions()
        if not parts:
            return
        # choose the partition of the current dir
        here = os.path.abspath(os.getcwd())
        best = parts[0]
        for part in parts:
            if here.startswith(part.mountpoint):
                best = part
                break
        use = psutil.disk_usage(best.mountpoint)
        p.storage["system_drive"] = best.mountpoint
        p.storage["free_gb"] = round(use.free / (1024 ** 3), 2)
        p.storage["total_gb"] = round(use.total / (1024 ** 3), 2)
        p.storage["fs"] = best.fstype
    except Exception:   # noqa: BLE001
        pass


def _software(p: Profile):
    p.software["python_version"] = platform.python_version()
    p.software["git"] = bool(shutil.which("git"))
    p.software["node"] = bool(shutil.which("node"))
    p.software["npm"] = bool(shutil.which("npm"))
    p.software["torch"] = bool(_mod("torch"))
    p.software["comfyui"] = _detect_comfyui_dir()
    p.software["cuda_toolkit"] = bool(shutil.which("nvcc"))


def _detect_comfyui_dir() -> str | None:
    for env in ("OLCAP_COMFYUI_DIR", "COMFYUI_DIR"):
        d = os.environ.get(env)
        if d and os.path.exists(os.path.join(d, "main.py")):
            return d
    for cand in (os.path.join(os.path.expanduser("~"), "ComfyUI"),):
        if os.path.exists(os.path.join(cand, "main.py")):
            return cand
    return None


def _gpu(p: Profile):
    g = p.gpu
    # nvidia-smi
    smi = shutil.which("nvidia-smi")
    if not smi and os.name == "nt":
        for cand in (r"C:\Windows\System32\nvidia-smi.exe",
                     r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"):
            if os.path.exists(cand):
                smi = cand
                break
    if smi:
        try:
            import subprocess
            out = subprocess.run(
                [smi, "--query-gpu=name,memory.total,memory.free,driver_version,"
                      "compute_cap,utilization.gpu,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=15)
            if out.returncode == 0 and out.stdout.strip():
                line = [x.strip() for x in out.stdout.splitlines()[0].split(",")]
                name, total, free = line[0], line[1], line[2]
                g["present"] = True
                g["vendor"] = "NVIDIA"
                g["model"] = name
                g["vram_gb"] = round(float(total) / 1024, 2)
                g["vram_free_gb"] = round(float(free) / 1024, 2)
                if len(line) > 3:
                    g["driver_version"] = line[3]
                if len(line) > 4:
                    g["compute_capability"] = line[4]
                if len(line) > 5:
                    try:
                        g["utilization_percent"] = float(line[5])
                    except Exception:   # noqa: BLE001
                        pass
                if len(line) > 6:
                    try:
                        g["temperature_c"] = float(line[6])
                    except Exception:   # noqa: BLE001
                        pass
        except Exception:   # noqa: BLE001
            pass
    # cuda availability via torch if installed
    g["cuda_available"] = _cuda_check()
    if g["cuda_available"] and not g["present"]:
        g["present"] = True
        g["vendor"] = "NVIDIA"
        try:
            import torch
            g["model"] = torch.cuda.get_device_name(0)
            try:
                props = torch.cuda.get_device_properties(0)
                g["vram_gb"] = round(props.total_memory / (1024 ** 3), 2)
                g["compute_capability"] = f"{props.major}.{props.minor}"
            except Exception:   # noqa: BLE001
                pass
        except Exception:   # noqa: BLE001
            pass


def _cuda_check() -> bool:
    if not _mod("torch"):
        return False
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:   # noqa: BLE001
        return False


def _recommend(p: Profile):
    if p.gpu["present"]:
        p.recommended_execution["mode"] = "gpu"
        p.recommended_execution["gpu_offload"] = "adaptive"
        p.recommended_execution["cpu_offload"] = True
    else:
        p.recommended_execution["mode"] = "cpu"
        p.recommended_execution["gpu_offload"] = "none"
        p.recommended_execution["cpu_offload"] = True


def detect_os_summary() -> dict:
    return {"os": platform.system(), "release": platform.release(),
            "arch": platform.machine(), "python": platform.python_version()}


def _mod(name: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(name) is not None
