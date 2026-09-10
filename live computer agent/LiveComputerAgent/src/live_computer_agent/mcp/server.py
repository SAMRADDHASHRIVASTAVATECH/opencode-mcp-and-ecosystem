from __future__ import annotations
import os,json,time
from ..config import Config
from ..core.engine import LiveComputerAgent
from ..models import serial
from ..planning.providers import OpenAICompatiblePlanner
CFG=Config.load(); planner=None
if os.getenv('LCA_LLM_URL') and os.getenv('LCA_LLM_MODEL'):
 planner=OpenAICompatiblePlanner(os.environ['LCA_LLM_URL'],os.environ['LCA_LLM_MODEL'],os.getenv('LCA_LLM_API_KEY',''))
ENGINE=LiveComputerAgent(CFG,planner=planner)
try:
 from fastmcp import FastMCP
except ImportError:
 from mcp.server.fastmcp import FastMCP
mcp=FastMCP('Live Windows Computer Agent',instructions='Persistent Windows perception/control runtime. Start a session, observe structured state, use bounded actions, verify, and stop safely.')
def tool(fn):return mcp.tool(fn)
@tool
def start_live_session(mode:str='direct',target:str='desktop')->dict:"""Start the persistent capture/perception session.""";return ENGINE.start(mode,target)
@tool
def stop_live_session()->dict:"""Stop session and release every held input.""";return ENGINE.stop()
@tool
def pause_live_session()->dict:"""Pause capture/actions and release inputs.""";return ENGINE.pause()
@tool
def resume_live_session()->dict:"""Resume a paused session.""";return ENGINE.resume()
@tool
def get_screen(include_image:bool=False)->dict:"""Get current screen metadata and optionally a base64 PNG.""";d=ENGINE.observe();d['png_base64']=ENGINE.screen_png() if include_image else None;return d
@tool
def get_screen_state()->dict:"""Get latest structured hybrid UIA/OCR state.""";return ENGINE.observe()
@tool
def observe_screen(force:bool=True)->dict:"""Force or retrieve a fresh observation.""";return ENGINE.observe(force)
@tool
def read_screen()->dict:"""Return OCR text and accessible elements.""";s=ENGINE.observe();return {'revision':s['revision'],'window':s['window'],'text':s['text'],'elements':s['elements']}
@tool
def analyze_screen()->dict:"""Run fresh hybrid perception and return state.""";return ENGINE.observe(True)
@tool
def get_active_window()->dict:"""Return foreground window metadata.""";return serial(ENGINE.windows.active())
@tool
def list_windows()->list[dict]:"""List visible top-level windows.""";return [serial(w) for w in ENGINE.windows.list()]
@tool
def click(x:int,y:int,button:str='left',verify:bool=True)->dict:"""Click absolute captured-desktop coordinates.""";return ENGINE.perform('click',verify,x=x,y=y,button=button)
@tool
def double_click(x:int,y:int,button:str='left',verify:bool=True)->dict:"""Double-click coordinates.""";return ENGINE.perform('double_click',verify,x=x,y=y,button=button)
@tool
def click_element(element:str,verify:bool=True)->dict:"""Click a structured element by id or visible name.""";return ENGINE.perform('click_element',verify,element=element)
@tool
def move_mouse(x:int,y:int,duration:float=0)->dict:"""Move pointer to coordinates.""";return ENGINE.perform('move_mouse',False,x=x,y=y,duration=duration)
@tool
def drag(x1:int,y1:int,x2:int,y2:int,duration:float=.3,button:str='left')->dict:"""Drag between validated coordinates.""";return ENGINE.perform('drag',True,x1=x1,y1=y1,x2=x2,y2=y2,duration=duration,button=button)
@tool
def scroll(amount:int,x:int|None=None,y:int|None=None)->dict:"""Scroll at current or specified pointer location.""";return ENGINE.perform('scroll',True,amount=amount,x=x,y=y)
@tool
def press_key(key:str,duration:float=.05)->dict:"""Press then always release one key.""";return ENGINE.perform('press_key',True,key=key,duration=duration)
@tool
def release_key(key:str)->dict:"""Release a key defensively.""";return ENGINE.perform('release_key',False,key=key)
@tool
def hotkey(keys:str)->dict:"""Press a plus-separated hotkey and release in reverse order.""";return ENGINE.perform('hotkey',True,keys=keys)
@tool
def type_text(text:str,interval:float=0)->dict:"""Type text into the focused application; clipboard is not used.""";return ENGINE.perform('type_text',True,text=text,interval=interval)
@tool
def focus_window(hwnd:int)->dict:"""Focus a known window handle.""";return ENGINE.perform('focus_window',True,hwnd=hwnd)
@tool
def switch_window()->dict:"""Switch using Alt+Tab.""";return ENGINE.perform('hotkey',True,keys='alt+tab')
@tool
def open_application(path:str,args:list[str]|None=None)->dict:"""Launch an explicit executable when process launching is enabled.""";return ENGINE.perform('open_application',True,path=path,args=args or [])
@tool
def get_agent_state()->dict:"""Get session, goal, recent actions, errors and current screen.""";return ENGINE.agent_state()
@tool
def get_current_goal()->dict:"""Get current goal and subgoal.""";s=ENGINE.agent_state();return {'goal':s['goal'],'subgoal':s['subgoal'],'mode':s['mode']}
@tool
def set_goal(goal:str,mode:str='assisted')->dict:"""Set a goal without starting autonomous execution.""";return ENGINE.set_goal(goal,mode)
@tool
def cancel_goal()->dict:"""Cancel current goal.""";return ENGINE.cancel_goal()
@tool
def execute_action(action:str,parameters:dict,verify:bool=True,expect:dict|None=None)->dict:"""Execute one normalized bounded action.""";return ENGINE.perform(action,verify,expect,**parameters)
@tool
def verify_action(action_id:str,expect:dict|None=None)->dict:
 """Re-observe and report stored action plus current state; actions are verified at dispatch."""
 for a in reversed(ENGINE.state.last_actions):
  if a.id==action_id:return {'action':serial(a),'current_revision':ENGINE.snapshot().revision}
 return {'status':'failed','message':'Unknown action id'}
