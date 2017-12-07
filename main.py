from modsim import *
import matplotlib
import matplotlib.animation as animation
import platform
import sys
import pickle
from astropy.time import Time
from astropy.coordinates import *
from pdb import set_trace

##############
# Calculations
##############

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
		mass: num
		radius: num
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

def generate_planet_orbit(x, y, vx, vy, mass, radius, planet_name, sun, system):
	"""
	Returns a dictionary representing a planet and its trajectory:

	Planet: {
		mass: num
		radius: num
		positions: TimeFrame
			x: TimeSeries
			y: TimeSeries
			vx: TimeSeries
			vy: TimeSeries
	}
	"""

	new_planet = State(x=x, y=y, vx=vx, vy=vy)
	system.init = new_planet
	system.other_bodies = [sun]

	run_odeint(system, projectile_slope_func)
	
	return {
		"mass": mass,
		"radius": radius,
		"positions": system.results,
	}

start_year = 1977
end_year = 2018
start_unix = Time(f'{start_year}-01-01').unix
end_unix = Time(f'{end_year}-01-01').unix
duration = end_unix - start_unix

system = System(
	init=None,
	G=6.67408e-11, 
	ts=linspace(0,duration,1000)
)

sun = {
	"mass": 1.989e30,
	"radius": 695700e3,
	"positions": TimeFrame({"x": 0, "y": 0, "vx": 0, "vy": 0},[0,1])
}

def generate_planets(system, sun):
	filepath = 'build/planets.pickle'

	# Regen
	if ('regen_planets' in sys.argv):
		additional_info = {
			"pluto" : {
				"mass": 1.309e22,
				"radius": 1.187e6,
			}, 
			"neptune" : {
				"mass": 1.024e26,
				"radius": 24622e3,
			}, 
			"uranus" : {
				"mass": 8.681e25,
				"radius": 25362e3,
			}, 
			"saturn" : {
				"mass": 5.683e26,
				"radius": 58232e3,
			}, 
			"jupiter" : {
				"mass": 1.898e27,
				"radius": 69911e3,
			}, 
			"mars" : {
				"mass": 6.39e23,
				"radius": 3390e3,
			}, 
			"earth" : {
				"mass": 5.972e24,
				"radius": 6371e3,
			}, 
			"venus" : {
				"mass": 4.867e24,
				"radius": 6052e3,
			}, 
			"mercury" : {
				"mass": 3.285e23,
				"radius": 2440e3,
			}
		}

		# Get initial starting conditions
		with solar_system_ephemeris.set('de432s'):
			t = Time('1977-08-20')
			planet_names = ['mercury', 'venus', 'earth', 'jupiter', 'saturn', 'uranus', 'neptune']
			planets = []

			for planet_name in planet_names:
				helio_pos = get_body(planet_name, t).icrs.cartesian
				icrs_vel = get_body_barycentric_posvel(planet_name, t)[1]

				print(planet_name)

				planets.append(generate_planet_orbit(
					x = helio_pos.x.si.to_value(), 
					y = helio_pos.y.si.to_value(), 
					vx = icrs_vel.x.si.to_value(), 
					vy = icrs_vel.y.si.to_value(),
					mass = additional_info[planet_name]["mass"],
					radius = additional_info[planet_name]["radius"],
					planet_name = planet_name,
					sun = sun,
					system = system
				))

		with open(filepath, 'wb') as file_handle:
			pickle.dump(planets, file_handle, pickle.HIGHEST_PROTOCOL)

		return planets

	# Don't regen, read from pickle
	try:
		with open(filepath, 'rb') as file_handle:
			return pickle.load(file_handle)
	except FileNotFoundError as error:
		print('No planets data saved at build/planets.pickle. Rerun this script passing in `regen_planets` as an argument.')
		exit()
		
planets = generate_planets(system, sun)

voyager_init = State(x = -1.471e11, 
			y = 0, 
			vx = -12e3, 
			vy = -12e3)

system.init = voyager_init
system.other_bodies = planets +[sun]

# run_odeint(system, projectile_slope_func)

# voyager = {
# 	"mass": 721,
# 	"radius":20,
# 	"positions": system.results
# }

bodies = [sun] + planets

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

limit_distance = 5e11
radius_mult = 1
colors = ['#009bdf','#e31d3c','#f47920','#ffc20e','#c0d028','#8ebe3f','#349e49','#26aaa5','#6bc1d3','#7b5aa6','#ed037c','#750324','#00677e']

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(9,9)
plt.title('Gravity Slingshot (position)')
ax = plt.axes(xlim=(-limit_distance,limit_distance), ylim=(-limit_distance,limit_distance))

# Setup modes
if (mode == 'update'):
	for idx, body in enumerate(bodies):
		color = colors[idx]
		positions = body['positions']

		circle = plt.Circle((positions.x[0], positions.y[0]), body['radius'] * radius_mult, color=color)
		line, = plt.plot([], [], color)

		ax.add_artist(circle)
		ax.add_artist(line)

		body['color'] = color
		body['artists'] = (circle, line)
if (mode == 'trail'):
	for idx, body in enumerate(bodies):
		body['color'] = colors[idx]

# Animation
def animate(t, bodies, ax):
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

		for body in bodies:
			positions = body['positions']
			circle, line = body['artists']
			_generate(t, positions.x, positions.y, ax, circle, line)

		return [body['artists'][1] for body in bodies]

	if (mode == 'trail'):
		def _generate(t, x, y, radius, ax, color):
			x = interpolate(x)(t)
			y = interpolate(y)(t)
			ax.add_artist(plt.Circle((x,y), radius, color=color))

		for body in bodies:
			positions = body['positions']
			_generate(t, positions.x, positions.y, 1e11, ax, body['color'])

		return []

num_frames = 200 if (mode == 'update') else 100
frames = linspace(0,duration, num_frames)
ani = animation.FuncAnimation(fig_pos, animate, frames, fargs=(bodies, ax), interval=200, blit=True)

# Save animation
if (platform.system() == "Darwin"):
	ani.save(f'build/slingshot_{mode}.gif', writer='imagemagick')
else:
	ani.save(f'build/slingshot_{mode}.mp4', writer='ffmpeg')

fig_pos.savefig('build/position.png')


# Velocity
# --------
 
fig_v = plt.figure()
plt.title('Speed')

for body in bodies:
	vx = body['positions'].vx
	vy = body['positions'].vy
	speed = np.sqrt(vx**2 + vy**2)
	plt.plot(speed, color=body['color'])

fig_v.savefig('build/speed.png')
