import net from 'node:net';
export async function waitPort(host, port, timeoutMs = 120000, interval = 2000) { const end = Date.now() + timeoutMs; while (Date.now() < end) {
    const ok = await new Promise(r => { const s = net.createConnection({ host, port, timeout: 1500 }, () => { s.destroy(); r(true); }); s.on('error', () => r(false)); s.on('timeout', () => { s.destroy(); r(false); }); });
    if (ok)
        return { ready: true, host, port, elapsedMs: timeoutMs - (end - Date.now()) };
    await new Promise(r => setTimeout(r, interval));
} return { ready: false, host, port, error: 'TIMEOUT' }; }
//# sourceMappingURL=readiness.js.map