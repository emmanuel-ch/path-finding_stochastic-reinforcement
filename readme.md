# Path-finding with Stochastic reinforcement

This is an experience of automated learning by using a strategy driven by stochastic generation of solution and positive reinforcement.

![Example of path-finding](Assets/Screenshot-Labyrinth.png?raw=true "Example of path-finding")

## Framework & Usage

It takes the analogy of cars driving on a pre-defined track.
3 classes make this framework:
- The track, class name TheRightRoute
- The strategy, example class name FinderStrategy_1. This is a basic strategy that can be refined. Feel free to suggest additional ones.
- The experiment manager, class name PathFinder

Open / run the main notebook Main experiment notebook.ipynb

## Requirements
Developed on Python 3.10. Non-standard packages used:
- numpy
- pandas
- tqdm
- shapely
- matplotlib
- ipywidgets
- geopandas

## Contributing

You found this repo and you like it? Feel free to contact me or to raise an issue!
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

