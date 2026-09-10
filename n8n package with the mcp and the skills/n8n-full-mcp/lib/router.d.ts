import type { Config, ToolResult } from './types.js';
import { RestAdapter } from './adapters/rest.js';
import { OfflineAdapter } from './adapters/offline.js';
import { OfficialMcpAdapter } from './adapters/official-mcp.js';
export declare class Router {
    config: Config;
    rest: RestAdapter;
    offline: OfflineAdapter;
    official: OfficialMcpAdapter;
    constructor(config: Config);
    read(officialTool: string | undefined, args: Record<string, unknown>, api?: {
        path: string;
        query?: Record<string, unknown>;
    }, offline?: () => Promise<ToolResult>): Promise<ToolResult>;
    write(officialTool: string | undefined, args: Record<string, unknown>, api?: {
        method: string;
        path: string;
        body?: unknown;
    }, offline?: () => Promise<ToolResult>): Promise<ToolResult>;
}
