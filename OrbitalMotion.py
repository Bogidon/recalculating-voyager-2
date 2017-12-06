from modsim import *
import matplotlib
import matplotlib.animation as animation
#import matplotlib.collections.LineCollection as LineCollection
import platform
import sys
from pdb import set_trace

# Calculations

def linear_slope_func(sun, t, system):
	x, y, vx, vy = sun
	unpack(system)

	return 0, 0, 0, 0
	
def projectile_slope_func(projectile, t, system):
	"""
	System, must contain an other_bodies property, which is
	an array of dictionaries containing information about each 
	body, with the following structure:

	Body: {
		mass: Int
		radius: Int
		positions: TimeSeries
	}
	"""

#     x_r, y_r, vx_r, vy_r, x_p, y_p, vx_p, vy_p = projectile
	x, y, vx, vy = projectile
	other_bodies = system.other_bodies
	
	pos = Vector(x, y)
	acc_net = Vector(0,0)

	for body in other_bodies:
		x_body = interpolate(body.positions.x)(t)
		y_body = interpolate(body.positions.y)(t)

		pos_body = Vector(x_body, y_body)
		distance = pos.dist(pos_body).mag

		if distance > body.radius:
			acc_net += - (G * body.mass / (distance**2)) * (pos-pos_body).hat()
		else:
			# hit sun surface
			return  0, 0, 0, 0

	return vx, vy, acc_net.x.m, acc_net.y.m

sun = State(
	x=-0,
	y=0,
	vx=0,
	vy=0)

projectile = State(
	x=-4.44e12, 
	y=0, 
	vx = 0,
	vy = -3756)

'''sun2 = State(
	x=-1e10,
	y=3000e6,
	vx=47e3,
	vy=0)'''

def add_planet(xs, ys, vxs, vys, mass, radius, system):
	new_planet = State(x=xs, y=ys, vx=vxs, vy=vys)
	sun = State(x=0, y=0, vx=0, vy=0)
	#new_system = System(init=sun, G=6.67408e-11, ts=linspace(0,duration,1000), mp = mps, ms = 1.989e30,
	#rp = 695700e3)

	system.init = new_planet

	run_odeint(system, projectile_slope_func)
	results_p = system.results

	return results_p

	








duration = 11e9

system = System(
	init=sun,
	G=6.67408e-11, 
	ts=linspace(0,duration,1000),
	mr = 1.309e22,
	mp = 1.989e30,
	#mp2 = 1.9e27,
	rp = 695700e3)
	#rp2 = 70e6)

run_odeint(system, linear_slope_func)
results_p = system.results

#system.init = sun2
#run_odeint(system, sun2_slope_func)
#results_p2 = system.results

system.init = projectile
system.results_p = results_p
#system.results_p2 = results_p2

'''if (t > 0 and (((system.results_r.x - system.results_p.x)**2 + (system.results_r.y - system.results_p.y)**2)**(1/2) < 
	((system.results_r.x - system.results_p2.x)**2 + (system.results_r.y - system.results_p2.y)**2)**(1/2)):

	run_odeint(system, projectile_slope_func)
	results_r = system.results

else:
	'''

run_odeint(system, projectile_slope_func)
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
#x_p2 = results_p2.x
#y_p2 = results_p2.y

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(9,9)
plt.title('Gravity Slingshot (position)')
ax = plt.axes(xlim=(-5e12,5e12), ylim=(-5e12,5e12))

# Setup modes
if (mode == 'update'):
	projectile = plt.Circle((x_r[0],y_r[0]), system.rp * 100, color='red')
	sun = plt.Circle((x_p[0],y_p[0]), system.rp * 100, color='green')
	#sun2 = plt.Circle((x_p2[0],y_p2[0]), system.rp2, color='blue')
	line_r, = plt.plot([], [], 'red')
	line_p, = plt.plot([], [], 'green')
	#line_p2 = plt.plot([], [], 'blue')

	ax.add_artist(projectile)
	ax.add_artist(sun)
	#ax.add_artist(sun2)


# Animation
def generate_circle(t, x_r, y_r, x_p, y_p, ax, projectile, sun, line_r, line_p):
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

		_generate(t, x_r, y_r, ax, projectile, line_r)
		_generate(t, x_p, y_p, ax, sun, line_p)
		#_generate(t, x_p2, y_p2, ax, sun2, line_p2)

		return [projectile, sun]

	if (mode == 'trail'):
		def _generate(t, x, y, ax, color):
			x = interpolate(x)(t)
			y = interpolate(y)(t)
			ax.add_artist(plt.Circle((x,y), system.rp, color=color))

		_generate(t, x_r, y_r, ax, 'red')
		_generate(t, x_p, y_p, ax, 'green')

		return []

num_frames = 200 if (mode == 'update') else 50
frames = linspace(0,duration, num_frames)
generate_circle_fargs = (
	x_r,
	y_r,
	x_p,
	y_p,
	ax,
	projectile,
	sun,
	line_r,
	line_p,
)

ani = animation.FuncAnimation(fig_pos, generate_circle, frames, fargs=generate_circle_fargs, interval=200, blit=True)

# Save animation
if (platform.system() == "Darwin"):
	ani.save(f'build/3slingshot_{mode}.gif', writer='imagemagick')
else:
	ani.save(f'build/3slingshot_{mode}.mp4', writer='ffmpeg')

fig_pos.savefig('build/3position.png')


# Velocity
# --------
 
fig_v = plt.figure()

vx_r = results_r.vx
vy_r = results_r.vy
v_r = np.sqrt(vx_r**2 + vy_r**2)

plt.plot(v_r)
plt.title('Speed')

fig_v.savefig('build/3velocity.png')
