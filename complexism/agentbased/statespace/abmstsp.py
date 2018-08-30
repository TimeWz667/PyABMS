from collections import namedtuple, Counter
from complexism.dcore import Transition
from complexism.agentbased.abm import GenericAgentBasedModel, ObsABM
from complexism.mcore.y0 import LeafY0

__author__ = 'TimeWz667'
__all__ = ['StSpAgentBasedModel', 'StSpY0']

Record = namedtuple('Record', ('Ag', 'Todo', 'Time'))


class ObsStSpABM(ObsABM):
    def __init__(self):
        ObsABM.__init__(self)
        self.States = list()
        self.Transitions = list()
        self.LazySnapshot = dict()

    def add_observing_state(self, st):
        self.States.append(st)

    def add_observing_transition(self, tr):
        self.Transitions.append(tr)

    def update_dynamic_observations(self, model, flow, ti):
        tds = [rec.Todo for rec in self.Records]
        count = Counter(tds)
        trs = {k: v for k, v in count.items() if isinstance(k, Transition)}
        es = {k: v for k, v in count.items() if not isinstance(k, Transition)}

        for tr in self.Transitions:
            try:
                flow[tr.Name] = trs[tr]
            except KeyError:
                flow[tr.Name] = 0

        for evt in self.Events:
            try:
                flow[str(evt)] = es[evt]
            except KeyError:
                flow[str(evt)] = 0

        self.Records.clear()

    def read_statics(self, model, tab, ti):
        ObsABM.read_statics(self, model, tab, ti)

        pop = model.Population
        for st in self.States:
            tab[st] = pop.count(st=st)

        for be in self.Behaviours:
            model.Behaviours[be].fill(tab, model, ti)

        for fn in self.Functions:
            fn(model, tab, ti)

    def get_snapshot(self, model, key, ti):
        try:
            ty, src = self.LazySnapshot[key]
            if ty == 'St':
                return model.Population.count(st=src)
            elif ty == 'Be':
                tab = dict()
                model.Behaviours[src].fill(tab, model, ti)
                return tab[key]
            elif ty == 'Fn':
                tab = dict()
                src(model, tab, ti)
                return tab[key]
            raise AttributeError('Non-identifiable request')
        except KeyError:
            return ObsABM.get_snapshot(self, model, key, ti)

    def initialise_observations(self, model, ti):
        ObsABM.initialise_observations(self, model, ti)
        self._find_lazy_stats(model, ti)

    def _find_lazy_stats(self, model, ti):
        self.LazySnapshot = dict()
        for st in self.States:
            self.LazySnapshot[st] = ('St', st)

        for bk, be in model.Behaviours.items():
            tab = dict()
            be.fill(tab, model, ti)
            for k, v in tab.items():
                self.LazySnapshot[k] = ('Be', bk)

        for fn in self.Functions:
            tab = dict()
            fn(model, tab, ti)
            for k, v in tab.items():
                self.LazySnapshot[k] = ('Fn', fn)

    def record(self, ag, evt, ti):
        self.Records.append(Record(ag.Name, evt.Todo, ti))


class StSpY0(LeafY0):
    def __init__(self, src=None):
        LeafY0.__init__(self, src)

    def match_model(self, model):
        pass

    def define(self, n, **kwargs):
        if isinstance(n, dict):
            if 'attributes' not in n:
                raise KeyError('State not defined')
            elif 'st' not in n['attributes']:
                raise KeyError('State not defined')
            else:
                LeafY0.define(self, n)
            return

        n = int(n)
        if n > 0:
            if 'attributes' in kwargs:
                atr = kwargs['attributes']
            elif 'st' in kwargs:
                atr = kwargs
            else:
                raise KeyError('State not defined')
            self.Entries.append({'n': n, 'attributes': atr})

    @staticmethod
    def from_source(src):
        y0 = StSpY0()
        for ent in src.Entries:
            y0.define(ent)
        return y0


class StSpAgentBasedModel(GenericAgentBasedModel):
    def __init__(self, name, pc, population):
        GenericAgentBasedModel.__init__(self, name, pc, population, ObsStSpABM(), StSpY0)
        self.DCore = population.Eve.DCore

    def read_y0(self, y0, ti):
        for y in y0:
            try:
                atr = y['attributes']
            except KeyError:
                atr = dict()
            self._make_agent(n=y['n'], ti=ti, **atr)

    def add_observing_transition(self, tr):
        try:
            tr = self.DCore.Transitions[tr]
        except KeyError:
            raise KeyError('Transition {} does not exist'.format(tr))
        self.Observer.add_observing_transition(tr)

    def add_observing_state(self, st):
        if st in self.DCore.States:
            self.Observer.add_observing_state(st)
        else:
            raise KeyError('State {} does not exist'.format(st))

    def clone(self, **kwargs):
        pass
