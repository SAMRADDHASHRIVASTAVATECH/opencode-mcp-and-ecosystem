import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
const stable = (x) => Array.isArray(x) ? `[${x.map(stable).join(',')}]` : x && typeof x === 'object' ? `{${Object.entries(x).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => JSON.stringify(k) + ':' + stable(v)).join(',')}}` : JSON.stringify(x);
export class ApprovalEngine {
    ttlMs;
    records = new Map();
    constructor(ttlMs = 60000) {
        this.ttlMs = ttlMs;
    }
    describe(o) { return { ...o, approvalRequired: o.risk !== 'read', prompt: 'Approve this exact operation?' }; }
    issue(o, answer) { if (!/^(approve|approved|yes)$/i.test(answer.trim()))
        throw new Error('Explicit approval not provided'); const digest = createHash('sha256').update(stable(o)).digest('hex'); const token = randomBytes(32).toString('base64url'); this.records.set(token, { token, digest, expiresAt: Date.now() + this.ttlMs, used: false }); return { approvalToken: token, expiresAt: Date.now() + this.ttlMs, operationDigest: digest }; }
    consume(o, token) { if (o.risk === 'read')
        return; const r = token ? this.records.get(token) : undefined; if (!r || r.used || Date.now() > r.expiresAt)
        throw new Error('Approval is missing, expired, or already used'); const d = createHash('sha256').update(stable(o)).digest(); const expected = Buffer.from(r.digest, 'hex'); if (d.length !== expected.length || !timingSafeEqual(d, expected))
        throw new Error('Approval does not match the exact operation'); r.used = true; }
}
//# sourceMappingURL=engine.js.map