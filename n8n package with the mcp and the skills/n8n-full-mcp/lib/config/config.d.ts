import type { Config } from '../types.js';
export declare function loadConfig(env?: NodeJS.ProcessEnv): Config;
export declare function assertEndpoint(c: Config): void;
