from __future__ import annotations
import json,re
from importlib.resources import files

class DomainKnowledge:
 def __init__(self):
  self.catalog=json.loads(files('universal_artist').joinpath('domain_catalog.json').read_text())
 def list(self):return [{'id':k,**v} for k,v in self.catalog['disciplines'].items()]
 def get(self,discipline):
  if discipline not in self.catalog['disciplines']:raise KeyError(f'Unknown discipline: {discipline}')
  return {'id':discipline,**self.catalog['disciplines'][discipline]}
 def classify(self,brief,max_results=5):
  text=brief.lower();scores=[]
  aliases={'3d_art':['3d','sculpt','model','render','texture'],'film_vfx':['film','movie','cinematic','vfx','shot'],'graphic_design':['logo','brand','poster','layout','packaging'],'architecture':['building','architecture','floor plan','bim'],'interior_design':['interior','room','home','furniture layout'],'landscape':['landscape','garden','park','site plan'],'industrial_design':['product','industrial','device','furniture'],'fashion':['fashion','garment','clothing','costume','textile'],'ui_ux':['ui','ux','website','app','interface','prototype'],'game_art':['game','level','real-time'],'illustration':['illustration','book cover','editorial'],'concept_art':['concept','character','creature','environment'],'photography':['photo','retouch','camera'],'animation':['animation','animated','motion'],'engineering_visualization':['technical drawing','schematic','engineering','diagram'],'data_visualization':['chart','dashboard','data visualization','infographic'],'emerging_media':['vr','ar','xr','projection','installation','generative art']}
  for k,v in self.catalog['disciplines'].items():
   terms=[k.replace('_',' '),v['name'].lower(),*[x.lower() for x in v['subdisciplines']],*aliases.get(k,[])];score=sum(3 if t in text else 0 for t in terms)
   if score:scores.append((score,k))
  scores.sort(reverse=True);return [{'discipline':k,'score':s,'profile':self.get(k)} for s,k in scores[:max_results]] or [{'discipline':'fine_art','score':0,'profile':self.get('fine_art'),'uncertain':True}]
 def workflow(self,disciplines,brief='',deliverables=None):
  profiles=[self.get(x) for x in disciplines];steps=[]
  for phase in self.catalog['common_workflow']:
   steps.append({'phase':phase,'discipline_actions':[{'discipline':p['id'],'focus':p['name']} for p in profiles],'requires_verification':phase not in {'brief','research'}})
  packs=sorted({x for p in profiles for x in p['capability_packs']});gates=sorted({x for p in profiles for x in p['review_gates']})
  return {'schema':'artist.interdisciplinary-workflow/1','brief':brief,'disciplines':disciplines,'steps':steps,'deliverables':deliverables or sorted({x for p in profiles for x in p['deliverables']}),'visual_capability_packs':packs,'review_gates':gates,'specialist_review_required':bool(gates)}
