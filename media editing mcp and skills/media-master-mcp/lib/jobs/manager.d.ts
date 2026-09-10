import type { Job, MediaPlan } from '../types.js';
export declare class Jobs {
    private jobs;
    private children;
    start(p: MediaPlan, timeoutMs: number): Job;
    get(id: string): Job;
    list(): Job[];
    cancel(id: string): Job;
}
