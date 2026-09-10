import { createHash, randomUUID } from 'node:crypto';
export function validateWorkflow(w) { const errors = []; const warnings = []; if (!w || typeof w !== 'object')
    return { valid: false, errors: ['Workflow must be an object'], warnings }; if (!w.name || typeof w.name !== 'string')
    errors.push('name is required'); if (!Array.isArray(w.nodes) || w.nodes.length === 0)
    errors.push('nodes must be a non-empty array'); if (!w.connections || typeof w.connections !== 'object')
    errors.push('connections object is required'); const names = new Set(); for (const [n, i] of (w.nodes ?? []).map((x, i) => [x, i])) {
    if (!n.name || !n.type)
        errors.push(`node[${i}] needs name and type`);
    if (names.has(n.name))
        errors.push(`duplicate node name: ${n.name}`);
    names.add(n.name);
    if (!Array.isArray(n.position) || n.position.length !== 2)
        warnings.push(`node ${n.name ?? i} has no valid position`);
} for (const [from, outputs] of Object.entries(w.connections ?? {})) {
    if (!names.has(from))
        errors.push(`connection source missing: ${from}`);
    for (const groups of Object.values(outputs))
        for (const group of groups ?? [])
            for (const edge of group ?? [])
                if (!names.has(edge.node))
                    errors.push(`connection target missing: ${edge.node}`);
} return { valid: errors.length === 0, errors, warnings, summary: analyzeWorkflow(w) }; }
export function analyzeWorkflow(w) { const nodes = (w.nodes ?? []).map((n) => ({ id: n.id, name: n.name, type: n.type, disabled: !!n.disabled, credentials: Object.keys(n.credentials ?? {}), expressionFields: collectExpressions(n.parameters) })); const edges = []; for (const [from, outputs] of Object.entries(w.connections ?? {}))
    for (const [type, groups] of Object.entries(outputs))
        for (const [index, group] of groups.entries())
            for (const e of group ?? [])
                edges.push({ from, to: e.node, type, output: index, input: e.index ?? 0 }); const triggers = nodes.filter((n) => /trigger|webhook/i.test(n.type)); const externals = nodes.filter((n) => /httpRequest|email|slack|gmail|database|postgres|mysql|dataTable/i.test(n.type)); return { nodeCount: nodes.length, edgeCount: edges.length, nodes, edges, triggers, externalEffectCandidates: externals, credentialReferenceCount: nodes.reduce((a, n) => a + n.credentials.length, 0) }; }
function collectExpressions(v, out = []) { if (typeof v === 'string' && v.includes('{{'))
    out.push(v);
else if (Array.isArray(v))
    v.forEach(x => collectExpressions(x, out));
else if (v && typeof v === 'object')
    Object.values(v).forEach(x => collectExpressions(x, out)); return out; }
export function diffWorkflows(a, b) { const by = (w) => new Map((w.nodes ?? []).map((n) => [n.name, n])); const A = by(a), B = by(b); const added = [...B.keys()].filter(x => !A.has(x)), removed = [...A.keys()].filter(x => !B.has(x)), changed = [...A.keys()].filter(x => B.has(x) && JSON.stringify(A.get(x)) !== JSON.stringify(B.get(x))); return { nodesAdded: added, nodesRemoved: removed, nodesChanged: changed, connectionsChanged: JSON.stringify(a.connections ?? {}) !== JSON.stringify(b.connections ?? {}), settingsChanged: JSON.stringify(a.settings ?? {}) !== JSON.stringify(b.settings ?? {}), activationChanged: a.active !== b.active, hashBefore: createHash('sha256').update(JSON.stringify(a)).digest('hex'), hashAfter: createHash('sha256').update(JSON.stringify(b)).digest('hex') }; }
export function simpleWorkflow(description, name = 'AI drafted workflow') { const lower = description.toLowerCase(); const nodes = [{ id: randomUUID(), name: lower.includes('webhook') ? 'Webhook' : 'Manual Trigger', type: lower.includes('webhook') ? 'n8n-nodes-base.webhook' : 'n8n-nodes-base.manualTrigger', typeVersion: 1, position: [0, 0], parameters: lower.includes('webhook') ? { path: `draft-${randomUUID().slice(0, 8)}`, httpMethod: 'POST' } : {} }]; if (/validate|filter/.test(lower))
    nodes.push({ id: randomUUID(), name: 'Validate Input', type: 'n8n-nodes-base.if', typeVersion: 2, position: [240, 0], parameters: { conditions: { options: {}, conditions: [] } } }); if (/store|database|table/.test(lower))
    nodes.push({ id: randomUUID(), name: 'Store Data', type: 'n8n-nodes-base.dataTable', typeVersion: 1, position: [480, 0], parameters: { operation: 'insert' } }); if (/notify|email/.test(lower))
    nodes.push({ id: randomUUID(), name: 'Notify', type: 'n8n-nodes-base.emailSend', typeVersion: 2, position: [720, 0], parameters: {} }); const connections = {}; for (let i = 0; i < nodes.length - 1; i++)
    connections[nodes[i].name] = { main: [[{ node: nodes[i + 1].name, type: 'main', index: 0 }]] }; return { name, nodes, connections, settings: { executionOrder: 'v1' }, active: false, meta: { draft: true, requiresNodeSchemaResolution: true, sourceDescription: description } }; }
//# sourceMappingURL=workflow.js.map