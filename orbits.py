from modsim import *
import astropy
from pdb import set_trace

from astropy.time import Time
from astropy.coordinates import *

with solar_system_ephemeris.set('de432s'):
	t = Time('1977-08-20')
	bodies = ['sun', 'mercury', 'venus', 'earth', 'jupiter', 'saturn', 'uranus', 'neptune']
	for body in bodies:
		helio_pos = get_body(body, t).icrs.cartesian
		icrs_vel = get_body_barycentric_posvel(body, t)[1]
		
		print(f'''
{body}
x: {helio_pos.x.si} 
y: {helio_pos.y.si}
vx: {icrs_vel.x.si} 
vy: {icrs_vel.y.si}''')

# fig = plt.figure()
# fig.set_dpi(100)
# fig.set_size_inches(9,9)
# ax = plt.axes()

def graph():
	start_year = 1971
	end_year = 1973
	radius = 1e12

	start_unix = Time(f'{start_year}-01-01').unix
	end_unix = Time(f'{end_year}-01-01').unix
	times = Time(linspace(start_unix,end_unix,20), format='unix')

	newfig()

	# bodies = solar_system_ephemeris.bodies
	bodies = ['mars', 'earth', 'sun','uranus']
	orbits = [[TimeSeries() for i in range(len(bodies))],[TimeSeries() for i in range(len(bodies))]]

	set_trace()
	for t in times:
		# for body in solar_system_ephemeris.bodies:
		
		for idx, body_name in enumerate(bodies):
			body = get_body(body_name, t).icrs.cartesian
			body2 = get_body(body_name, t).heliocentrictrueecliptic.cartesian
			x = body.x.to_value()
			y = body.y.to_value()
			x2 = body2.x.to_value()
			y2 = body2.y.to_value()

			orbits[0][idx][x] = y
			orbits[1][idx][x2] = y2
			print(t)

	colors = ['red', 'blue']
	for idx, orbits2 in enumerate(orbits):
		color = colors[idx]
		for orbit in orbits2:
			plot(orbit, color=color)

	# set_trace()
	savefig('build/orbits.png')
