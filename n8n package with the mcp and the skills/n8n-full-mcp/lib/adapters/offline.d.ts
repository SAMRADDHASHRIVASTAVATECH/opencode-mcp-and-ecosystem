import type { ToolResult } from '../types.js';
export declare class OfflineAdapter {
    private root;
    constructor(root: string);
    available(): boolean;
    list(): Promise<ToolResult>;
    get(id: string): Promise<ToolResult>;
    put(id: string, data: unknown): Promise<ToolResult>;
    replace(id: string, data: unknown): Promise<ToolResult>;
    delete(id: string): Promise<ToolResult>;
}
