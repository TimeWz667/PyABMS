import numpy as np
import numpy.random as rd
from complexism.element import Clock, Event
from complexism.agentbased import TimeIndBehaviour, TimeDepBehaviour
from .trigger import StateEnterTrigger

__author__ = 'TimeWz667'
__all__ = ['Reincarnation', 'Cohort', 'LifeRate', 'LifeS']


class Reincarnation(TimeIndBehaviour):
    def __init__(self, name, s_death, s_birth):
        TimeIndBehaviour.__init__(self, name, StateEnterTrigger(s_death))
        self.S_death = s_death
        self.S_birth = s_birth
        self.BirthN = 0

    def initialise(self, model, ti):
        pass

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti):
        model.kill(ag.Name, ti)
        model.birth(n=1, ti=ti, st=self.S_birth)
        self.BirthN += 1

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        model.Behaviours[name] = Reincarnation(name, s_death, kwargs['s_birth'])

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.S_birth, self.BirthN
        return 'Reincarnation({}, Death:{}, Birth:{}, NBir:{})'.format(*opt)


class Cohort(TimeIndBehaviour):
    def __init__(self, name, s_death):
        TimeIndBehaviour.__init__(self, name, StateEnterTrigger(s_death))
        self.S_death = s_death
        self.DeathN = 0

    def initialise(self, model, ti):
        pass

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti):
        model.kill(ag.Name, ti)
        self.DeathN = 0

    def fill(self, obs, model, ti):
        obs[self.Name] = self.DeathN

    @staticmethod
    def decorate(name, model, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        model.Behaviours[name] = Cohort(name, s_death)

    def match(self, be_src, ags_src, ags_new, ti):
        self.DeathN = be_src.DeathN

    def __repr__(self):
        opt = self.Name, self.S_death.Name, self.DeathN
        return 'Cohort({}, Death:{}, NDeath:{})'.format(*opt)


class LifeRate(TimeDepBehaviour):
    def __init__(self, name, s_birth, s_death, rate, dt=1):
        TimeDepBehaviour.__init__(self, name, Clock(dt), StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.BirthRate = rate
        self.Dt = dt
        self.BirthN = 0

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def do_action(self, model, todo, ti):
        n = model.Pop.count()

        if n <= 0:
            return
        prob = 1 - np.exp(-self.BirthRate * self.Dt)
        n = rd.binomial(n, prob)

        self.BirthN += n
        model.birth(n=n, ti=ti, st=self.S_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = LifeRate(name, kwargs['s_birth'], s_death, kwargs['rate'], dt)

    def __repr__(self):
        return 'BDbyRate({}, BirthRate={})'.format(self.Name, self.BirthRate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def clone(self, *args, **kwargs):
        pass


class LifeS(TimeDepBehaviour):
    def __init__(self, name, s_birth, s_death, cap, rate, dt=1):
        TimeDepBehaviour.__init__(self, name, Clock(dt), StateEnterTrigger(s_death))
        self.S_death = s_death.Name
        self.S_birth = s_birth
        self.Cap = cap
        self.Rate = rate
        self.Dt = dt
        self.BirthN = 0

    def compose_event(self, ti):
        return Event(self.Name, ti)

    def do_action(self, model, todo, ti):
        n = model.Pop.count()

        if n <= 0:
            return

        rate = self.Rate * (1 - n / self.Cap)
        prob = 1 - np.exp(-rate * self.Dt)

        n = rd.binomial(n, prob)

        self.BirthN += n
        model.birth(n=n, ti=ti, st=self.S_birth)

    def register(self, ag, ti):
        pass

    def impulse_change(self, model, ag, ti):
        model.kill(ag.Name, ti)

    def fill(self, obs, model, ti):
        obs[self.Name] = self.BirthN

    @staticmethod
    def decorate(name, model, *args, **kwargs):
        s_death = model.DCore.States[kwargs['s_death']]
        dt = kwargs['dt'] if 'dt' in kwargs else 1
        model.Behaviours[name] = LifeS(name, kwargs['s_birth'], s_death, kwargs['cap'], kwargs['rate'], dt)

    def __repr__(self):
        return 'S-shape({}, K={}, R={})'.format(self.Name, self.Cap, self.Rate)

    def match(self, be_src, ags_src, ags_new, ti):
        self.BirthN = be_src.BirthN

    def clone(self, *args, **kwargs):
        pass