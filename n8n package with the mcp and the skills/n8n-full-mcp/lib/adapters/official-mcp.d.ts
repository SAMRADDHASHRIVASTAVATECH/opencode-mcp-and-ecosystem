import type { Config, ToolResult } from '../types.js';
export declare class OfficialMcpAdapter {
    private c;
    private client?;
    constructor(c: Config);
    available(): boolean;
    private connect;
    listTools(): Promise<ToolResult>;
    call(name: string, args: Record<string, unknown>): Promise<ToolResult>;
}
