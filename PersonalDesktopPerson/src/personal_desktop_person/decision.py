class MotivationEngine:
 ORDER={'safety':1000,'user_interrupt':900,'commitment':700,'active_task':600,'maintenance':300,'curiosity':100,'social':90}
 def drives(self,state,event_depth=0):
  return {'system_integrity':1.0,'user_commitment':.9 if state.active_goal else 0,'unresolved_work':.8 if state.active_goal else 0,'approved_learning':.25,'bounded_novelty':state.affect.curiosity*.3,'social_continuity':state.affect.social*.2,'resource_management':state.affect.fatigue}
class DecisionUtility:
 def __init__(self,traits):self.t=traits
 def score(self,c):
  t=self.t;return (c.get('goal_progress',0)*(1+t.get('persistence',.5)*.25)+c.get('user_value',0)+c.get('information_gain',0)*(0.5+t.get('curiosity',.5))+c.get('preference_fit',0)+c.get('social_fit',0)*t.get('sociability',.5)-c.get('risk',0)*(1.5-t.get('risk_tolerance',.2))-c.get('cost',0)*(1+t.get('patience',.5)*-.2)-c.get('interruption',0)-c.get('policy_penalty',0)*10+c.get('verification_strength',0)*t.get('conscientiousness',.5))
 def rank(self,candidates):return sorted([dict(c,utility=self.score(c)) for c in candidates],key=lambda x:x['utility'],reverse=True)
