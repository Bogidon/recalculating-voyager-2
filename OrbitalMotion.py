from modsim import *
import matplotlib
import matplotlib.animation as animation
import platform
import sys
from pdb import set_trace

# Calculations

def linear_slope_func(sun, t, system):
	x, y, vx, vy = sun
	unpack(system)

	return vx, vy, 0, 0
	
def projectile_slope_func(projectile, t, system):
	"""
	System, must contain an other_bodies property, which is
	an array of dictionaries containing information about each 
	body, with the following structure:

	Body: {
		mass: Int
		radius: Int
		positions: TimeFrame
			x: TimeSeries
			y: TimeSeries
	}
	"""

	x, y, vx, vy = projectile
	other_bodies = system.other_bodies
	G = system.G
	
	pos = Vector(x, y)
	acc_net = Vector(0.0,0.0)

	for body in other_bodies:
		x_body = interpolate(body["positions"].x)(t)
		y_body = interpolate(body["positions"].y)(t)

		pos_body = Vector(x_body, y_body)
		distance = pos.dist(pos_body).m

		if distance > body["radius"]:
			acc_net += - (G * body["mass"] / (distance**2)) * (pos-pos_body).hat()
		else:
			# hit sun surface
			return  0, 0, 0, 0

	return vx, vy, acc_net.x.m, acc_net.y.m

def generate_planet_orbit(x, y, vx, vy, mass, radius, sun, system):
	new_planet = State(x=x, y=y, vx=vx, vy=vy)
	system.init = new_planet
	system.other_bodies = [sun]

	run_odeint(system, projectile_slope_func)
	return system.results


duration = 11e9

system = System(
	init=None,
	G=6.67408e-11, 
	ts=linspace(0,duration,1000)
)

sun = {
	"mass": 1.989e30,
	"radius": 695700e3,
	"positions": TimeFrame({"x": 0, "y": 0},[0,1])
}

# Pluto
pluto = generate_planet_orbit(
	x = -4.44e12, 
	y = 0, 
	vx = 0, 
	vy = -3756,
	mass = 1.309e22,
	radius = 1.187e6,
	sun = sun,
	system = system,
)


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

radius = 1e10

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(9,9)
plt.title('Gravity Slingshot (position)')
ax = plt.axes(xlim=(-5e12,5e12), ylim=(-5e12,5e12))

# Setup modes
if (mode == 'update'):
	projectile = plt.Circle((pluto.x[0],pluto.y[0]), radius, color='red')
	sun = plt.Circle((0,0), radius, color='green')

	line_p, = plt.plot([], [], 'green')

	ax.add_artist(projectile)
	ax.add_artist(sun)


# Animation
def generate_circle(t, x, y, ax, projectile, line_p):
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

		_generate(t, x, y, ax, projectile, line_p)

		return [projectile]

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
	pluto.x,
	pluto.y,
	ax,
	projectile,
	line_p
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

vx_r = pluto.vx
vy_r = pluto.vy
v_r = np.sqrt(vx_r**2 + vy_r**2)

plt.plot(v_r)
plt.title('Speed')

fig_v.savefig('build/3velocity.png')
