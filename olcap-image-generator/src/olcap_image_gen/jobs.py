"""Asynchronous job system with stage + progress tracking.

Long-running work (model download, runtime start, generation, upscaling) runs in
background threads and reports a stage + optional percent. ETA is only ever set
from measured rates; otherwise None.
"""
from __future__ import annotations

import threading
import time
import uuid

STAGES = ["queued", "initializing", "loading_model", "running", "upscaling",
          "refining", "completed", "failed", "cancelled"]


class Job:
    def __init__(self, tool: str, label: str, total: float | None = None):
        self.job_id = "olcap-" + uuid.uuid4().hex[:12]
        self.tool = tool
        self.label = label
        self.stage = "queued"
        self.progress_percent = 0.0
        self.step = None
        self.total_steps = total
        self.elapsed_s = 0.0
        self.eta_s = None
        self.vram_gb = None
        self.ram_gb = None
        self.model = None
        self.output = None
        self.error = None
        self.log = []
        self.created = time.time()
        self.started = None
        self.finished = None
        self._cancel = threading.Event()
        self._thread = None

    def append_log(self, msg: str):
        self.log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        self.log = self.log[-500:]

    def as_dict(self, *, tail_log: int = 20):
        return {
            "job_id": self.job_id, "tool": self.tool, "label": self.label,
            "status": self.stage, "progress_percent":
                round(self.progress_percent, 1) if self.progress_percent else None,
            "stage": self.stage, "step": self.step,
            "total_steps": self.total_steps, "elapsed_s": self.elapsed_s,
            "eta_s": self.eta_s, "vram_gb": self.vram_gb,
            "ram_gb": self.ram_gb, "model": self.model,
            "output": self.output, "error": self.error,
            "log_tail": self.log[-tail_log:],
        }


class JobManager:
    def __init__(self, max_history: int = 200):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._max_history = max_history

    def submit(self, tool: str, label: str, fn, total_steps: float | None = None,
               model: str | None = None) -> dict:
        job = Job(tool, label, total_steps)
        job.model = model

        def _wrap():
            job.started = time.time()
            job.stage = "initializing"
            try:
                job._thread = threading.current_thread()
                res = fn(job)
                job.output = res
                job.stage = "completed"
            except Exception as e:     # noqa: BLE001
                job.error = {"code": getattr(e, "code", "ERROR"),
                             "message": str(e)}
                job.stage = "failed"
            finally:
                job.finished = time.time()
                job.elapsed_s = round(job.finished - (job.started or
                                                      job.created), 3)
        with self._lock:
            self._jobs[job.job_id] = job
        t = threading.Thread(target=_wrap, daemon=True)
        job._thread = t
        t.start()
        return job.as_dict()

    def cancel(self, job_id: str) -> dict | None:
        with self._lock:
            j = self._jobs.get(job_id)
        if not j:
            return None
        j._cancel.set()
        j.log.append("cancellation requested")
        if j.stage in ("queued", "initializing", "loading_model", "running",
                       "upscaling", "refining"):
            j.stage = "cancelling"
        return j.as_dict()

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            j = self._jobs.get(job_id)
            return j.as_dict() if j else None

    def progress(self, job_id: str) -> dict | None:
        return self.get(job_id)

    def list(self, limit: int = 50) -> list[dict]:
        with self._lock:
            allj = sorted(self._jobs.values(), key=lambda j: -j.created)
        return [j.as_dict(tail_log=5) for j in allj[:limit]]

    def update(self, job_id: str, **kw):
        with self._lock:
            j = self._jobs.get(job_id)
        if j:
            for k, v in kw.items():
                setattr(j, k, v)

    def append_log(self, job_id: str, msg: str):
        with self._lock:
            j = self._jobs.get(job_id)
        if j:
            j.log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
            j.log = j.log[-500:]

    def cancelled(self, job_id: str) -> bool:
        with self._lock:
            j = self._jobs.get(job_id)
            return bool(j and j._cancel.is_set())
