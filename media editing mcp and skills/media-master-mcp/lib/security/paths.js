import path from 'node:path';
import { existsSync, realpathSync } from 'node:fs';
const ROOT = realpathSync(process.env.MEDIA_MCP_ROOT || process.cwd());
export function safePath(v, mustExist = false) { if (!v || v.includes('\0'))
    throw Error('INVALID_PATH'); const p = path.resolve(ROOT, v); const parent = existsSync(p) ? realpathSync(p) : realpathSync(path.dirname(p)); if (parent !== ROOT && !parent.startsWith(ROOT + path.sep))
    throw Error('PATH_OUTSIDE_MEDIA_ROOT'); if (mustExist && !existsSync(p))
    throw Error('INPUT_NOT_FOUND'); return p; }
export function root() { return ROOT; }
//# sourceMappingURL=paths.js.map