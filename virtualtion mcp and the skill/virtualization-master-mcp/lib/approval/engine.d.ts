import type { Plan } from '../types.js';
export declare function digest(p: Omit<Plan, 'digest'>): string;
export declare class Approval {
    m: Map<string, {
        d: string;
        e: number;
        u: boolean;
    }>;
    issue(p: Plan, a: string): {
        token: string;
        digest: string;
        expiresAt: number;
    };
    consume(p: Plan, t: string): void;
}
