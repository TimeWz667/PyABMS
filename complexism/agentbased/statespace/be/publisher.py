from ...be.behaviour import PassiveBehaviour
from .trigger import StateTrigger, DoubleStateTrigger
__author__ = 'TimeWz667'
__all__ = ['StateTrack']


class StateTrack(PassiveBehaviour):
    def __init__(self, name, s_src):
        tri = StateTrigger(s_src)
        PassiveBehaviour.__init__(self, name, tri)
        self.S_src = s_src
        self.Value = 0

    def initialise(self, ti, model):
        self.Value = model.Population.count(st=self.S_src)

    def reset(self, ti, model):
        pass

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        if self.S_src in ag:
            self.Value += 1
        else:
            self.Value -= 1
        model.disclose('update value', self.Name, v=self.Value)

    def impulse_enter(self, model, ag, ti, args=None):
        self.Value += 1
        model.disclose('update value', self.Name, v=self.Value)

    def impulse_exit(self, model, ag, ti, args=None):
        self.Value -= 1
        model.disclose('update value', self.Name, v=self.Value)

    def match(self, be_src, ags_src, ags_new, ti):
        self.Value = be_src.Value

    def fill(self, obs, model, ti):
        obs[self.Name] = self.Value

    def register(self, ag, ti):
        pass

    @staticmethod
    def decorate(name, model, **kwargs):
        s_src = model.DCore.States[kwargs['s_src']]
        model.add_behavior(StateTrack(name, s_src))


class StateRatioTrack(PassiveBehaviour):
    def __init__(self, name, s_num, s_den):
        tri = DoubleStateTrigger(s_num, s_den)
        PassiveBehaviour.__init__(self, name, tri)
        self.S_num = s_num
        self.S_den = s_den
        self.ValueNum = 0
        self.ValueDen = 0

    def initialise(self, ti, model):
        self.ValueNum = model.Population.count(st=self.S_num)
        self.ValueDen = model.Population.count(st=self.S_den)

    def reset(self, ti, model):
        self.ValueNum = model.Population.count(st=self.S_num)
        self.ValueDen = model.Population.count(st=self.S_den)

    def impulse_change(self, model, ag, ti, args_pre=None, args_post=None):
        a0, b0 = args_pre
        a1, b1 = args_post
        if a0 and not a1:
            self.ValueNum -= 1
        elif a1 and not a0:
            self.ValueNum += 1

        if b0 and not b1:
            self.ValueDen -= 1
        elif b1 and not b0:
            self.ValueDen += 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def impulse_enter(self, model, ag, ti, args=None):
        a, b = args
        if a:
            self.ValueNum += 1
        if b:
            self.ValueDen += 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def impulse_exit(self, model, ag, ti, args=None):
        a, b = args
        if a:
            self.ValueNum -= 1
        if b:
            self.ValueDen -= 1
        model.disclose('update value', self.Name, v=self.ValueNum/self.ValueDen)

    def match(self, be_src, ags_src, ags_new, ti):
        self.ValueNum = be_src.ValueNum
        self.ValueDen = be_src.ValueDen

    def fill(self, obs, model, ti):
        obs[self.Name] = self.ValueNum / self.ValueDen

    def register(self, ag, ti):
        pass

    @staticmethod
    def decorate(name, model, **kwargs):
        s_num = model.DCore.States[kwargs['s_num']]
        s_den = model.DCore.States[kwargs['s_den']]
        model.add_behavior(StateRatioTrack(name, s_num, s_den))
