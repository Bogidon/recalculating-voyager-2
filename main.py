from modsim import *
import matplotlib
import matplotlib.animation as animation
#import matplotlib.collections.LineCollection as LineCollection
import platform
import sys
from pdb import set_trace

# Calculations

def planet_slope_func(planet, t, system):
	x, y, vx, vy = planet
	unpack(system)

	return vx, vy, 0, 0
	
def planet2_slope_func(planet2, t, system):
	x, y, vx, vy = planet2
	unpack(system)

	return vx, vy, 0, 0
	

def rocket_slope_func(rocket, t, system):
#     x_r, y_r, vx_r, vy_r, x_p, y_p, vx_p, vy_p = rocket
	x, y, vx, vy = rocket
	unpack(system)
	
	x_p = interpolate(results_p.x)(t)
	y_p = interpolate(results_p.y)(t)

	x_p2 = interpolate(results_p2.x)(t)
	y_p2 = interpolate(results_p2.y)(t)

	pos = Vector(x, y)
	pos_p = Vector(x_p, y_p)
	pos_p2 = Vector(x_p2, y_p2)
	distance = pos.dist(pos_p).m
	distance2 = pos.dist(pos_p2).m

	if (distance2 > distance):

		if distance > rp:
			acc = - (G * mp / (distance**2)) * (pos-pos_p).hat()
		else:
			# hit planet surface
			vx = 0
			vy = 0
			acc = Vector(0,0)

		return vx, vy, acc.x.m, acc.y.m

	else:
		if distance2 > rp2:
			acc = - (G * mp / (distance2**2)) * (pos-pos_p2).hat()
		else:
			# hit planet surface
			vx = 0
			vy = 0
			acc = Vector(0,0)

		return vx, vy, acc.x.m, acc.y.m

'''def rocket_slope_func2(rocket, t, system):
#     x_r, y_r, vx_r, vy_r, x_p, y_p, vx_p, vy_p = rocket
	x, y, vx, vy = rocket
	unpack(system)
	
	x_p2 = interpolate(results_p2.x)(t)
	y_p2 = interpolate(results_p2.y)(t)

	pos = Vector(x, y)
	pos_p2 = Vector(x_p2, y_p2)
	distance = pos.dist(pos_p2).m

	if distance > rp2:
		acc = - (G * mp2 / (distance**2)) * (pos-pos_p2).hat()
	else:
		# hit planet surface
		vx = 0
		vy = 0
		acc = Vector(0,0)

	return vx, vy, acc.x.m, acc.y.m
'''

planet = State(
	x=-1e10,
	y=0,
	vx=47e3,
	vy=0)

rocket = State(
	x=-0.65e10, 
	y=-1000e6, 
	vx = 12e3,
	vy = 12e3)

planet2 = State(
	x=-1e10,
	y=3000e6,
	vx=47e3,
	vy=0)


duration = 11e5

system = System(
	init=planet,
	G=6.67408e-11, 
	ts=linspace(0,duration,1000),
	mr = 721.9,
	mp = 1.9e27,
	mp2 = 1.9e27,
	rp = 70e6,
	rp2 = 70e6)

run_odeint(system, planet_slope_func)
results_p = system.results

system.init = planet2
run_odeint(system, planet2_slope_func)
results_p2 = system.results

system.init = rocket
system.results_p = results_p
system.results_p2 = results_p2

'''if (t > 0 and (((system.results_r.x - system.results_p.x)**2 + (system.results_r.y - system.results_p.y)**2)**(1/2) < 
	((system.results_r.x - system.results_p2.x)**2 + (system.results_r.y - system.results_p2.y)**2)**(1/2)):

	run_odeint(system, rocket_slope_func)
	results_r = system.results

else:
	'''
	
run_odeint(system, rocket_slope_func)
results_r = system.results


##########
# Graphing
##########

mode = 'update'
if ('trail' in sys.argv):
	mode = 'trail'
if ('update' in sys.argv):
	mode = 'update'

# Position
# ========

x_p = results_p.x
y_p = results_p.y
x_r = results_r.x
y_r = results_r.y
x_p2 = results_p2.x
y_p2 = results_p2.y

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(9,9)
plt.title('Gravity Slingshot (position)')
ax = plt.axes(xlim=(-1.2e10,1e10), ylim=(-5e9,5e9))

# Setup modes
if (mode == 'update'):
	rocket = plt.Circle((x_r[0],y_r[0]), system.rp, color='red')
	planet = plt.Circle((x_p[0],y_p[0]), system.rp, color='green')
	planet2 = plt.Circle((x_p2[0],y_p2[0]), system.rp2, color='blue')
	line_r, = plt.plot([], [], 'red')
	line_p, = plt.plot([], [], 'green')
	line_p2 = plt.plot([], [], 'blue')

	ax.add_artist(rocket)
	ax.add_artist(planet)
	ax.add_artist(planet2)


# Animation
def generate_circle(t, x_r, y_r, x_p, y_p, x_p2, y_p2, ax, rocket, planet, planet2, line_r, line_p, line_p2):
	if (mode == 'update'):
		def _generate(t, x_series, y_series, ax, circle, line):
			x = interpolate(x_series)(t)
			y = interpolate(y_series)(t)
			circle.center = (x, y)

			line_x = np.append(line.get_xdata(), x)
			line_y = np.append(line.get_ydata(), y)

			#attempt to vary line width with velocity
			#lwidths = 1 + results_r.vx[:-1]
			#lc = LineCollection(segments, linewidths=lwidths,color='blue')

			line.set_data(line_x, line_y)

		_generate(t, x_r, y_r, ax, rocket, line_r)
		_generate(t, x_p, y_p, ax, planet, line_p)
		_generate(t, x_p2, y_p2, ax, planet2, line_p2)

		return [rocket, planet, planet2]

	if (mode == 'trail'):
		def _generate(t, x, y, ax, color):
			x = interpolate(x)(t)
			y = interpolate(y)(t)
			ax.add_artist(plt.Circle((x,y), system.rp, color=color))

		_generate(t, x_r, y_r, ax, 'red')
		_generate(t, x_p, y_p, ax, 'green')
		_generate(t, x_p2, y_p2, ax, 'blue')

		return []

num_frames = 200 if (mode == 'update') else 50
frames = linspace(0,duration, num_frames)
generate_circle_fargs = (
	x_r,
	y_r,
	x_p,
	y_p,
	x_p2,
	y_p2,
	ax,
	rocket,
	planet,
	planet2,
	line_r,
	line_p,
	line_p2
)

ani = animation.FuncAnimation(fig_pos, generate_circle, frames, fargs=generate_circle_fargs, interval=200, blit=True)

# Save animation
if (platform.system() == "Darwin"):
	ani.save(f'build/slingshot_{mode}.gif', writer='imagemagick')
else:
	ani.save(f'build/slingshot_{mode}.mp4', writer='ffmpeg')

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
