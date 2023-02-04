import numpy as np
from shapely.geometry import Point, LineString


class TheRightRoute():
    def __init__(self, waypoints: LineString, acceptable_distance):
        self.route = waypoints
        self.acceptable_distance = acceptable_distance
        
        self.start_pt = Point(self.route.coords[0])
        self.finish_line = self.calc_finish_line()
    
    def calc_finish_line(self):
        if self.route.coords[-1][0]-self.route.coords[-2][0] == 0:
            RouteEndAngle = np.pi /2
        else:
            RouteEndAngle = np.arctan((self.route.coords[-1][1]-self.route.coords[-2][1])/ \
                                      (self.route.coords[-1][0]-self.route.coords[-2][0]))
        finish_line = LineString([
            Point(
                self.route.coords[-1][0] - self.acceptable_distance * np.sin(RouteEndAngle),
                self.route.coords[-1][1] + self.acceptable_distance * np.cos(RouteEndAngle)),
            Point(
                self.route.coords[-1][0] + self.acceptable_distance * np.sin(RouteEndAngle),
                self.route.coords[-1][1] - self.acceptable_distance * np.cos(RouteEndAngle))
        ])
        return finish_line

