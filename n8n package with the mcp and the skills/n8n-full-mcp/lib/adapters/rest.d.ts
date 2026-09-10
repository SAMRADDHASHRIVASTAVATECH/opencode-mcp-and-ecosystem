import type { Config, ToolResult } from '../types.js';
export declare class RestAdapter {
    private c;
    constructor(c: Config);
    available(): boolean;
    request(method: string, path: string, body?: unknown, query?: Record<string, unknown>): Promise<ToolResult>;
}
