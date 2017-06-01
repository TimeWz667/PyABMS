import json
from collections import OrderedDict
from dcore.dynamics import *


class ModelCTMC(AbsDynamicModel):
    def __init__(self, name, sts, trs, tars, js):
        AbsDynamicModel.__init__(self, name, js)
        self.States = sts
        self.Transitions = trs
        self.Targets = tars

    def get_transitions(self, fr):
        return self.Targets[fr]

    def get_transition(self, fr, to):
        return [tr for tr in self.Targets[fr] if tr.State == to]

    def isa(self, s0, s1):
        return s0 is s1

    def get_state_space(self):
        return self.States

    def get_transition_space(self):
        return self.Transitions

    def __getitem__(self, item):
        return self.States[item]

    def exec(self, st, evt):
        return evt.State

    def __deepcopy__(self):
        return BluePrintCTMC.from_json(self.to_json())


class BluePrintCTMC(AbsBluePrint):
    @staticmethod
    def from_json(js):
        js = json.loads(js)
        bp = BluePrintCTMC(js['ModelName'])
        for st, desc in js['States'].items():
            bp.add_state(st, desc)
        for tr, trd in js['Transitions'].items():
            bp.add_transition(tr, trd['To'], trd['Dist'])
        for fr, trs in js['Targets'].items():
            for tr in trs:
                bp.link_state_transition(fr, tr)
        return bp

    def __init__(self, name, sm='{}'):
        AbsBluePrint.__init__(self, name, sm)
        self.States = dict()  # Nick name -> full desc
        self.Transitions = dict()  # Name -> (event, distribution)
        self.Targets = dict()  # StateName -> TransitionNames

    def add_state(self, state, desc=None):
        if state in self.States:
            return False
        desc = desc if desc else state

        self.States[state] = desc
        self.Targets[state] = list()
        return True

    def add_transition(self, tr, to, dist=None):
        """
        Define a new transition
        :param tr: name of transition
        :param to: name of targeted state
        :param dist: name of distribution, need to be in the parameter core
        :return: true if succeed
        """
        self.add_state(to)
        if not dist:
            dist = tr
        if dist not in self.ExCore.Distributions:
            raise KeyError('Distribution {} does not exist'.format(dist))
        self.Transitions[tr] = {'To': to, 'Dist': dist}
        return True

    def link_state_transition(self, state, tr):
        self.add_state(state)

        if tr not in self.Transitions:
            raise KeyError('Transition {} does not exist'.format(tr))
        self.Targets[state].append(tr)
        return True

    def to_json(self, ind=None):
        js = dict()
        js['ModelType'] = 'CTMC'
        js['ModelName'] = self.Name
        js['States'] = self.States
        js['Transitions'] = self.Transitions
        js['Targets'] = self.Targets
        js = {'dcore': js, 'pcore': self.SimulationCore.DAG.to_json()}
        return json.dumps(js, sort_keys=True, indent=ind)

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return str(self.to_json(4))

    def generate_model(self, suffix=''):
        pc = self.SimulationCore.sample_core()
        sts = {k: State(k, desc, None) for k, desc in self.States.items()}
        trs = dict()
        for name, tr in self.Transitions.items():
            trs[name] = Transition(name, sts[tr['To']], pc.get_distribution(tr['Dist']))

        tars = {stv: [trs[tar] for tar in self.Targets[stk]] for stk, stv in sts.items()}

        mn = '{}_{}'.format(self.Name, suffix) if suffix else self.Name

        js = dict()
        js['ModelType'] = 'CTMC'
        js['ModelName'] = mn
        js['States'] = self.States
        js['Transitions'] = {name: {'To': tr.State.Value, 'Dist': str(tr.Dist)} for name, tr in trs.items()}
        js['Targets'] = self.Targets
        js = json.dumps(js, sort_keys=True)

        mod = ModelCTMC(mn, sts, trs, tars, js)
        for val in sts.values():
            val.Model = mod
        return mod
