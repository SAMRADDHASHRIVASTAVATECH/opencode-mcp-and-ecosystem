export declare function waitPort(host: string, port: number, timeoutMs?: number, interval?: number): Promise<{
    ready: boolean;
    host: string;
    port: number;
    elapsedMs: number;
    error?: undefined;
} | {
    ready: boolean;
    host: string;
    port: number;
    error: string;
    elapsedMs?: undefined;
}>;
