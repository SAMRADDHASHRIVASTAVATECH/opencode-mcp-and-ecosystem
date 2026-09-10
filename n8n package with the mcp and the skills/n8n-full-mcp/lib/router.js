import { RestAdapter } from './adapters/rest.js';
import { OfflineAdapter } from './adapters/offline.js';
import { OfficialMcpAdapter } from './adapters/official-mcp.js';
export class Router {
    config;
    rest;
    offline;
    official;
    constructor(config) {
        this.config = config;
        this.rest = new RestAdapter(config);
        this.offline = new OfflineAdapter(config.offlineDir);
        this.official = new OfficialMcpAdapter(config);
    }
    async read(officialTool, args, api, offline) { if (this.official.available() && officialTool) {
        const r = await this.official.call(officialTool, args);
        if (r.ok)
            return r;
    } if (this.rest.available() && api) {
        const r = await this.rest.request('GET', api.path, undefined, api.query);
        if (r.ok)
            return r;
    } if (offline)
        return offline(); return { ok: false, backend: 'router', error: { code: 'unavailable', message: 'No configured backend supports this capability' } }; }
    async write(officialTool, args, api, offline) { if (this.official.available() && officialTool) {
        const r = await this.official.call(officialTool, args);
        if (r.ok)
            return r;
    } if (this.rest.available() && api) {
        const r = await this.rest.request(api.method, api.path, api.body);
        if (r.ok)
            return r;
    } if (offline)
        return offline(); return { ok: false, backend: 'router', error: { code: 'unavailable', message: 'No configured backend supports this operation' } }; }
}
//# sourceMappingURL=router.js.map