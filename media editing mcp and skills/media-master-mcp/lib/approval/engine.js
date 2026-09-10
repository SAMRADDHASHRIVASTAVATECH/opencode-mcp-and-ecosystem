import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
const stable = (x) => Array.isArray(x) ? `[${x.map(stable)}]` : x && typeof x === 'object' ? `{${Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + stable(x[k])).join(',')}}` : JSON.stringify(x);
export function planDigest(p) { return createHash('sha256').update(stable(p)).digest('hex'); }
export class Approval {
    tokens = new Map();
    issue(p, confirmation) { if (!/^(approve|approved|yes)$/i.test(confirmation.trim()))
        throw Error('EXPLICIT_APPROVAL_REQUIRED'); const token = randomBytes(32).toString('base64url'), expires = Date.now() + 60_000; this.tokens.set(token, { digest: p.digest, expires, used: false }); return { token, planId: p.id, digest: p.digest, expiresAt: expires }; }
    consume(p, token) { const r = this.tokens.get(token); if (!r || r.used || r.expires < Date.now())
        throw Error('APPROVAL_INVALID_EXPIRED_OR_USED'); const { digest, ...unsigned } = p; const a = Buffer.from(planDigest(unsigned)), b = Buffer.from(r.digest); if (a.length !== b.length || !timingSafeEqual(a, b))
        throw Error('PLAN_CHANGED'); r.used = true; }
}
//# sourceMappingURL=engine.js.map