import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
export class OfficialMcpAdapter {
    c;
    client;
    constructor(c) {
        this.c = c;
    }
    available() { return !!this.c.officialMcpUrl; }
    async connect() {
        if (this.client)
            return this.client;
        const headers = this.c.officialMcpToken ? { Authorization: `Bearer ${this.c.officialMcpToken}` } : {};
        const transport = new StreamableHTTPClientTransport(new URL(this.c.officialMcpUrl), { requestInit: { headers } });
        this.client = new Client({ name: 'n8n-full-mcp-proxy', version: '0.1.0' });
        await this.client.connect(transport);
        return this.client;
    }
    async listTools() {
        try {
            return { ok: true, backend: 'official-mcp', data: await (await this.connect()).listTools() };
        }
        catch (e) {
            return { ok: false, backend: 'official-mcp', error: { code: 'mcp_error', message: e instanceof Error ? e.message : String(e) } };
        }
    }
    async call(name, args) {
        try {
            return { ok: true, backend: 'official-mcp', data: await (await this.connect()).callTool({ name, arguments: args }) };
        }
        catch (e) {
            return { ok: false, backend: 'official-mcp', error: { code: 'mcp_error', message: e instanceof Error ? e.message : String(e) } };
        }
    }
}
//# sourceMappingURL=official-mcp.js.map