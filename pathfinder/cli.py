#pathfinder/cli.py

import numpy as np
from typing import Optional
import typer
app = typer.Typer(rich_markup_mode="rich")

from pathfinder import __appname__, __version__


@app.command()
def main(
    n_cars: int = typer.Option(20, '--n-cars', '-n', help='Number of cars to simulate.', min=1, rich_help_panel='Customization of simulation'),
    n_loops: int = typer.Option(20, '--n-loops', '-l', help='Number of loops to simulate.', min=1, rich_help_panel='Customization of simulation'),
    step_length: float = typer.Option(1, '--step-length', '-s', help='Lenght of cars\' steps', min=1, rich_help_panel='Customization of simulation'),
    acceptable_distance: float = typer.Option(10, '--acc-distance', '-d', help='Defines the half-width of the "road".', min=1, rich_help_panel='Customization of simulation'),
    max_steering: float = typer.Option(45 * np.pi / 180, '--max-steering', '-a', help='Maximum steering angle for the cars, in radians. Default 45deg.', rich_help_panel='Customization of simulation'), #Default 45deg in radians
) -> None:
    
    from shapely.geometry import Point, LineString
    from pathfinder.the_right_route import TheRightRoute
    from pathfinder.finder_strategy_1 import FinderStrategy_1
    from pathfinder.pathfinder import PathFinder
    
    # RouteToFollow = LineString([(0,0), (60,100)]) # Straight line
    RouteToFollow = LineString([(0,0), (60, 0), (60, 60)]) # L-shape
    # RouteToFollow = LineString([(0,0), (60, 0), (60, 60), (100, 50), (90, 30), (90, 0), (120,0)]) # Bumpy road
    # RouteToFollow = LineString([(0,0), (60, 0), (60, 60), (100, 50), (75, 30), (90, 0), (120,0)]) # Bumpy road with shortcut
    # RouteToFollow = LineString([(0,0), (60, 0), (60, 60), (100, 50), (90, 30), (90, 0), (120,0), (130,90), (10, 85), (10, 30)]) # Snail
    # RouteToFollow = LineString([(0,0), (20, 0), (20, 30), (50, 30), (50, -30), (20, -30), (20,-60), (80,-60), (80, 60), \
    #                             (-30, 60), (-30, 0), (0, -90), (110, -90), (110, 0), (130, 0)]) # Labyrinth
    
    the_right_route = TheRightRoute(RouteToFollow, acceptable_distance)
    n_steps = int(the_right_route.route.length*1.5)
    
    pf = PathFinder(the_right_route, FinderStrategy_1, acceptable_distance, n_cars, n_steps, n_loops, step_length, max_steering)
    pf.run_simulation()
    pf.display_interactive_plot()
    return