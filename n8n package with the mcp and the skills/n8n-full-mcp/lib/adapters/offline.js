import { mkdir, readdir, readFile, writeFile, rm } from 'node:fs/promises';
import path from 'node:path';
const safe = (root, p) => {
    const full = path.resolve(root, p);
    if (full !== root && !full.startsWith(root + path.sep))
        throw new Error('Path traversal rejected');
    return full;
};
export class OfflineAdapter {
    root;
    constructor(root) {
        this.root = root;
    }
    available() { return true; }
    async list() {
        await mkdir(this.root, { recursive: true });
        const files = (await readdir(this.root)).filter(x => x.endsWith('.json'));
        return { ok: true, backend: 'offline', data: await Promise.all(files.map(async (f) => {
                const x = JSON.parse(await readFile(safe(this.root, f), 'utf8'));
                return { id: x.id ?? f.slice(0, -5), name: x.name ?? f, file: f, active: x.active ?? false };
            })) };
    }
    async get(id) {
        try {
            return { ok: true, backend: 'offline', data: JSON.parse(await readFile(safe(this.root, `${id}.json`), 'utf8')) };
        }
        catch (e) {
            return { ok: false, backend: 'offline', error: { code: 'not_found', message: e instanceof Error ? e.message : String(e) } };
        }
    }
    async put(id, data) {
        await mkdir(this.root, { recursive: true });
        await writeFile(safe(this.root, `${id}.json`), JSON.stringify(data, null, 2), { flag: 'wx' });
        return { ok: true, backend: 'offline', data: { id, file: `${id}.json` } };
    }
    async replace(id, data) {
        await mkdir(this.root, { recursive: true });
        await writeFile(safe(this.root, `${id}.json`), JSON.stringify(data, null, 2));
        return { ok: true, backend: 'offline', data: { id } };
    }
    async delete(id) {
        await rm(safe(this.root, `${id}.json`));
        return { ok: true, backend: 'offline', data: { deleted: id } };
    }
}
//# sourceMappingURL=offline.js.map