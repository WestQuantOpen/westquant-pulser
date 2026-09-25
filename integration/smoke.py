import pulser
from westquant_pulser import ConstantPulseTemplate, PulserSearchSpace, PulserSequentialSearch
reg=pulser.Register({'q0':(0,0),'q1':(5,0)})
template=ConstantPulseTemplate(register=reg,device=pulser.AnalogDevice,duration_ns=1000,amplitude=1.0,detuning=0.0)
space=PulserSearchSpace(mapping=('identity',),duration=(0.75,1.0),amplitude=(0.75,1.0),detuning=(1.0,))
r=PulserSequentialSearch(builder=template.build,search_space=space,beam_width=2).run(challenge_id='smoke-pulser')
assert r.best is not None
print(r.best.to_dict())
