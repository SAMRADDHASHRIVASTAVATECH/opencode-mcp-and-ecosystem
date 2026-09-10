from __future__ import annotations
import shutil,platform
class ApplicationRegistry:
 KNOWN={
 'krita':{'methods':['plugin','script','accessibility','visual_gui'],'editable':['kra','ora','psd']},
 'inkscape':{'methods':['native_document','cli','actions','accessibility'],'editable':['svg']},
 'blender':{'methods':['python_api','cli','accessibility'],'editable':['blend']},
 'gimp':{'methods':['plugin','cli','accessibility'],'editable':['xcf']},
 'paint':{'executables':['mspaint'],'methods':['accessibility','visual_gui','raw_user_input'],'editable':['png'],'platform':'Windows'},
 'photoshop':{'executables':['Photoshop'],'methods':['plugin','script','accessibility','visual_gui'],'editable':['psd'],'platform':'Windows/macOS'},
 'illustrator':{'executables':['Illustrator'],'methods':['plugin','script','accessibility','visual_gui'],'editable':['ai','svg'],'platform':'Windows/macOS'},
 'comfyui':{'executables':[],'methods':['http_api'],'editable':['workflow.json']}}
 def discover(self):
  r=[]
  for name,d in self.KNOWN.items():
   paths=[shutil.which(x) for x in d.get('executables',[name])];r.append({'name':name,'available':any(paths),'path':next((x for x in paths if x),None),'platform':d.get('platform','cross-platform'),'methods':d['methods'],'editable_formats':d['editable']})
  return r
