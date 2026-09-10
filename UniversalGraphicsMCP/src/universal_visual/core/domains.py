from __future__ import annotations
import json
from importlib.resources import files
class DomainCapabilityMap:
 def __init__(self):self.catalog=json.loads(files('universal_visual').joinpath('domain_catalog.json').read_text())
 def disciplines(self):return [{'id':k,**v} for k,v in self.catalog['disciplines'].items()]
 def packs(self):return [{'id':k,'operations':v} for k,v in self.catalog['capability_packs'].items()]
 def requirements(self,disciplines):
  missing=[x for x in disciplines if x not in self.catalog['disciplines']]
  if missing:raise KeyError(f'Unknown disciplines: {missing}')
  profiles=[self.catalog['disciplines'][x] for x in disciplines];packs=sorted({x for p in profiles for x in p['capability_packs']})
  return {'schema':'visual.domain-requirements/1','disciplines':disciplines,'required_packs':[{'id':x,'operations':self.catalog['capability_packs'][x]} for x in packs],'artifact_types':self._artifacts(packs),'review_gates':sorted({x for p in profiles for x in p['review_gates']})}
 def installation_plan(self,requested_packs,available_capabilities):
  unknown=[x for x in requested_packs if x not in self.catalog['capability_packs']]
  if unknown:raise KeyError(f'Unknown packs: {unknown}')
  return {'schema':'visual.capability-pack-plan/1','requested':requested_packs,'operations':{x:self.catalog['capability_packs'][x] for x in requested_packs},'currently_registered':available_capabilities,'automatic_install':False,'requires_approval':True,'requirements':['license review','disk/RAM/VRAM estimate','platform compatibility','pinned versions','health test','rollback plan']}
 def _artifacts(self,packs):
  m={'raster-photo':['Image','Mask'],'color-vfx':['Image','ColorTransform'],'vector-typography':['Path','GlyphRun','Layout','Document'],'classical-cv':['Detection','Track','Transform'],'ocr-document':['TextRegion','Document'],'video-animation':['Frame','Timeline'],'detection-segmentation':['Detection','Mask','Track'],'generation-restoration':['Image','GenerationManifest'],'three-d-usd':['Mesh','Scene','Material'],'cad-bim':['Scene','Drawing','BIMDocument'],'architecture-gis':['GeoLayer','Terrain','Scene'],'ui-ux':['Layout','Prototype'],'game-engine':['Scene','EngineAsset'],'procedural':['Graph','Scene'],'fabrication-output':['Drawing','Toolpath']};return sorted({a for p in packs for a in m.get(p,['Artifact'])})
