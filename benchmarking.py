from modsim import *
from timeit import timeit
from pdb import set_trace

setup = '''
import pickle
from modsim import System, linspace, TimeFrame, State, Vector, interpolate

with open('build/planets.pickle', 'rb') as file_handle:
	planets = pickle.load(file_handle)
'''

num = 10000
print(timeit("planets[0]['position_interpolations']", setup=setup, number=num)/num)

setup = '''
from modsim import System, linspace, TimeFrame, State, Vector, interpolate
import numpy as np
import matplotlib
import matplotlib.animation as animation
import platform
import sys
import pickle
from astropy.time import Time
from astropy.coordinates import get_body
from pdb import set_trace

with open('build/planets.pickle', 'rb') as file_handle:
	planets = pickle.load(file_handle)

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

		if distance > body["radius"]:
			acc_net += - (G * body["mass"] / (distance**2)) * (pos-pos_body).hat()
		else:
			# hit body surface
			return  0, 0, 0, 0

	return vx, vy, acc_net.x.m, acc_net.y.m

system = System(
	init=None,
	G=np.float64(6.67408e-11), 
	ts=linspace(0,1293840000,1000)
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

earth = get_body('earth', Time('1977-08-20')).icrs.cartesian

voyager_init = State(
			x = earth.x.to_value('m'), 
			y = earth.y.to_value('m') + 6371e3,
			vx = 0, 
			vy = 38.5e3)

system.init = voyager_init
system.other_bodies = planets + [sun]
'''

num = 1000
print(timeit("projectile_slope_func(voyager_init, system.ts[0], system)", setup=setup, number=num)/num)