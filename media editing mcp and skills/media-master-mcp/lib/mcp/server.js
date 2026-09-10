import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { execFileSync } from 'node:child_process';
import { statSync } from 'node:fs';
import { z } from 'zod';
import { capabilities } from '../discovery/tools.js';
import { safePath, root } from '../security/paths.js';
import { makePlan } from '../planner/planner.js';
import { Approval } from '../approval/engine.js';
import { Jobs } from '../jobs/manager.js';
const out = (x) => ({ content: [{ type: 'text', text: JSON.stringify(x, null, 2) }] });
const plans = new Map(), approvals = new Approval(), jobs = new Jobs();
export async function createServer() { const s = new McpServer({ name: 'media-master', version: '1.0.0' }); s.tool('get_media_capabilities', 'Discover installed media backends and truthful operations.', {}, async () => out({ mediaRoot: root(), backends: capabilities() })); s.tool('probe_media', 'Read local media metadata without mutation.', { path: z.string() }, async (a) => { const p = safePath(a.path, true), cs = capabilities(), ff = cs.find(x => x.id === 'ffprobe' && x.available), im = cs.find(x => x.id === 'magick' && x.available); let metadata = { path: p, bytes: statSync(p).size }; if (ff)
    try {
        metadata = JSON.parse(execFileSync(ff.executable, ['-v', 'error', '-show_format', '-show_streams', '-of', 'json', p], { encoding: 'utf8', timeout: 30000, maxBuffer: 5_000_000 }));
    }
    catch { }
else if (im)
    try {
        metadata = { path: p, bytes: statSync(p).size, identify: execFileSync(im.executable, ['identify', '-verbose', p], { encoding: 'utf8', timeout: 30000, maxBuffer: 2_000_000 }) };
    }
    catch { } return out(metadata); }); s.tool('plan_media_operation', 'Create exact non-executing plan for image conversion/resize/metadata stripping, transcode/trim/audio extraction/thumbnail, or authorized HTTPS download.', { operation: z.enum(['convert_image', 'resize_image', 'strip_image_metadata', 'transcode', 'trim', 'extract_audio', 'thumbnail', 'download']), input: z.string().optional(), output: z.string().optional(), parameters: z.record(z.unknown()).default({}) }, async (a) => { const p = makePlan(a); plans.set(p.id, p); return out(p); }); s.tool('approve_media_operation', 'Issue a 60-second single-use token after explicit approval of exact plan.', { planId: z.string(), explicitApproval: z.string() }, async (a) => { const p = plans.get(a.planId); if (!p)
    throw Error('PLAN_NOT_FOUND'); return out(approvals.issue(p, a.explicitApproval)); }); s.tool('execute_media_operation', 'Execute an approved unchanged plan as a bounded job.', { planId: z.string(), approvalToken: z.string(), timeoutMs: z.number().int().min(1000).max(3_600_000).default(300_000) }, async (a) => { const p = plans.get(a.planId); if (!p)
    throw Error('PLAN_NOT_FOUND'); approvals.consume(p, a.approvalToken); return out(jobs.start(p, a.timeoutMs)); }); s.tool('get_media_job', 'Get job status, bounded logs, exit code, and verification.', { jobId: z.string() }, async (a) => out(jobs.get(a.jobId))); s.tool('list_media_jobs', 'List jobs for this server process.', {}, async () => out(jobs.list())); s.tool('cancel_media_job', 'Cancel a running job.', { jobId: z.string(), explicitConfirmation: z.literal('CANCEL') }, async (a) => out(jobs.cancel(a.jobId))); return s; }
export async function run() { const s = await createServer(); await s.connect(new StdioServerTransport()); }
//# sourceMappingURL=server.js.map