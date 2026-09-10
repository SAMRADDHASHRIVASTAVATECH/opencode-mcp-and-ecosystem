import sys,importlib.util,json
from .config import Config
from .capture.backends import create_capture
from .windows.win32 import create_windows
from .input.win32 import create_input
def main():
 checks={'python':sys.version,'platform':sys.platform,'windows_live_ready':sys.platform=='win32'}
 for p in ['numpy','PIL','fastmcp','mss','win32gui','pywinauto','pyautogui','dxcam','pytesseract']:checks[p]=importlib.util.find_spec(p) is not None
 try:
  w=create_windows();checks['active_window']=w.active().title;checks['window_provider']=type(w).__name__
  i=create_input();checks['input_provider']=type(i).__name__
 except Exception as e:checks['provider_error']=str(e)
 print(json.dumps(checks,indent=2));return 0 if checks['numpy'] and checks['PIL'] and checks['fastmcp'] else 1
if __name__=='__main__':raise SystemExit(main())
