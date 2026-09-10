from __future__ import annotations
import os
from .runtime import ArtistRuntime
from .core.control import envelope
rt=ArtistRuntime(os.getenv('UA_STATE_ROOT'))
def create_server():
 from mcp.server.fastmcp import FastMCP
 m=FastMCP('universal-artist')
 @m.tool()
 def create_artwork_project(name:str,brief:str,canvas:dict|None=None)->dict:"""Create durable editable artwork state.""";return rt.store.create(name,brief,canvas)
 @m.tool()
 def get_artwork_state(project_id:str)->dict:return rt.store.get(project_id)
 @m.tool()
 def update_artwork_state(project_id:str,patch:dict,expected_updated:float|None=None)->dict:return rt.store.update(project_id,patch,expected_updated)
 @m.tool()
 def plan_artwork(brief:str,deliverables:list[str]|None=None,application:str|None=None)->dict:
  """Build a professional workflow enriched by the integrated discipline ontology."""
  base=rt.planner.plan(brief,deliverables,application);matches=rt.domains.classify(brief);ids=[x['discipline'] for x in matches if not x.get('uncertain')][:3] or ['fine_art'];base['domain_matches']=matches;base['discipline_workflow']=rt.domains.workflow(ids,brief,deliverables);return base
 @m.resource('artist://domain-catalog')
 def domain_catalog_resource()->str:
  """Professional visual-discipline ontology used by the Artist runtime."""
  import json;return json.dumps(rt.domains.catalog,indent=2)
 @m.tool()
 def list_visual_disciplines()->dict:
  """List integrated professional art, design, spatial, media and visualization disciplines."""
  return {'schema':'artist.discipline-list/1','disciplines':rt.domains.list()}
 @m.tool()
 def classify_visual_brief(brief:str,max_results:int=5)->dict:
  """Classify a brief into one or more professional visual disciplines."""
  return {'schema':'artist.discipline-classification/1','matches':rt.domains.classify(brief,max_results)}
 @m.tool()
 def get_discipline_profile(discipline:str)->dict:
  """Return workflow, deliverables, capability packs and review gates for a discipline."""
  return rt.domains.get(discipline)
 @m.tool()
 def plan_interdisciplinary_workflow(disciplines:list[str],brief:str='',deliverables:list[str]|None=None)->dict:
  """Combine specialist profiles into one editable, review-gated workflow."""
  return rt.domains.workflow(disciplines,brief,deliverables)
 @m.tool()
 def discover_art_applications()->dict:return {'applications':rt.apps.discover(),'preference':['native_api','plugin','script','cli','accessibility','visual_gui','raw_user_input']}
 @m.tool()
 def create_stroke_trajectory(points:list[list[float]],brush:dict|None=None,duration_ms:int|None=None,max_step:float=3)->dict:return rt.trajectory.generate(points,brush,duration_ms,max_step)
 @m.tool()
 def critique_image(path:str)->dict:return rt.critic.analyze(path)
 @m.tool()
 def delegate_control_action(project_id:str,action:str,payload:dict,approval_token:str|None=None,preconditions:list[dict]|None=None,verification:dict|None=None)->dict:"""Create, but do not execute, a safe action envelope for Windows Live Control Agent.""";return envelope(project_id,action,payload,approval_token,preconditions,verification)
 @m.tool()
 def visual_compute_request(operation:str,inputs:list[str],params:dict)->dict:"""Create a typed request for the separate Universal Visual MCP.""";return {'schema':'visual.request/1','operation':operation,'inputs':inputs,'params':params,'delegate_to':'universal-visual-computing'}
 @m.tool()
 def diagnose()->dict:return {'status':'ok','state_db':str(rt.root/'artwork.sqlite3'),'applications':rt.apps.discover(),'control':'delegation-only'}
 return m
def main():create_server().run(transport='stdio')
if __name__=='__main__':main()
