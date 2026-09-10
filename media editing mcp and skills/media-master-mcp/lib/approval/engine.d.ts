import type { MediaPlan } from '../types.js';
export declare function planDigest(p: Omit<MediaPlan, 'digest'>): string;
export declare class Approval {
    private tokens;
    issue(p: MediaPlan, confirmation: string): {
        token: string;
        planId: string;
        digest: string;
        expiresAt: number;
    };
    consume(p: MediaPlan, token: string): void;
}
