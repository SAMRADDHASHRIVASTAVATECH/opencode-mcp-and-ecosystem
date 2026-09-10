import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
const stable = (x) => Array.isArray(x) ? `[${x.map(stable)}]` : x && typeof x === 'object' ? `{${Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + stable(x[k])).join(',')}}` : JSON.stringify(x);
export function digest(p) { return createHash('sha256').update(stable(p)).digest('hex'); }
export class Approval {
    m = new Map();
    issue(p, a) { if (!/^(yes|approve|approved)$/i.test(a.trim()))
        throw Error('Explicit approval required'); const t = randomBytes(32).toString('base64url'); this.m.set(t, { d: p.digest, e: Date.now() + 60000, u: false }); return { token: t, digest: p.digest, expiresAt: Date.now() + 60000 }; }
    consume(p, t) { const r = this.m.get(t); if (!r || r.u || Date.now() > r.e)
        throw Error('Approval missing, expired, or used'); const { digest: _, ...x } = p; const a = Buffer.from(digest(x)), b = Buffer.from(r.d); if (a.length !== b.length || !timingSafeEqual(a, b))
        throw Error('Plan changed'); r.u = true; }
}
//# sourceMappingURL=engine.js.map