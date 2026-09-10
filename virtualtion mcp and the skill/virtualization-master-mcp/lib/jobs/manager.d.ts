import type { Plan } from '../types.js';
export declare class Jobs {
    m: Map<string, any>;
    start(p: Plan): any;
    get(id: string): any;
    list(): any[];
    cancel(id: string): any;
}
