from modsim import *
import matplotlib
import matplotlib.animation as animation
import platform
import sys
import dill as pickle
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
		position_interpolations: dict
			x: function
			y: function
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
		x_body = body["position_interpolations"]['x'](t)
		y_body = body["position_interpolations"]['y'](t)

		pos_body = Vector(x_body, y_body)
		distance = pos.dist(pos_body).m

		if distance > body["radius"] and not system.crashed:
			acc_net += - (G * body["mass"] / (distance**2)) * (pos-pos_body).hat()
		else:
			# hit body surface
			system.crashed = True
			vx = 0.0001
			vy = 0.0001
			acc_net = Vector(0.0001,0.0001)

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
		"name": planet_name,
		"position_interpolations": {
			"x": interpolate(system.results.x),
			"y": interpolate(system.results.y),
		},
		"positions": system.results,
	}

def generate_planets(system, sun):
	filepath = 'build/planets.pickle'

	# Regen
	if ('regen_planets' in sys.argv):
		additional_info = {
			"pluto" : {
				"mass": np.float64(1.309e22),
				"radius": np.float64(1.187e6),
			}, 
			"neptune" : {
				"mass": np.float64(1.024e26),
				"radius": np.float64(24622e3),
			}, 
			"uranus" : {
				"mass": np.float64(8.681e25),
				"radius": np.float64(25362e3),
			}, 
			"saturn" : {
				"mass": np.float64(5.683e26),
				"radius": np.float64(58232e3),
			}, 
			"jupiter" : {
				"mass": np.float64(1.898e27),
				"radius": np.float64(69911e3),
			}, 
			"mars" : {
				"mass": np.float64(6.39e23),
				"radius": np.float64(3390e3),
			}, 
			"earth" : {
				"mass": np.float64(5.972e24),
				"radius": np.float64(6371e3),
			}, 
			"venus" : {
				"mass": np.float64(4.867e24),
				"radius": np.float64(6052e3),
			}, 
			"mercury" : {
				"mass": np.float64(3.285e23),
				"radius": np.float64(2440e3),
			}
		}

		# Get initial starting conditions
		with solar_system_ephemeris.set('de432s'):
			t = Time('1977-08-20')
			planet_names = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
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
		print(f'No planets data saved at {filepath}. Rerun this script passing in `regen_planets` as an argument.')
		exit()

def sweep_voyager(vmag, vy0, vyf, num, planets):
	filepath = 'build/voyager.pickle'

	# Regen
	if ('regen_voyager' in sys.argv):
		vy = linspace(vy0,vyf, num)
		
		earth = get_body('earth', Time('1977-08-20')).icrs.cartesian
		runs = []

		for i in range(num):
			vx = np.sqrt(vmag**2 - vy[i]**2)

			print(f'Computing voyager trajectory #{i}: vx: {vx} vy: {vy[i]}')
			voyager_init = State(
				x = earth.x.to_value('m'), 
				y = earth.y.to_value('m') + 6371e3,
				vx = vx,
				vy = vy[i])

			system.init = voyager_init
			system.other_bodies = planets +[sun]
			
			run_odeint(system, projectile_slope_func)
			runs.append({
				"mass": 721,
				"radius":20,
				"name": "voyager",
				"position_interpolations": {
					"x": interpolate(system.results.x),
					"y": interpolate(system.results.y),
				},
				"positions": system.results
			})

		with open(filepath, 'wb') as file_handle:
			pickle.dump(runs, file_handle, pickle.HIGHEST_PROTOCOL)

		print('Done computing voyager trajectories')
		return runs
	
	# Don't regen, read from pickle
	try:
		with open(filepath, 'rb') as file_handle:
			return pickle.load(file_handle)
	except FileNotFoundError as error:
		print(f'No voyager data saved at {filepath}. Rerun this script passing in `regen_voyager` as an argument.')
		exit()

start_year = 1977
end_year = 2018
start_unix = Time(f'{start_year}-01-01').unix
end_unix = Time(f'{end_year}-01-01').unix
duration = end_unix - start_unix

system = System(
	init=None,
	G=np.float64(6.67408e-11), 
	ts=linspace(0,duration,10000),
	crashed=False
)

sun_frame = TimeFrame({"x": 0, "y": 0, "vx": 0, "vy": 0},[0,1])
sun = {
	"mass": 1.989e30,
	"radius": 695700e3,
	"name": 'sun',
	"position_interpolations": {
		"x": interpolate(sun_frame.x),
		"y": interpolate(sun_frame.y)
	},
	"positions": sun_frame,
}
		
planets = generate_planets(system, sun)

runs = sweep_voyager(vmag=44556.31534, vy0=41.0e3, vyf=41.4e3, num=10, planets=planets)

bodies = runs + planets 

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

def radius_transform(radius):
	return np.power(radius, 1/4) * 8e8

limit_distance = 5e12
colors = ['#009bdf','#e31d3c','#f47920','#ffc20e','#c0d028','#8ebe3f','#349e49','#26aaa5','#6bc1d3','#7b5aa6','#ed037c','#750324','#00677e'] * 1000

# Setup figure
fig_pos = plt.figure()
fig_pos.set_dpi(100)
fig_pos.set_size_inches(20,20)
plt.title('Gravity Slingshot (position)')
ax = plt.axes(xlim=(-limit_distance,limit_distance), ylim=(-limit_distance,limit_distance))

# Setup modes
if (mode == 'update'):
	for idx, body in enumerate(bodies):
		color = colors[idx]
		positions = body['positions']

		circle = plt.Circle((positions.x[0], positions.y[0]), radius_transform(body['radius']), color=color)
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
		def _generate(x, y, ax, circle, line):
			circle.center = (x, y)
			line_x = np.append(line.get_xdata(), x)
			line_y = np.append(line.get_ydata(), y)
			line.set_data(line_x, line_y)

		for body in bodies:
			interp = body['position_interpolations']
			circle, line = body['artists']
			_generate(interp['x'](t), interp['y'](t), ax, circle, line)

		return [body['artists'][1] for body in bodies]

	if (mode == 'trail'):
		def _generate(x, y, radius, ax, color):
			ax.add_artist(plt.Circle((x,y), radius, color=color))

		for body in bodies:
			interp = body['position_interpolations']
			_generate(interp['x'](t), interp['y'](t), 1e11, ax, body['color'])

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
 
def plot_velocity(bodies, name):
	fig_v = plt.figure()
	fig_v.set_size_inches(20,20)
	plt.title(f'Speed ({name})')

	for body in bodies:
		vx = body['positions'].vx
		vy = body['positions'].vy
		speed = np.sqrt(vx**2 + vy**2)
		plt.plot(speed, color=body['color'])

	fig_v.savefig(f'build/speed_{name}.png')

plot_velocity([body for body in bodies if body['name'] != 'voyager'], 'planets')
plot_velocity([body for body in bodies if body['name'] == 'voyager'], 'voyager')
