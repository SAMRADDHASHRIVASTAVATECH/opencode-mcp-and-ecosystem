from __future__ import annotations
class Verifier:
 def compare(self,before,after,expect=None):
  changed=after.revision>before.revision and after.frame_id!=before.frame_id
  if expect:
   kind=expect.get('kind')
   if kind=='element_present':
    q=expect.get('text','').lower();ok=any(q in e.name.lower() for e in after.elements);return ok,'success' if ok else 'failed',{'predicate':kind,'query':q}
   if kind=='window_title_contains':
    q=expect.get('text','').lower();ok=q in after.window.title.lower();return ok,'success' if ok else 'failed',{'predicate':kind,'query':q}
   if kind=='screen_changed':return changed,'success' if changed else 'uncertain',{'change_ratio':after.metrics.get('change_ratio',0)}
  return changed,'success' if changed else 'uncertain',{'screen_changed':changed}
