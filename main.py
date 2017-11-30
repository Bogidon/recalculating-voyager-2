from modsim import *
import matplotlib
import matplotlib.animation as animation
import pdb
import platform

# Calculations

def planet_slope_func(planet, t, system):
	x, y, vx, vy = planet
	unpack(system)

	return vx, vy, 0, 0
	

def rocket_slope_func(rocket, t, system):
#     x_r, y_r, vx_r, vy_r, x_p, y_p, vx_p, vy_p = rocket
	x, y, vx, vy = rocket
	unpack(system)
	
	pos = Vector(x, y)

	if pos.mag > rp:
		acc = - (G * mp / (pos.mag**2)).m * pos.hat()
	else:
		# hit planet surface
		vx = 0
		vy = 0
		acc = Vector(0,0)

	return vx, vy, acc.x, acc.y

rocket = State(
	x=-1e10, 
	y=300e6, 
	vx = 17e3,
	vy = 0)

planet = State(
	x=0,
	y=0,
	vx=47e3,
	vy=0)

duration = 11e5

system = System(
	init=planet,
	G=6.67408e-11, 
	ts=linspace(0,duration,1000),
	mr = 721.9,
	mp = 1.9e27,
	rp = 70e6)

run_odeint(system, planet_slope_func)
results_p = system.results

system.init = rocket
run_odeint(system, rocket_slope_func)
results_r = system.results


##########
# Graphing
##########

# Position
# ========

# Planet
# ------

x_p = results_p.x
y_p = results_p.y

plot(x_p, y_p)
savefig('build/jupiter.png')


# Rocket
# ------

x_r = results_r.x
y_r = results_r.y

# pdb.set_trace()

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(9,9)
plt.title('Gravity Slingshot (position)')

# Plot Jupiter 
ax = plt.axes(xlim=(-5e9,5e9), ylim=(-5e9,5e9))
ax.add_artist(plt.Circle((0,0), system.rp))

# Animation
def generate_circle(t, x_r, y_r, x_p, y_p, ax):
	def _generate(t, x, y, ax, color):
		x = interpolate(x)(t)
		y = interpolate(y)(t)
		ax.add_artist(plt.Circle((x,y), system.rp, color=color))

	_generate(t, x_r, y_r, ax, 'red')
	_generate(t, x_p, y_p, ax, 'green')

	return []

frames = linspace(0,duration, 50)
ani = animation.FuncAnimation(fig_pos, generate_circle, frames, 
							  fargs=(x_r, y_r, x_p, y_p, ax), interval=200, blit=True)

# Save animation
if (platform.system() == "Darwin"):
	ani.save('build/slingshot.gif', writer='imagemagick')
else:
	ani.save('build/slingshot.mp4', writer='ffmpeg')

fig_pos.savefig('build/position.png')


# Velocity
# --------
 
fig_v = plt.figure()

vx_r = results_r.vx
vy_r = results_r.vy
v_r = np.sqrt(vx_r**2 + vy_r**2)

plt.plot(v_r)
plt.title('Speed')

fig_v.savefig('build/velocity.png')
