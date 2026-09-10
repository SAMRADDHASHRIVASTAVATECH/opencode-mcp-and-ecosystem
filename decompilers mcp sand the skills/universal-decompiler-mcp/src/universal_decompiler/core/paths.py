from pathlib import Path
import os
TARGET_ROOT=Path(os.environ.get('DECOMPILER_TARGET_ROOT','/home/user/decompiler-targets')).resolve();ANALYSIS_ROOT=Path(os.environ.get('DECOMPILER_ANALYSIS_ROOT','/home/user/decompiler-analysis')).resolve();TOOL_ROOT=Path(os.environ.get('DECOMPILER_TOOL_ROOT','/home/user/decompiler-tools')).resolve()
for p in (TARGET_ROOT,ANALYSIS_ROOT,TOOL_ROOT):p.mkdir(parents=True,exist_ok=True)
def within(value:str,root:Path,exists=False):
 p=Path(value);p=(root/p).resolve() if not p.is_absolute() else p.resolve()
 try:p.relative_to(root)
 except ValueError:raise ValueError(f'path outside authorized root {root}')
 if exists and not p.is_file():raise FileNotFoundError(p)
 return p
