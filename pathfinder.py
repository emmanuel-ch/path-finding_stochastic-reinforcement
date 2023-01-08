import numpy as np
import pandas as pd
from tqdm import tqdm
from itertools import takewhile
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import ipywidgets as widgets
import geopandas as gpd

class PathFinder():
    def __init__(self, the_right_route, finder_strategy, acceptable_distance, n_cars, n_steps, n_loops, step_length):
        self.the_right_route = the_right_route
        self.finder_strategy = finder_strategy # Why not generate instance of strategy WITHIN here? (more safe re variables)
        
        self.acceptable_distance = acceptable_distance
        self.n_cars = n_cars
        self.n_steps = n_steps
        self.n_loops = n_loops
        self.step_length = step_length
        
        self.vehicles_history = None
    
    
    def run_simulation(self):
        steering_angles = self.finder_strategy.generate_random_steering_angles(self.n_cars)
        self.vehicles_history = pd.DataFrame()

        for loop in tqdm(range(self.n_loops+1)):
            vehicles = self.calc_vehicles_df(loop, steering_angles)
            self.vehicles_history = pd.concat([self.vehicles_history, vehicles])
            steering_angles = self.finder_strategy.generate_twins(vehicles) # Prep next iteration. MOST IMPORTANT STEP FOR LEARNING!
        return None
    
    
    def calc_vehicles_df(self, loop, steering_angles):
        vehicles = pd.DataFrame({'Loop': loop, 'Steering angles': steering_angles})
        vehicles['Trajectory'] = vehicles['Steering angles'].apply(self.calc_trajectory)
        vehicles['DistanceFromStart'] = vehicles['Trajectory'].apply(self.calc_distance_from_start)
        vehicles['TrajectoryLength'] = vehicles['Trajectory'].apply(lambda traj: traj.length)
        vehicles['Score'] = vehicles.apply(self.finder_strategy.calc_score, axis=1)
        return vehicles
    
    
    def calc_trajectory(self, steering_angles):
        steering_angles_cumsum = np.cumsum(steering_angles)
        Xpts = (self.step_length*np.cos(steering_angles_cumsum)).cumsum()
        Ypts = (self.step_length*np.sin(steering_angles_cumsum)).cumsum()
        
        trajectory = [self.the_right_route.start_pt] + list(takewhile(lambda pt: pt.distance(self.the_right_route.route) <= self.acceptable_distance, self.gen_points(Xpts, Ypts)))
        return LineString(trajectory)
    
    
    def gen_points(self, Xpts, Ypts):
        for pt in list(zip(Xpts, Ypts)):
            yield Point(pt[0], pt[1])
    
    
    def calc_distance_from_start(self, trajectory):
        return self.the_right_route.route.project(Point(list(trajectory.coords)[-1]))
    
    
    def display_interactive_plot(self):
        widgets.interact(self.plot_path, loop = widgets.IntSlider(
            value=0,
            min=0,
            max=self.n_loops,
            step=1,
            description='Loop:',
            disabled=False,
            orientation='horizontal',
            continuous_update=True,
            readout=True,
            readout_format='d',
            layout=widgets.Layout(width='95%')
        ));
    
    
    def plot_path(self, loop):
        vehicles = self.vehicles_history.loc[self.vehicles_history['Loop'] == loop]
        shapes_on_map = [{'geometry': self.the_right_route.start_pt, 'name': 'Start'},
                         {'geometry': self.the_right_route.finish_line, 'name': 'Finish'},
                         {'geometry': self.the_right_route.route.buffer(self.acceptable_distance, cap_style=2), 'name': 'Route to follow'}]
        vehicles.apply(lambda row: shapes_on_map.append({
            'geometry': row['Trajectory'],
            'name': f'Car{row.name}'
        }), axis=1)

        gdf = gpd.GeoDataFrame(shapes_on_map)
        ax = gdf.plot(column='name', figsize=(12,6), cmap='RdYlBu')#, legend=True)
        ax.set_title(f"Loop {loop} || Max score {vehicles['Score'].max():.2f} || Max dist from start {vehicles['DistanceFromStart'].max():.2f}", y=1.0, pad=-14, fontsize=8)

        dims = np.round(gdf.total_bounds*1.10)
        plt.xlim(dims[0], dims[2])
        plt.ylim(dims[1], dims[3])
        plt.grid()
        plt.show()

