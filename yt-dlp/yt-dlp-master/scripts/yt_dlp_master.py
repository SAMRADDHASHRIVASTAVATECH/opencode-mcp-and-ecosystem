#!/usr/bin/env python3
"""Capability-aware, approval-gated yt-dlp planner/executor. Python 3.10+."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

SECRET_FLAGS={'--password','-p','--video-password','--ap-password','--netrc-cmd','--add-headers','--cookies','--cookies-from-browser','--proxy'}
WRITE_FLAGS={'--write-subs','--write-auto-subs','--write-thumbnail','--write-all-thumbnails','--write-info-json','--download-archive','--exec','--embed-subs','--embed-thumbnail','--embed-metadata','--split-chapters','--remove-chapters','--update','-U'}

def run(argv, timeout=30):
    try:
        p=subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout, shell=False)
        return {'ok':p.returncode==0,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except FileNotFoundError as e:return {'ok':False,'code':127,'stdout':'','stderr':str(e)}
    except subprocess.TimeoutExpired as e:return {'ok':False,'code':124,'stdout':e.stdout or '','stderr':'Timed out'}

def which_all(name):
    found=[]
    p=shutil.which(name)
    if p:found.append(str(Path(p).resolve()))
    if platform.system()=='Windows':
        roots=[os.getenv('LOCALAPPDATA',''),os.getenv('APPDATA',''),os.getenv('USERPROFILE','')]
        for root in roots:
            for rel in ('Programs/yt-dlp/yt-dlp.exe','scoop/shims/yt-dlp.exe','AppData/Local/Microsoft/WinGet/Links/yt-dlp.exe'):
                q=Path(root)/rel
                if q.exists():found.append(str(q.resolve()))
    return list(dict.fromkeys(found))

def config_candidates():
    home=Path.home(); appdata=os.getenv('APPDATA'); programdata=os.getenv('PROGRAMDATA')
    c=[Path.cwd()/'yt-dlp.conf',home/'yt-dlp.conf',home/'.config/yt-dlp/config',home/'.config/yt-dlp/config.txt']
    if appdata:c += [Path(appdata)/'yt-dlp/config',Path(appdata)/'yt-dlp/config.txt']
    if programdata:c += [Path(programdata)/'yt-dlp/config',Path(programdata)/'yt-dlp/config.txt']
    return [str(x) for x in c]

def redact_args(args):
    out=[]; hide=False
    for a in args:
        if hide:out.append('[REDACTED]');hide=False;continue
        shown=a
        if isinstance(a,str) and re.match(r'https?://',a,re.I) and ('?' in a or '#' in a):
            shown=re.split(r'[?#]',a,maxsplit=1)[0]+'?[REDACTED]'
        out.append(shown)
        if a in SECRET_FLAGS:hide=True
        elif any(a.startswith(f+'=') for f in SECRET_FLAGS):out[-1]=a.split('=',1)[0]+'=[REDACTED]'
    return out

def discover():
    bins=which_all('yt-dlp') or which_all('yt-dlp.exe'); exe=bins[0] if bins else None
    ver=run([exe,'--version'])['stdout'].strip() if exe else None
    help_text=run([exe,'--help'],timeout=20)['stdout'] if exe else ''
    ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');py=shutil.which('python') or shutil.which('python3')
    configs=[{'path':p,'exists':Path(p).exists()} for p in config_candidates()]
    plugin_roots=[]
    for p in [Path.home()/'.config/yt-dlp/plugins',Path.home()/'yt_dlp_plugins']:
        if p.exists():plugin_roots.append(str(p))
    status=lambda supported,available,req=None:{'supported':supported,'available_locally':available,'requirement':req}
    return {'host':{'os':platform.system(),'version':platform.version(),'architecture':platform.machine(),'python':sys.version.split()[0]},'yt_dlp':{'status':'AVAILABLE LOCALLY' if exe else 'NOT AVAILABLE','executables':bins,'selected':exe,'version':ver,'option_count':len(set(re.findall(r'(?<!\w)--[a-z0-9][a-z0-9-]+',help_text))),'supports':{x:(x in help_text) for x in ['--dump-single-json','--list-formats','--list-subs','--cookies-from-browser','--download-archive','--sponsorblock-mark','--concurrent-fragments','--update-to','--use-postprocessor']}},'dependencies':{'ffmpeg':status(True,bool(ffmpeg),'install FFmpeg for merging/post-processing'),'ffprobe':status(True,bool(ffprobe),'install FFprobe for media inspection'),'python':status(True,bool(py)),'git':status(False,bool(shutil.which('git')))},'configs':configs,'plugins':{'detected_roots':plugin_roots,'status':'UNKNOWN' if not exe else 'inspect --verbose without printing secrets'},'network':{'required_for_url_inspection_and_download':True,'proxy_environment_present':any(k.lower() in {'http_proxy','https_proxy','all_proxy'} for k in os.environ)}}

def format_selector(p):
    if p.get('audio_only'):return 'bestaudio/best'
    h=p.get('max_height'); container=p.get('container'); codec=p.get('codec'); max_size=p.get('max_filesize')
    filters=[]
    if h:filters.append(f'height<={int(h)}')
    if max_size:filters.append(f'filesize<={max_size}')
    vfilter=''.join(f'[{x}]' for x in filters)
    if codec=='h264':vfilter += "[vcodec~='^(avc|h264)']"
    elif codec=='av1':vfilter += "[vcodec~='^(av01|av1)']"
    elif codec=='vp9':vfilter += "[vcodec~='^vp0?9']"
    if container=='mp4':return f"bv*[ext=mp4]{vfilter}+ba[ext=m4a]/b[ext=mp4]{vfilter}/bv*{vfilter}+ba/b"
    return f'bv*{vfilter}+ba/b{vfilter}/b'

def build_plan(req):
    url=req.get('url'); urls=req.get('urls') or ([url] if url else [])
    if not urls and not req.get('batch_file'):raise ValueError('url, urls, or batch_file is required')
    exe=(discover()['yt_dlp']['selected'] or 'yt-dlp'); args=[exe]
    kind=req.get('operation','video'); outdir=req.get('output_dir') or str(Path.home()/'Downloads')
    template=req.get('output_template') or ('%(uploader)s/%(playlist)s/%(playlist_index)03d - %(title)s [%(id)s].%(ext)s' if req.get('playlist') or req.get('channel') else '%(uploader)s/%(title)s [%(id)s].%(ext)s')
    args += ['--paths',outdir,'--output',template,'--windows-filenames' if platform.system()=='Windows' else '--trim-filenames','180']
    if kind=='metadata':args += ['--dump-single-json','--skip-download']
    elif kind=='formats':args += ['--list-formats','--simulate']
    elif kind=='subtitles':
        args += ['--skip-download','--write-auto-subs' if req.get('automatic_subtitles') else '--write-subs','--sub-langs',req.get('subtitle_languages','en.*')]
        if req.get('subtitle_format'):args += ['--convert-subs',req['subtitle_format']]
    elif kind=='thumbnail':args += ['--skip-download','--write-thumbnail']
    elif kind=='audio':
        args += ['--format',format_selector({'audio_only':True}),'--extract-audio','--audio-format',req.get('audio_format','mp3'),'--audio-quality',str(req.get('audio_quality','0'))]
    else:
        args += ['--format',format_selector(req)]
        if req.get('container'):args += ['--merge-output-format',req['container']]
        if req.get('remux'):args += ['--remux-video',req['remux']]
        if req.get('recode'):args += ['--recode-video',req['recode']]
    if req.get('subtitles'):
        args += ['--write-subs','--sub-langs',req.get('subtitle_languages','en.*')]
        if req.get('automatic_subtitles'):args += ['--write-auto-subs']
        if req.get('embed_subtitles'):args += ['--embed-subs']
    if req.get('thumbnail'):args += ['--write-thumbnail']
    if req.get('embed_thumbnail'):args += ['--embed-thumbnail']
    if req.get('embed_metadata'):args += ['--embed-metadata']
    if req.get('embed_chapters'):args += ['--embed-chapters']
    if req.get('sponsorblock_mark'):args += ['--sponsorblock-mark',req.get('sponsorblock_categories','all')]
    if req.get('sponsorblock_remove'):args += ['--sponsorblock-remove',req.get('sponsorblock_categories','sponsor')]
    if req.get('archive'):args += ['--download-archive',req['archive']]
    if req.get('playlist_items'):args += ['--playlist-items',str(req['playlist_items'])]
    if req.get('dateafter'):args += ['--dateafter',str(req['dateafter'])]
    if req.get('datebefore'):args += ['--datebefore',str(req['datebefore'])]
    if req.get('match_filter'):args += ['--match-filter',req['match_filter']]
    if req.get('retries') is not None:args += ['--retries',str(req['retries'])]
    if req.get('fragment_retries') is not None:args += ['--fragment-retries',str(req['fragment_retries'])]
    if req.get('concurrent_fragments'):args += ['--concurrent-fragments',str(req['concurrent_fragments'])]
    if req.get('rate_limit'):args += ['--limit-rate',str(req['rate_limit'])]
    if req.get('proxy'):args += ['--proxy',req['proxy']]
    if req.get('cookies_from_browser'):args += ['--cookies-from-browser',req['cookies_from_browser']]
    if req.get('cookies_file'):args += ['--cookies',req['cookies_file']]
    if req.get('batch_file'):args += ['--batch-file',req['batch_file']]
    else:args += list(map(str,urls))
    consequential=kind not in {'metadata','formats'} or any(x in args for x in WRITE_FLAGS) or any(x in args for x in SECRET_FLAGS)
    deps=[]
    if any(x in args for x in ['--extract-audio','--merge-output-format','--remux-video','--recode-video','--embed-subs','--embed-thumbnail','--convert-subs','--split-chapters']):deps += ['ffmpeg','ffprobe']
    if req.get('cookies_from_browser') or req.get('cookies_file'):deps += ['authorized cookie access']
    scope='batch/playlist/channel' if req.get('playlist') or req.get('channel') or req.get('batch_file') else 'single/multiple URLs'
    plan={'schema':1,'created_at':int(time.time()),'operation':kind,'target_count':len(urls) if urls else 'batch-file','scope':scope,'output_location':outdir,'important_parameters':{k:v for k,v in req.items() if k not in {'proxy','cookies_file','cookies_from_browser'}},'dependencies':deps,'persistent_effects':['writes media/metadata files'] if consequential else [],'external_effects':['network requests to media site/CDNs'],'command':args,'redacted_command':redact_args(args),'approval_required':consequential}
    plan['digest']=hashlib.sha256(json.dumps({k:v for k,v in plan.items() if k!='digest'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return plan

def execute_plan(path,approval):
    plan=json.loads(Path(path).read_text(encoding='utf-8')); saved=plan.pop('digest'); digest=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if saved!=digest:raise PermissionError('Plan was modified after review')
    if plan['approval_required'] and approval!=saved:raise PermissionError('Exact plan approval digest is missing or mismatched')
    exe=plan['command'][0]
    if exe=='yt-dlp' and not shutil.which(exe):raise RuntimeError('yt-dlp is not installed or not on PATH')
    for dep in plan['dependencies']:
        if dep in {'ffmpeg','ffprobe'} and not shutil.which(dep):raise RuntimeError(f'{dep} is required but unavailable')
    started=time.time(); result=run(plan['command'],timeout=24*3600); result['duration_seconds']=round(time.time()-started,3); result['command']=plan['redacted_command']; return result

def diagnose(text):
    tests=[('authentication',r'login|sign in|cookies|authentication|private video','Use authorized browser cookies/cookie file; never bypass access controls.'),('drm',r'\bDRM\b|encrypted media','DRM-protected content is outside the skill boundary.'),('format',r'requested format.*not available|no video formats','Inspect formats and revise the selector.'),('ffmpeg',r'ffmpeg|ffprobe','Install/detect FFmpeg or remove merge/conversion/embed operations.'),('network',r'timed? out|connection|proxy|http error 429|429','Check network/proxy, rate limits, retries, and sleep intervals.'),('extractor',r'unsupported url|no suitable extractor','Check installed extractors/version; separate web URL discovery from yt-dlp.'),('filesystem',r'permission denied|file name too long|invalid argument|no space','Check output path, permissions, free space, and Windows filename/long-path behavior.'),('availability',r'private|unavailable|removed|geo','Content availability or authorization restriction; do not bypass it.')]
    for layer,pat,fix in tests:
        if re.search(pat,text,re.I):return {'layer':layer,'recommendation':fix}
    return {'layer':'unknown','recommendation':'Run yt-dlp --verbose with secrets redacted; check version, extractor, URL, dependencies, network and output path.'}

def main(argv=None):
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    sp.add_parser('discover'); p=sp.add_parser('plan');p.add_argument('--request',required=True);p.add_argument('--out',required=True)
    e=sp.add_parser('execute');e.add_argument('--plan',required=True);e.add_argument('--approval')
    d=sp.add_parser('diagnose');d.add_argument('--text',required=True)
    args=ap.parse_args(argv)
    try:
        if args.cmd=='discover':result=discover()
        elif args.cmd=='plan':
            req=json.loads(Path(args.request).read_text(encoding='utf-8'));result=build_plan(req);Path(args.out).write_text(json.dumps(result,indent=2),encoding='utf-8');result={'plan':args.out,'digest':result['digest'],'approval_required':result['approval_required'],'review':{k:result[k] for k in ('operation','scope','output_location','important_parameters','dependencies','persistent_effects','external_effects','redacted_command')}}
        elif args.cmd=='execute':result=execute_plan(args.plan,args.approval)
        else:result=diagnose(args.text)
        print(json.dumps({'ok':True,'data':result},indent=2));return 0
    except Exception as e:print(json.dumps({'ok':False,'error':{'type':type(e).__name__,'message':str(e)}},indent=2));return 1
if __name__=='__main__':raise SystemExit(main())