@tool
def start_autonomous_mode(goal:str,timeout:float=120)->dict:"""Start bounded background observe-plan-act-verify loop using configured planner.""";return ENGINE.start_autonomous(goal,timeout)
@tool
def stop_autonomous_mode()->dict:"""Cancel autonomous goal while retaining live session.""";return ENGINE.cancel_goal()
@tool
def computer_agent(goal:str,mode:str='assisted',application:str='',timeout:float=120,autonomous:bool=False)->dict:
 """Master entry point: ensure session, set goal, and optionally start autonomous loop."""
 if ENGINE.state.status.value not in ('running','paused'):ENGINE.start('autonomous' if autonomous else mode)
 if application:
  matches=[w for w in ENGINE.windows.list() if application.lower() in (w.title+' '+w.application).lower()]
  if not matches:return {'status':'failed','message':'Requested application not found','windows':[serial(w) for w in ENGINE.windows.list()]}
  if not ENGINE.windows.focus(matches[0].hwnd):return {'status':'failed','message':'Could not focus requested application'}
 return ENGINE.start_autonomous(goal,timeout) if autonomous else {'status':'ready','goal':ENGINE.set_goal(goal,mode),'observation':ENGINE.observe()}
@tool
def health_check()->dict:"""Report provider availability and runtime health.""";return {'ok':True,'platform':os.name,'session':ENGINE.state.status.value,'capture':type(ENGINE.capture).__name__,'windows':type(ENGINE.windows).__name__,'input':type(ENGINE.input).__name__,'planner':type(ENGINE.planner).__name__}
def main():mcp.run()
if __name__=='__main__':main()
