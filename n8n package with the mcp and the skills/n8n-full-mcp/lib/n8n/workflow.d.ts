export declare function validateWorkflow(w: any): {
    valid: boolean;
    errors: string[];
    warnings: string[];
    summary?: undefined;
} | {
    valid: boolean;
    errors: string[];
    warnings: string[];
    summary: {
        nodeCount: any;
        edgeCount: number;
        nodes: any;
        edges: any[];
        triggers: any;
        externalEffectCandidates: any;
        credentialReferenceCount: any;
    };
};
export declare function analyzeWorkflow(w: any): {
    nodeCount: any;
    edgeCount: number;
    nodes: any;
    edges: any[];
    triggers: any;
    externalEffectCandidates: any;
    credentialReferenceCount: any;
};
export declare function diffWorkflows(a: any, b: any): {
    nodesAdded: unknown[];
    nodesRemoved: unknown[];
    nodesChanged: unknown[];
    connectionsChanged: boolean;
    settingsChanged: boolean;
    activationChanged: boolean;
    hashBefore: string;
    hashAfter: string;
};
export declare function simpleWorkflow(description: string, name?: string): {
    name: string;
    nodes: any[];
    connections: any;
    settings: {
        executionOrder: string;
    };
    active: boolean;
    meta: {
        draft: boolean;
        requiresNodeSchemaResolution: boolean;
        sourceDescription: string;
    };
};
