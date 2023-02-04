import numpy as np
import pandas as pd
from tqdm import tqdm
from itertools import takewhile
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import geopandas as gpd

class PathFinder():
    def __init__(self, the_right_route, finder_strategy, acceptable_distance, n_cars, n_steps, n_loops, step_length, max_steering):
        self.the_right_route = the_right_route
        
        self.acceptable_distance = acceptable_distance
        self.n_cars = n_cars
        self.n_steps = n_steps
        self.n_loops = n_loops
        self.step_length = step_length
        self.max_steering = max_steering
        
        self.finder_strategy = finder_strategy(self.n_cars, self.n_steps, self.max_steering)
        
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
    
    
    def display_interactive_plot_notebook(self):
        import ipywidgets as widgets
        widgets.interact(self.plot_path_notebook, loop = widgets.IntSlider(
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
    
    
    def make_gdf_shapes_on_map(self, vehicles, loop):
        shapes_on_map = [{'geometry': self.the_right_route.start_pt, 'name': 'Start'},
                         {'geometry': self.the_right_route.finish_line, 'name': 'Finish'},
                         {'geometry': self.the_right_route.route.buffer(self.acceptable_distance, cap_style=2), 'name': 'Route to follow'}]
        vehicles.apply(lambda row: shapes_on_map.append({
            'geometry': row['Trajectory'],
            'name': f'Car{row.name}'
        }), axis=1)

        return gpd.GeoDataFrame(shapes_on_map)
    
    
    def plot_path_notebook(self, loop):
        vehicles = self.vehicles_history.loc[self.vehicles_history['Loop'] == loop]
        gdf = self.make_gdf_shapes_on_map(vehicles, loop)
        ax = gdf.plot(column='name', figsize=(12,6), cmap='RdYlBu')#, legend=True)
        ax.set_title(f"Loop {loop} || Max score {vehicles['Score'].max():.2f} || Max dist from start {vehicles['DistanceFromStart'].max():.2f}", y=1.0, pad=-14, fontsize=8)

        dims = np.round(gdf.total_bounds*1.10)
        plt.xlim(dims[0], dims[2])
        plt.ylim(dims[1], dims[3])
        plt.grid()
        plt.show()
    
    
    def plot_path(self, loop):
        vehicles = self.vehicles_history.loc[self.vehicles_history['Loop'] == loop]
        gdf = self.make_gdf_shapes_on_map(vehicles, loop)
        
        self.ax.clear()
        self.ax.set_xlim(self.the_right_route.route.bounds[0] - 1.5 * self.acceptable_distance, self.the_right_route.route.bounds[2] + 1.5 * self.acceptable_distance)
        self.ax.set_ylim(self.the_right_route.route.bounds[1] - 1.5 * self.acceptable_distance, self.the_right_route.route.bounds[3] + 1.5 * self.acceptable_distance)
        self.ax.set_aspect('equal', adjustable='box')
        
        self.ax = gdf.plot(column='name', figsize=(12,6), cmap='RdYlBu', ax=self.ax)
        
        self.ax.set_title(f"Loop {loop} || Max score {vehicles['Score'].max():.2f} || Max dist from start {vehicles['DistanceFromStart'].max():.2f}", fontsize=8)
        self.fig.canvas.draw_idle()
        

    def display_interactive_plot(self):
        from matplotlib.widgets import Slider
        
        self.fig, self.ax = plt.subplots()
        self.fig.suptitle('Path finding by stochastic reinforcement', fontsize=16)
        
        loop = 0
        self.plot_path(loop)
        self.ax.set_position([0.05, 0.15, 0.90, 0.75])
        
        self.fig.subplots_adjust(bottom=0.15)
        
        # Horizontal slider
        ax_loopchoser = self.fig.add_axes([0.20, 0.05, 0.70, 0.03])
        loopchoser_slider = Slider(
            ax=ax_loopchoser,
            label=f'Loop no. [0...{self.n_loops}]',
            valmin=0,
            valmax=self.n_loops,
            valinit=0,
            valstep=1
        )
        loopchoser_slider.label.set_size(8)
        loopchoser_slider.on_changed(lambda loop: self.plot_path(loop))
        
        plt.show()
        
        
        
        