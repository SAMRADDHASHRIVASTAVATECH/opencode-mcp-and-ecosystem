import { execFileSync } from 'node:child_process';
function find(names) { for (const n of names)
    try {
        return execFileSync(process.platform === 'win32' ? 'where.exe' : 'which', [n], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).split(/\r?\n/)[0].trim();
    }
    catch { } }
function version(exe, args = ['--version']) { if (!exe)
    return; try {
    return execFileSync(exe, args, { encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'pipe'] }).split(/\r?\n/)[0].trim();
}
catch {
    return 'unknown';
} }
export function capabilities() { const defs = [['ffmpeg', ['ffmpeg.exe', 'ffmpeg'], ['transcode', 'trim', 'resize-video', 'extract-audio', 'thumbnail', 'normalize-audio'], ['Uses local codecs; format support varies.']], ['ffprobe', ['ffprobe.exe', 'ffprobe'], ['probe'], ['Read-only media stream/container inspection.']], ['magick', ['magick.exe', 'magick'], ['probe-image', 'convert-image', 'resize-image', 'crop-image', 'rotate-image', 'strip-metadata'], ['ImageMagick policy may restrict formats.']], ['exiftool', ['exiftool.exe', 'exiftool'], ['read-metadata', 'write-metadata', 'strip-metadata'], ['Metadata mutation may create backups unless disabled.']], ['ytdlp', ['yt-dlp.exe', 'yt-dlp'], ['inspect-url', 'download'], ['Network use; obey site terms, copyright, and authorization.']]]; return defs.map(([id, names, operations, notes]) => { const executable = find(names); return { id, available: !!executable, executable, version: version(executable, id === 'magick' ? ['-version'] : ['--version']), operations, notes }; }); }
//# sourceMappingURL=tools.js.map