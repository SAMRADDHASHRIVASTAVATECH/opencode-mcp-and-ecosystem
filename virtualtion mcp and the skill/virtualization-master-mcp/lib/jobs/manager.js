import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
export class Jobs {
    m = new Map();
    start(p) { const id = randomUUID(), [cmd, ...args] = p.argv, j = { id, planId: p.id, context: p.context, vm: p.vm, operation: p.action, status: 'running', stdout: '', stderr: '', started: Date.now() }; const c = spawn(cmd, args, { shell: false, windowsHide: true }); j.pid = c.pid; this.m.set(id, j); c.stdout?.on('data', d => j.stdout = (j.stdout + d).slice(-200000)); c.stderr?.on('data', d => j.stderr = (j.stderr + d).slice(-200000)); c.on('error', e => { j.status = 'failed'; j.stderr = e.message; j.completed = Date.now(); }); c.on('close', code => { j.code = code; j.status = code === 0 ? 'completed' : 'failed'; j.completed = Date.now(); }); return j; }
    get(id) { const j = this.m.get(id); if (!j)
        throw Error('JOB_NOT_FOUND'); return j; }
    list() { return [...this.m.values()]; }
    cancel(id) { const j = this.get(id); if (j.status !== 'running' || !j.pid)
        throw Error('JOB_NOT_RUNNING'); process.kill(j.pid, 'SIGTERM'); j.status = 'cancelled'; j.completed = Date.now(); return j; }
}
//# sourceMappingURL=manager.js.map