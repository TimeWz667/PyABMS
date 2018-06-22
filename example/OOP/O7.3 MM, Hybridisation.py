import matplotlib.pyplot as plt
from complexism.misc import start_counting, stop_counting, get_results
import epidag as dag
import complexism as cx
import complexism.agentbased.statespace as ss
from complexism.mcore import EventListener


bn_scr = '''
PCore pSEIR {
    beta = 1.5/300
    theta = 0.5
    gamma = 0.2
    Activate ~ exp(theta)
    Infect ~ exp(beta)
    Recover ~ exp(gamma)
}
'''

hie = {
    'city': ['abm_ser', 'abm_i'],
    'abm_ser': ['ag_ser'],
    'ag_ser': ['Infect', 'Activate'],
    'abm_i': ['ag_i'],
    'ag_i': ['Recover']
}

bn = cx.read_bn_script(bn_scr)

sm = dag.as_simulation_core(bn, hie=hie)


d_ser = '''
CTMC SER {
    Sus
    Lat
    Export
    Rec
    Sus -- Infect -> Lat
    Lat -- Activate -> Export
}
'''

d_i = '''
CTMC I {
    Inf
    Export
    Inf -- Recover -> Export
}
'''


dbp_ser = cx.read_dbp_script(d_ser)
dbp_i = cx.read_dbp_script(d_i)

model_name = 'MultiSIR'

pc = sm.generate(model_name)

model = cx.MultiModel(model_name, pc)


mbp_ser = ss.BlueprintStSpABM('SER')
mbp_ser.set_agent(prefix='Ag', group='ag_ser', dynamics='SER')
# mbp_ser.add_behaviour('FOI', 'ForeignShock', t_tar='Infect')
mbp_ser.add_behaviour('Activation', 'Cohort', s_death='Export')
mbp_ser.add_behaviour('Recovery', 'AgentImport', s_birth='Rec')
mbp_ser.set_observations(states=['Sus', 'Lat', 'Rec'],
                         transitions=['Infect', 'Activate'],
                         behaviours=['Recovery', 'Activation', 'FOI'])


mbp_i = ss.BlueprintStSpABM('I')
mbp_i.set_agent(prefix='Ag', group='ag_i', dynamics='I')
mbp_i.add_behaviour('Activation', 'AgentImport', s_birth='Inf')
mbp_i.add_behaviour('Recovery', 'Cohort', s_death='Export')
mbp_i.set_observations(states=['Inf'],
                       transitions=['Recover'],
                       behaviours=['Recovery', 'Activation'])


model_ser = mbp_ser.generate('SER', pc=pc.breed('SER', 'abm_ser'), dc=dbp_ser)
model_i = mbp_i.generate('I', pc=pc.breed('I', 'abm_i'), dc=dbp_i)


model.append(model_ser)
model.append(model_i)


class LisSER(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        print('SEI', disclosure.What)
        if disclosure.What == 'Recover':
            model_local.Behaviours['Recovery'].shock(ti, model_foreign, model_local, 1)


class LisI(EventListener):

    def needs(self, disclosure, model_local):
        if disclosure.is_sibling():
            return True

    def apply_shock(self, disclosure, model_foreign, model_local, ti, arg=None):
        print('I', disclosure.What)
        if disclosure.What == 'Activate':
            model_local.Behaviours['Activation'].shock(ti, model_foreign, model_local, 1)


model_ser.add_listener(LisSER())
model_i.add_listener(LisI())

# model.link('I@Inf', 'SER@FOI', message=['Recover', 'Activation'])
# model.link('I@Recover', 'SER@Recovery', message='Recover')
# model.link('SER@Activate', 'I@Activation', message='Activate')

model.add_observing_model('I')
model.add_observing_model('SER')


y0 = {
    'SER': [
        {'n': 280, 'attributes': {'st': 'Sus'}},
        # {'n': 100, 'attributes': {'st': 'Lat'}}
    ],
    'I': [
        {'n': 20, 'attributes': {'st': 'Inf'}},
    ]

}

start_counting('Hybrid')
output = cx.simulate(model, y0, 0, 30, 1, mid=False, seed=100)
stop_counting()
print(output)

print('Profiling\n', get_results('Hybrid'))

output[['SER@Sus', 'SER@Lat', 'I@Inf', 'SER@Rec']].plot()
plt.show()

