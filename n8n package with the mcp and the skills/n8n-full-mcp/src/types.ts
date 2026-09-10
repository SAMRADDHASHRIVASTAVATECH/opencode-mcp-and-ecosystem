export type Mode='online'|'offline'|'local';
export type Risk='read'|'write'|'execute'|'destructive'|'admin';
export interface Config{mode:Mode;baseUrl?:string;apiKey?:string;officialMcpUrl?:string;officialMcpToken?:string;offlineDir:string;allowInsecureLocalhost:boolean;approvalTtlMs:number;timeoutMs:number;auditFile:string}
export interface ToolResult{ok:boolean;backend:string;data?:unknown;error?:{code:string;message:string;status?:number;details?:unknown};meta?:Record<string,unknown>}
export interface Operation{target:string;resource:string;operation:string;parameters:Record<string,unknown>;expectedResult:string;persistent:boolean;externalEffects:string[];risk:Risk}
export interface ApprovalRecord{token:string;digest:string;expiresAt:number;used:boolean}
export interface Capability{capability:string;officialMcp?:string;api?:string;offline?:boolean;write:boolean;minVersion?:string;notes?:string}
