def main():
    import argparse
    import os
    import tomli
    from .generator import generator
    from .httpserver import bestatic_serv
    from .quickstart import quickstart
    import bestatic

    parser = argparse.ArgumentParser(description="Program to accept command-line arguments in Bestatic")
    parser.add_argument("action", nargs="?", choices=["generator", "quickstart", "version"], default="generator",
                        help="Specify whether you are checking a version (argument: version),"
                             " initializing the site (argument: quickstart), or doing a build (argument: generator)."
                             " If only package name is entered, by default, we will assume that you are trying to build"
                             " it from the current directory.")
    parser.add_argument("--directory", "-d", help="Specify a custom directory. If not specified,"
                                                  " it will use the current directory.")
    parser.add_argument("--theme", "-t", help="Specify the theme. If not specified, it will use the Amazing theme.")
    parser.add_argument("--serve", "-s", action="store_true", help="Start server after the build...")

    args = parser.parse_args()

    if args.action == "quickstart":
        if args.directory:
            os.chdir(args.directory)
            if args.theme:
                config = quickstart(args.theme)
            else:
                config = quickstart()
            generator(**config)
        else:
            path = os.getcwd()  # os.path.dirname(os.path.abspath(__file__))
            config = quickstart()
            generator(**config)
    elif args.action == "version":
        print(f'Bestatic version: {bestatic.__version__}')
    else:
        if args.directory or args.theme:
            raise ValueError("Directory and theme can only be specified here during quickstart. Please update your "
                             "config.toml to specify theme. ")
        with open("config.toml", mode="rb") as ft:
            config = tomli.load(ft)
            generator(**config)

    if args.serve:
        bestatic_serv()


if __name__ == '__main__':
    main()
