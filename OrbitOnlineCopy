import matplotlib.pyplot as plt
import math
plt.ion()

G = 6.673e-11  # gravity constant
gridArea = [0, 200, 0, 200]  # margins of the coordinate grid
gridScale = 1000000  # 1 unit of grid equals 1000000m or 1000km

plt.clf()  # clear plot area
plt.axis(gridArea)  # create new coordinate grid
plt.grid(b="on")  # place grid

class Object:
    _instances = []
    def __init__(self, name, position, radius, mass):
        self.name = name
        self.position = position
        self.radius = radius  # in grid values
        self.mass = mass
        self.placeObject()
        self.velocity = 0
        Object._instances.append(self)

    def placeObject(self):
        drawObject = plt.Circle(self.position, radius=self.radius, fill=False, color="black")
        plt.gca().add_patch(drawObject)
        plt.show()

    def giveMotion(self, deltaV, motionDirection, time):
        if self.velocity != 0:
            x_comp = math.sin(math.radians(self.motionDirection))*self.velocity
            y_comp = math.cos(math.radians(self.motionDirection))*self.velocity
            x_comp += math.sin(math.radians(motionDirection))*deltaV
            y_comp += math.cos(math.radians(motionDirection))*deltaV
            self.velocity = math.sqrt((x_comp**2)+(y_comp**2))

            if x_comp > 0 and y_comp > 0:  # calculate degrees depending on the coordinate quadrant
                self.motionDirection = math.degrees(math.asin(abs(x_comp)/self.velocity))  # update motion direction
            elif x_comp > 0 and y_comp < 0:
                self.motionDirection = math.degrees(math.asin(abs(y_comp)/self.velocity)) + 90
            elif x_comp < 0 and y_comp < 0:
                self.motionDirection = math.degrees(math.asin(abs(x_comp)/self.velocity)) + 180
            else:
                self.motionDirection = math.degrees(math.asin(abs(y_comp)/self.velocity)) + 270

        else:
            self.velocity = self.velocity + deltaV  # in m/s
            self.motionDirection = motionDirection  # degrees
        self.time = time  # in seconds
        self.vectorUpdate()

    def vectorUpdate(self):
        self.placeObject()
        data = []

        for t in range(self.time):
            motionForce = self.mass * self.velocity  # F = m * v
            x_net = 0
            y_net = 0
            for x in [y for y in Object._instances if y is not self]:
                distance = math.sqrt(((self.position[0]-x.position[0])**2) +
                             (self.position[1]-x.position[1])**2)
                gravityForce = G*(self.mass * x.mass)/((distance*gridScale)**2)

                x_pos = self.position[0] - x.position[0]
                y_pos = self.position[1] - x.position[1]

                if x_pos <= 0 and y_pos > 0:  # calculate degrees depending on the coordinate quadrant
                    gravityDirection = math.degrees(math.asin(abs(y_pos)/distance))+90

                elif x_pos > 0 and y_pos >= 0:
                    gravityDirection = math.degrees(math.asin(abs(x_pos)/distance))+180

                elif x_pos >= 0 and y_pos < 0:
                    gravityDirection = math.degrees(math.asin(abs(y_pos)/distance))+270

                else:
                    gravityDirection = math.degrees(math.asin(abs(x_pos)/distance))

                x_gF = gravityForce * math.sin(math.radians(gravityDirection))  # x component of vector
                y_gF = gravityForce * math.cos(math.radians(gravityDirection))  # y component of vector

                x_net += x_gF
                y_net += y_gF

            x_mF = motionForce * math.sin(math.radians(self.motionDirection))
            y_mF = motionForce * math.cos(math.radians(self.motionDirection))
            x_net += x_mF
            y_net += y_mF
            netForce = math.sqrt((x_net**2)+(y_net**2))

            if x_net > 0 and y_net > 0:  # calculate degrees depending on the coordinate quadrant
                self.motionDirection = math.degrees(math.asin(abs(x_net)/netForce))  # update motion direction
            elif x_net > 0 and y_net < 0:
                self.motionDirection = math.degrees(math.asin(abs(y_net)/netForce)) + 90
            elif x_net < 0 and y_net < 0:
                self.motionDirection = math.degrees(math.asin(abs(x_net)/netForce)) + 180
            else:
                self.motionDirection = math.degrees(math.asin(abs(y_net)/netForce)) + 270

            self.velocity = netForce/self.mass  # update velocity
            traveled = self.velocity/gridScale  # grid distance traveled per 1 sec
            self.position = (self.position[0] + math.sin(math.radians(self.motionDirection))*traveled,
                             self.position[1] + math.cos(math.radians(self.motionDirection))*traveled)  # update pos
            data.append([self.position[0], self.position[1]])

            collision = 0
            for x in [y for y in Object._instances if y is not self]:
                if (self.position[0] - x.position[0])**2 + (self.position[1] - x.position[1])**2 <= x.radius**2:
                    collision = 1
                    break
            if collision != 0:
                print("Collision!")
                break

        plt.plot([x[0] for x in data], [x[1] for x in data])

Earth = Object(name="Earth", position=(50.0, 50.0), radius=6.371, mass=5.972e24)
Moon = Object(name="Moon", position=(100.0, 100.0), radius=1.737, mass = 7.347e22)  # position not to real scale
Craft = Object(name="SpaceCraft", position=(49.0, 40.0), radius=1, mass=1.0e4)

Craft.giveMotion(deltaV=8500.0, motionDirection=100, time=130000)
Craft.giveMotion(deltaV=2000.0, motionDirection=90, time=60000)
plt.show(block=True)