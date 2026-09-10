export class RestAdapter {
    c;
    constructor(c) {
        this.c = c;
    }
    available() { return !!(this.c.baseUrl && this.c.apiKey); }
    async request(method, path, body, query) { if (!this.available())
        return { ok: false, backend: 'rest', error: { code: 'unavailable', message: 'REST adapter not configured' } }; const u = new URL(`/api/v1/${path.replace(/^\//, '')}`, this.c.baseUrl); for (const [k, v] of Object.entries(query ?? {}))
        if (v !== undefined)
            u.searchParams.set(k, String(v)); const ctl = new AbortController(); const timer = setTimeout(() => ctl.abort(), this.c.timeoutMs); try {
        const r = await fetch(u, { method, headers: { 'X-N8N-API-KEY': this.c.apiKey, 'Accept': 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}) }, body: body ? JSON.stringify(body) : undefined, signal: ctl.signal });
        const text = await r.text();
        let data;
        try {
            data = text ? JSON.parse(text) : null;
        }
        catch {
            data = text;
        }
        if (!r.ok)
            return { ok: false, backend: 'rest', error: { code: r.status === 401 ? 'authentication' : r.status === 403 ? 'authorization' : r.status === 404 ? 'not_found' : 'http_error', message: `n8n API returned ${r.status}`, status: r.status, details: data } };
        return { ok: true, backend: 'rest', data };
    }
    catch (e) {
        return { ok: false, backend: 'rest', error: { code: e instanceof DOMException && e.name === 'AbortError' ? 'timeout' : 'network', message: e instanceof Error ? e.message : String(e) } };
    }
    finally {
        clearTimeout(timer);
    } }
}
//# sourceMappingURL=rest.js.map