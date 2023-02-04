#pathfinder/__main__.py


from pathfinder import cli, __appname__

def main():
    cli.app(prog_name=__appname__)

if __name__ == "__main__":
    main()