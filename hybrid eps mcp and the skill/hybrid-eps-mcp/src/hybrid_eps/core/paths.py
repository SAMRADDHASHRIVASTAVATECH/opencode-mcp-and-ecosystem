from pathlib import Path
import os
ROOT=Path(os.environ.get('HYBRID_EPS_ROOT',Path.cwd())).resolve()
def safe_path(value:str,exists=False)->Path:
 p=(ROOT/value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
 try:p.relative_to(ROOT)
 except ValueError:raise ValueError(f'path outside HYBRID_EPS_ROOT: {p}')
 if exists and not p.is_file():raise FileNotFoundError(p)
 return p
