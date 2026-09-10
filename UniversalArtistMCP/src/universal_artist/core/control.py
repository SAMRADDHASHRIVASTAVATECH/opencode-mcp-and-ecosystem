from __future__ import annotations
import uuid,time
CONSEQUENTIAL={'launch_application','save','overwrite','export','pointer_sequence','keyboard_sequence','install'}
def envelope(project_id,action,payload,approval_token=None,preconditions=None,verify=None):
 if action not in {'inspect_accessibility','capture_region','launch_application','save','overwrite','export','pointer_sequence','keyboard_sequence','invoke_supported_api'}:raise ValueError('Unsupported delegated action')
 return {'schema':'live-control.action/1','id':str(uuid.uuid4()),'project_id':project_id,'created_at':time.time(),'action':action,'payload':payload,'preconditions':preconditions or [],'verification':verify or {'mode':'observe_change'},'requires_approval':action in CONSEQUENTIAL,'approval_token':approval_token,'fail_closed':True,'emergency_release':action in {'pointer_sequence','keyboard_sequence'}}
