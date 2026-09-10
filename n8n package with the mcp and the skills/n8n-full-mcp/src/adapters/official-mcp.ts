import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import type { Config, ToolResult } from '../types.js';

export class OfficialMcpAdapter {
  private client?: Client;
  constructor(private c: Config) {}
  available() { return !!this.c.officialMcpUrl; }
  private async connect() {
    if (this.client) return this.client;
    const headers: Record<string, string> = this.c.officialMcpToken ? { Authorization: `Bearer ${this.c.officialMcpToken}` } : {};
    const transport = new StreamableHTTPClientTransport(new URL(this.c.officialMcpUrl!), { requestInit: { headers } });
    this.client = new Client({ name: 'n8n-full-mcp-proxy', version: '0.1.0' });
    await this.client.connect(transport);
    return this.client;
  }
  async listTools(): Promise<ToolResult> {
    try { return { ok: true, backend: 'official-mcp', data: await (await this.connect()).listTools() }; }
    catch (e) { return { ok: false, backend: 'official-mcp', error: { code: 'mcp_error', message: e instanceof Error ? e.message : String(e) } }; }
  }
  async call(name: string, args: Record<string, unknown>): Promise<ToolResult> {
    try { return { ok: true, backend: 'official-mcp', data: await (await this.connect()).callTool({ name, arguments: args }) }; }
    catch (e) { return { ok: false, backend: 'official-mcp', error: { code: 'mcp_error', message: e instanceof Error ? e.message : String(e) } }; }
  }
}
