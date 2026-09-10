from __future__ import annotations
import json,os
from .runtime import VisualRuntime
rt=VisualRuntime(os.getenv('UVC_ARTIFACT_ROOT'))
def create_server():
 from mcp.server.fastmcp import FastMCP
 m=FastMCP('universal-visual-computing')
 @m.tool()
 def discover_capabilities(query:str='')->dict:"""Discover executable visual capabilities and adapters.""";return {'capabilities':rt.capabilities(query),'tools':rt.system.discover(),'hardware':rt.system.hardware()}
 @m.resource('visual://domain-catalog')
 def domain_catalog_resource()->str:
  """Discipline-to-computation and capability-pack ontology."""
  import json;return json.dumps(rt.domains.catalog,indent=2)
 @m.tool()
 def list_domain_capability_packs()->dict:
  """List maximal optional visual-computing packs without installing them."""
  return {'schema':'visual.capability-pack-list/1','packs':rt.domains.packs()}
 @m.tool()
 def map_disciplines_to_graphics(disciplines:list[str])->dict:
  """Map professional disciplines to required packs, artifact types, and review gates."""
  return rt.domains.requirements(disciplines)
 @m.tool()
 def plan_capability_pack_install(requested_packs:list[str])->dict:
  """Produce an approval-required installation plan; never installs automatically."""
  return rt.domains.installation_plan(requested_packs,[x['name'] for x in rt.capabilities()])
 @m.tool()
 def import_artifact(path:str)->dict:"""Import an allowed local file into the immutable artifact store.""";return rt.store.import_file(path).__dict__
 @m.tool()
 def get_artifact(artifact_id:str)->dict:"""Read artifact metadata by ID.""";return rt.store.get(artifact_id).__dict__
 @m.tool()
 def execute_visual_graph(graph:dict)->dict:"""Validate and execute an allowlisted visual DAG.""";return rt.execute(graph)
 @m.tool()
 def screen_analysis_request(region:dict,reason:str,continuous:bool=False)->dict:
  """Create a capture request for an approved platform capture/control provider; this server does not capture the desktop itself."""
  return {'schema':'visual.capture-request/1','region':region,'reason':reason,'continuous':continuous,'preferred_sources':['accessibility_event','changed_region','frame'],'delegate_to':'platform-capture-provider','requires_approval':continuous}
 @m.tool()
 def diagnose()->dict:return {'status':'ok','capability_count':len(rt.capabilities()),'tools':rt.system.discover(),'hardware':rt.system.hardware()}
 return m
def main():create_server().run(transport='stdio')
if __name__=='__main__':main()
