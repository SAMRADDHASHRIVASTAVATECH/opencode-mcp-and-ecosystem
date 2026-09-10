import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { existsSync, statSync } from 'node:fs';
export class Jobs {
    jobs = new Map();
    children = new Map();
    start(p, timeoutMs) { const id = randomUUID(), j = { id, planId: p.id, operation: p.operation, status: 'running', stdout: '', stderr: '', startedAt: Date.now() }; const c = spawn(p.executable, p.argv, { shell: false, windowsHide: true }); j.pid = c.pid; this.jobs.set(id, j); this.children.set(id, c); const timer = setTimeout(() => { if (j.status === 'running') {
        j.status = 'timed_out';
        c.kill('SIGTERM');
    } }, timeoutMs); c.stdout?.on('data', d => j.stdout = (j.stdout + d).slice(-200_000)); c.stderr?.on('data', d => j.stderr = (j.stderr + d).slice(-200_000)); c.on('error', e => { j.status = 'failed'; j.stderr = (j.stderr + '\n' + e.message).slice(-200_000); j.completedAt = Date.now(); clearTimeout(timer); }); c.on('close', code => { clearTimeout(timer); j.exitCode = code; j.completedAt = Date.now(); if (j.status === 'running')
        j.status = code === 0 && p.outputs.every(existsSync) ? 'completed' : 'failed'; if (j.status === 'completed')
        j.stdout += '\nVERIFIED_OUTPUTS ' + JSON.stringify(p.outputs.map(x => ({ path: x, bytes: statSync(x).size }))); this.children.delete(id); }); return j; }
    get(id) { const j = this.jobs.get(id); if (!j)
        throw Error('JOB_NOT_FOUND'); return j; }
    list() { return [...this.jobs.values()]; }
    cancel(id) { const j = this.get(id), c = this.children.get(id); if (!c || j.status !== 'running')
        throw Error('JOB_NOT_RUNNING'); j.status = 'cancelled'; c.kill('SIGTERM'); return j; }
}
//# sourceMappingURL=manager.js.map