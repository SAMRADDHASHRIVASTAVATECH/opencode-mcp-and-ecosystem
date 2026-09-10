import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
function find(names) { for (const n of names)
    try {
        return execFileSync(process.platform === 'win32' ? 'where.exe' : 'which', [n], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).split(/\r?\n/)[0].trim();
    }
    catch { } if (process.platform === 'win32') {
    const roots = [process.env.ProgramFiles, process.env['ProgramFiles(x86)'], process.env.LOCALAPPDATA].filter(Boolean);
    for (const r of roots)
        for (const n of names)
            for (const d of ['Oracle/VirtualBox', 'VMware/VMware Workstation', 'qemu']) {
                const p = path.join(r, d, n);
                if (existsSync(p))
                    return p;
            }
} }
function ver(exe, args = ['--version']) { if (!exe)
    return; try {
    return execFileSync(exe, args, { encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'pipe'] }).split(/\r?\n/)[0];
}
catch {
    return 'unknown';
} }
export function platforms() {
    const vbox = find(['VBoxManage.exe', 'VBoxManage']), vmrun = find(['vmrun.exe', 'vmrun']), virsh = find(['virsh.exe', 'virsh']), wsl = find(['wsl.exe']), ps = find(['pwsh.exe', 'powershell.exe', 'pwsh', 'powershell']);
    let hyper = false;
    if (ps)
        try {
            hyper = execFileSync(ps, ['-NoProfile', '-Command', "[bool](Get-Module -ListAvailable Hyper-V)"], { encoding: 'utf8', timeout: 5000 }).trim().toLowerCase() === 'true';
        }
        catch { }
    ;
    return [
        { id: 'virtualbox', state: vbox ? 'AVAILABLE' : 'NOT_DETECTED', executable: vbox, version: ver(vbox, ['--version']), capabilities: ['list', 'inspect', 'start', 'shutdown', 'poweroff', 'pause', 'resume', 'reset', 'save', 'snapshot', 'clone', 'create', 'configure', 'import', 'export'], guestControl: ['Guest Additions guestcontrol', 'SSH'], notes: ['Guestcontrol needs running VM, Guest Additions and guest credentials; prefer passwordfile, never command-line password.'] },
        { id: 'hyperv', state: hyper ? 'AVAILABLE' : 'NOT_DETECTED', executable: hyper ? ps : undefined, version: hyper ? ver(ps, ['-NoProfile', '-Command', '(Get-Module -ListAvailable Hyper-V|Sort Version -Descending|Select -First 1).Version.ToString()']) : undefined, capabilities: ['list', 'inspect', 'start', 'stop', 'checkpoint', 'restore', 'create', 'configure', 'import', 'export'], guestControl: ['PowerShell Direct for compatible Windows guests', 'SSH', 'WinRM', 'Guest Service Interface file copy'], notes: ['Often requires elevated Hyper-V permissions. PowerShell Direct requires Windows guest and credentials.'] },
        { id: 'vmware', state: vmrun ? 'AVAILABLE' : 'NOT_DETECTED', executable: vmrun, version: ver(vmrun), capabilities: ['running-list', 'start', 'stop', 'suspend', 'reset', 'snapshot', 'clone'], guestControl: ['VMware Tools vmrun', 'SSH', 'WinRM'], notes: ['Inventory of powered-off VMs requires configured search paths; guest vmrun operations require VMware Tools and credentials.'] },
        { id: 'libvirt', state: virsh ? 'AVAILABLE' : 'NOT_DETECTED', executable: virsh, version: ver(virsh, ['--version']), capabilities: ['list', 'inspect', 'start', 'shutdown', 'destroy', 'reboot', 'suspend', 'resume', 'snapshot', 'define', 'undefine'], guestControl: ['QEMU Guest Agent metadata', 'SSH', 'WinRM'], notes: ['Guest arbitrary command execution is not assumed from QEMU Guest Agent. Prefer SSH/WinRM.'] },
        { id: 'wsl', state: wsl ? 'AVAILABLE' : 'NOT_DETECTED', executable: wsl, version: ver(wsl, ['--version']), capabilities: ['list', 'start', 'terminate', 'shutdown-all', 'import', 'export', 'unregister', 'resize'], guestControl: ['wsl.exe direct exec', 'wsl.exe file path bridge'], notes: ['WSL is a managed Linux environment, not a full independent VM management surface. unregister deletes distro data.'] }
    ];
}
function parseVBox(text) { return [...text.matchAll(/^"(.*)" \{([^}]+)\}$/gm)].map(m => ({ id: m[2], name: m[1], platform: 'virtualbox', state: 'unknown', guestControl: ['guestcontrol', 'ssh'], snapshots: true })); }
export function listVMs() { const out = []; for (const p of platforms().filter(x => x.state === 'AVAILABLE'))
    try {
        if (p.id === 'virtualbox') {
            const all = parseVBox(execFileSync(p.executable, ['list', 'vms'], { encoding: 'utf8' }));
            const running = new Set(parseVBox(execFileSync(p.executable, ['list', 'runningvms'], { encoding: 'utf8' })).map(x => x.id));
            all.forEach(x => { x.state = running.has(x.id) ? 'running' : 'powered_off'; out.push(x); });
        }
        else if (p.id === 'wsl') {
            const lines = execFileSync(p.executable, ['--list', '--verbose'], { encoding: 'utf16le' }).replaceAll('\0', '').split(/\r?\n/).slice(1);
            for (const l of lines) {
                const m = l.trim().replace(/^\*\s*/, '').match(/^(.*?)\s{2,}(Running|Stopped)\s+(\d+)$/i);
                if (m)
                    out.push({ id: m[1], name: m[1], platform: 'wsl', state: m[2].toLowerCase(), os: 'Linux', guestControl: ['direct'], snapshots: false });
            }
        }
        else if (p.id === 'hyperv') {
            const data = JSON.parse(execFileSync(p.executable, ['-NoProfile', '-Command', 'Get-VM|Select Name,Id,State,ProcessorCount,MemoryAssigned|ConvertTo-Json'], { encoding: 'utf8' }) || '[]');
            for (const x of (Array.isArray(data) ? data : [data]))
                out.push({ id: String(x.Id), name: x.Name, platform: 'hyperv', state: String(x.State), cpus: x.ProcessorCount, memoryMB: Math.round(x.MemoryAssigned / 1048576), guestControl: ['powershell-direct', 'ssh', 'winrm'], snapshots: true });
        }
        else if (p.id === 'libvirt') {
            for (const l of execFileSync(p.executable, ['list', '--all', '--name'], { encoding: 'utf8' }).trim().split(/\r?\n/).filter(Boolean))
                out.push({ id: l, name: l, platform: 'libvirt', state: 'unknown', guestControl: ['ssh'], snapshots: true });
        }
        else if (p.id === 'vmware') {
            const lines = execFileSync(p.executable, ['list'], { encoding: 'utf8' }).split(/\r?\n/).slice(1).filter(Boolean);
            for (const f of lines)
                out.push({ id: f, name: path.basename(f, '.vmx'), platform: 'vmware', state: 'running', configPath: f, guestControl: ['vmrun-tools', 'ssh', 'winrm'], snapshots: true });
        }
    }
    catch { } return out; }
//# sourceMappingURL=platforms.js.map