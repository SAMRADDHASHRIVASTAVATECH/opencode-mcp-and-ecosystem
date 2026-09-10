from __future__ import annotations
import uuid,re
class ArtistPlanner:
 def plan(self,brief,deliverables=None,application=None):
  b=brief.lower();kind='illustration'
  if any(x in b for x in ['logo','mark','identity']):kind='identity'
  elif any(x in b for x in ['poster','flyer','banner']):kind='layout'
  elif any(x in b for x in ['model','3d','scene']):kind='3d'
  elif any(x in b for x in ['photo','retouch']):kind='photo'
  vector=kind in {'identity','layout'};steps=[
   self._s('analyze','Interpret brief, audience, medium and constraints','artist',True),
   self._s('references','Collect and classify approved references','artist',True),
   self._s('concepts','Generate distinct concepts and select direction','artist',True),
   self._s('blockout','Establish composition, hierarchy and proportions','artist',False),
   self._s('construct','Build editable forms, layers, paths and typography','visual' if vector else 'application',False),
   self._s('refine','Refine edges, values, color, rhythm and detail','application',False),
   self._s('critique','Evaluate legibility, balance, contrast, artifacts and brief fit','artist',False),
   self._s('correct','Apply targeted corrections and re-evaluate','application',False),
   self._s('preflight','Validate dimensions, color, fonts, bleed, filenames and editability','artist',True),
   self._s('export','Save editable master and requested derivatives','application',True)]
  return {'schema':'artist.workflow/1','id':str(uuid.uuid4()),'classification':kind,'editable_strategy':'vector-first' if vector else 'layered-raster','application':application,'deliverables':deliverables or [],'steps':steps,'operation_preference':['native_api','plugin','script','cli','accessibility','visual_gui','raw_user_input'],'uncertainties':self._uncertainties(brief,deliverables)}
 def _s(self,i,goal,owner,approval):return {'id':i,'goal':goal,'owner':owner,'requires_approval':approval,'verify':True,'status':'planned'}
 def _uncertainties(self,b,d):
  u=[]
  if not re.search(r'\b\d+\s*[x×]\s*\d+',b):u.append('canvas dimensions')
  if not d:u.append('output formats')
  if not any(x in b.lower() for x in ['audience','for children','for adults','business','consumer']):u.append('audience')
  return u
