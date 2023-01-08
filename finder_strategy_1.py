import numpy as np
import pandas as pd

class FinderStrategy_1():
    
    def __init__(self, n_cars, n_steps, max_steering):
        self.n_cars = n_cars
        self.n_steps = n_steps
        self.max_steering = max_steering
    
    
    def generate_random_steering_angles(self, n_trajectories: int, length: int = None):
        if length is None:
            length = self.n_steps
        return [np.array([0] + list(self.max_steering*np.random.normal(0, 0.5, size=length))) \
                for i in range(n_trajectories)]
    
    
    def generate_twins(self, df_vehicles):
        v_best_score = df_vehicles.nlargest(n=1, columns='Score').iloc[0]
        base = v_best_score['Steering angles']
        n_adnl_combinations = self.n_cars - 1

        max_upto = int(v_best_score['TrajectoryLength'])
        shorten_halflength = int(0.05*v_best_score['TrajectoryLength'])
        list_keep_upto = max_upto - np.clip(np.abs(np.random.normal(0, max_upto/3.3, (n_adnl_combinations))), 0, max_upto).astype(int)

        output = [self.make_new_branch(base, keep_upto) if keep_upto > int(0.80*max_upto) \
                  else self.shorten_branch(base, v_best_score['Trajectory'], int(keep_upto-shorten_halflength), int(keep_upto+shorten_halflength)) \
                  for keep_upto in list_keep_upto]
        return [base] + output
    
    
    def make_new_branch(self, base, keep_upto):
        return np.concatenate((base[:keep_upto], self.generate_random_steering_angles(1, length=len(base)-keep_upto)[0]))
    
    
    def shorten_branch(self, base_angles, trajectory, rework_from, rework_to):
        deltaX = trajectory.coords[rework_to][0] - trajectory.coords[rework_from][0]
        deltaY = trajectory.coords[rework_to][1] - trajectory.coords[rework_from][1]
        n_steps_shortcut = int(np.round(np.sqrt(deltaX**2 + deltaY**2)))

        sum_prev_angles = np.sum(base_angles[:rework_from])
        ini_angle = np.sign(deltaY)*np.pi if deltaX == 0 else (np.arctan(deltaY/deltaX) - sum_prev_angles)
        finish_angle = np.sum(base_angles[:rework_to]) - sum_prev_angles - ini_angle

        new_length = rework_from + n_steps_shortcut + len(base_angles) - rework_to
        add_n_elements = rework_to - rework_from - n_steps_shortcut -1
        add_elements = [] if add_n_elements <= 0 else self.generate_random_steering_angles(1, 1+add_n_elements)[0][1:]

        new_angles = np.concatenate((base_angles[:rework_from], [ini_angle], np.zeros(n_steps_shortcut-2), \
                                     [finish_angle], base_angles[rework_to:], add_elements))[:len(base_angles)]
        return new_angles
    
    
    def calc_score(self, vehicle: pd.Series):
        return vehicle['DistanceFromStart'] - sum([abs(val) for val in vehicle['Steering angles']])

