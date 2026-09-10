from __future__ import annotations
import xml.etree.ElementTree as ET,math
class SVGAdapter:
 name='svg'
 def capabilities(self):return ['vector.create_svg','vector.inspect','vector.transform']
 def run(self,op,inputs,p,store):
  if op=='vector.create_svg':
   w,h=int(p.get('width',1000)),int(p.get('height',1000));root=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width=str(w),height=str(h),viewBox=f'0 0 {w} {h}')
   for x in p.get('elements',[]):
    tag=x['type'];attrs={k:str(v) for k,v in x.items() if k!='type' and k!='text'};e=ET.SubElement(root,tag,attrs);e.text=x.get('text')
   out=store.create_path('.svg');ET.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True);a=store.register(out,'vector',self.name,[],{'editable':True});return [a],{'elements':len(p.get('elements',[]))}
  if op=='vector.inspect':
   root=ET.parse(store.get(inputs[0]).path).getroot();nodes=list(root.iter());return [],{'root':root.tag,'attributes':root.attrib,'elements':len(nodes),'types':sorted({x.tag.split('}')[-1] for x in nodes})}
  raise ValueError(op)
