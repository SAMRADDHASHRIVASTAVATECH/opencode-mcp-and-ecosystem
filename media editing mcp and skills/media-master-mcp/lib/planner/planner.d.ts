import type { MediaPlan } from '../types.js';
type Request = {
    operation: string;
    input?: string;
    output?: string;
    parameters: Record<string, unknown>;
};
export declare function makePlan(r: Request): MediaPlan;
export {};
