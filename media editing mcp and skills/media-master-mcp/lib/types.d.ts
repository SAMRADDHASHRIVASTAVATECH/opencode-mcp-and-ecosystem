export type ToolId = 'ffmpeg' | 'ffprobe' | 'magick' | 'exiftool' | 'ytdlp';
export interface Capability {
    id: ToolId;
    available: boolean;
    executable?: string;
    version?: string;
    operations: string[];
    notes: string[];
}
export interface MediaPlan {
    id: string;
    operation: string;
    inputs: string[];
    outputs: string[];
    argv: string[];
    executable: string;
    network: boolean;
    overwrite: boolean;
    persistentEffects: string[];
    potentialDataLoss: string[];
    verification: string[];
    createdAt: number;
    digest: string;
}
export interface Job {
    id: string;
    planId: string;
    operation: string;
    status: 'running' | 'completed' | 'failed' | 'cancelled' | 'timed_out';
    stdout: string;
    stderr: string;
    startedAt: number;
    completedAt?: number;
    exitCode?: number | null;
    pid?: number;
}
