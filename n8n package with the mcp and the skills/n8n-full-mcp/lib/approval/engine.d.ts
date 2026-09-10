import type { Operation } from '../types.js';
export declare class ApprovalEngine {
    private ttlMs;
    private records;
    constructor(ttlMs?: number);
    describe(o: Operation): {
        approvalRequired: boolean;
        prompt: string;
        target: string;
        resource: string;
        operation: string;
        parameters: Record<string, unknown>;
        expectedResult: string;
        persistent: boolean;
        externalEffects: string[];
        risk: import("../types.js").Risk;
    };
    issue(o: Operation, answer: string): {
        approvalToken: string;
        expiresAt: number;
        operationDigest: string;
    };
    consume(o: Operation, token?: string): void;
}
