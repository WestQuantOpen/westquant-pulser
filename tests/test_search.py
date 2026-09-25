from westquant_pulser.search import PulserSequentialSearch, PulserSearchSpace

class Seq: pass

def builder(config):
    s=Seq(); s.config=config; return s

def evaluator(s):
    return {'duration_ns': 1000*float(s.config.get('duration',1.0)), 'n_atoms':4}
class Verifier:
    def verify(self,s): return {'equivalence':'same_problem_different_dynamics','verified':True}

def test_pulser_search():
    space=PulserSearchSpace(mapping=('identity',), duration=(0.5,1.0), amplitude=(1.0,), detuning=(1.0,))
    r=PulserSequentialSearch(builder=builder, search_space=space, beam_width=1, evaluator=evaluator, verifier=Verifier()).run()
    assert r.best is not None
    assert any(a.stage=='duration' and a.parameters['value']==0.5 for a in r.best.prefix)
