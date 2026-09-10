import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
py=root/'.venv'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
data={'$schema':'https://opencode.ai/config.json','mcp':{'personal_desktop_person':{'type':'local','command':[str(py),'-m','personal_desktop_person'],'environment':{'PDP_CONFIG':str(root/'config/default.json')},'enabled':True,'timeout':30000},'open_computer_use':{'type':'local','command':['open-computer-use','mcp'],'enabled':False,'timeout':30000}},'instructions':[str(root/'skills/SKILL.md')]}
(root/'opencode.generated.json').write_text(json.dumps(data,indent=2));print(root/'opencode.generated.json')
