import complexism as cx
import complexism.equationbased as ebm
import epidag as dag
import matplotlib.pyplot as plt
__author__ = 'TimeWz667'


model_name = 'TB'

# Step 1 set a parameter core
psc = """
PCore pSIR {
    beta = 1.5
    gamma = 0.2
}
"""

bn = cx.read_bn_script(psc)
sm = dag.as_simulation_core(bn, hie={'city': []})
pc = sm.generate('Taipei')


# Step 2 define equations
def SIR_ODE(y, t, p, x):
    s = y[0]
    i = y[1]
    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


# Step 3 generate a model
model = ebm.OrdinaryDifferentialEquationModel(model_name, SIR_ODE, 0.1, 0.5,
                                              ['S', 'I', 'R'], {'dis': 0.5}, pc)


# Step 4 decide outputs
for st in ['S', 'I', 'R']:
    model.add_observing_stock(st)


# Step 5 simulate
y0 = ebm.ODEY0()
y0.define(st='S', n=950)
y0.define(st='I', n=50)
y0.define(st='R', n=0)

output = cx.simulate(model, y0, 0, 10, 0.5, log=False)


# Step 6 inference, draw figures, and manage outputs
fig, axes = plt.subplots(nrows=3, ncols=1)

ax = output.plot(ax=axes[0])
ax.set_xlim([0, 30])

# Internal intervention
model.shock(time=10, action='impulse', k='dis', v=10)
output = cx.update(model, to=20, dt=1)
ax = output.plot(ax=axes[1])
ax.set_xlim([0, 30])

# External intervention
pc.impulse({'beta': 10.0})
output = cx.update(model, to=30, dt=1)
ax = output.plot(ax=axes[2])
ax.set_xlim([0, 30])

plt.show()
