def main():
    import argparse
    import os
    import datetime
    import frontmatter
    import yaml
    import shutil
    from .generator import generator
    from .httpserver import bestatic_serv
    from .quickstart import quickstart
    from .newcontent import newpost, newpage
    import bestatic

    parser = argparse.ArgumentParser(description="Program to accept command-line arguments in Bestatic")
    parser.add_argument("action", nargs="?", choices=["generator", "quickstart", "version", "newpage", "newpost"], default="generator",
                        help="Specify whether you are checking a version (argument: version),"
                             " initializing the site (argument: quickstart), or doing a build (argument: generator)."
                             " If only package name is entered, by default, we will assume that you are just trying to"
                             " build your website into '_output' directory")

    parser.add_argument("filename", nargs="?", help="For newpost or newpage argument, specify the filename(.md will "
                                                    "be added automatically)")
    parser.add_argument("--directory", "-d", help="Specify a custom directory. If not specified,"
                                                  " it will generate the website in '_output' directory by default")
    parser.add_argument("--theme", "-t", help="Specify the theme. If not specified, it will use the 'Amazing' theme.")
    parser.add_argument("--serve", "-s", action="store_true", help="Start server after the build...")

    args = parser.parse_args()

    if args.action == "quickstart":
        if args.theme:
            config = quickstart(args.theme)
        else:
            config = quickstart()

        generator(**config)

        config = quickstart()
        generator(**config)
    elif args.action == "version":
        print(f'Bestatic version: {bestatic.__version__}')
    elif args.action == "newpost":
        if not args.filename:
            raise ValueError("Please specify filename to use 'newpost' function.")
        else:
            os.chdir(os.getcwd())
            newpost(args.filename)
    elif args.action == "newpage":
        if not args.filename:
            raise ValueError("Please specify filename to use 'newpage' function.")
        else:
            os.chdir(os.getcwd())
            newpage(args.filename)
    else:
        with open("config.yaml", mode="rb") as ft:
            config = yaml.safe_load(ft)
        if args.theme:
            config["theme"] = args.theme

        theme = config["theme"]
        current_directory = os.getcwd()
        path = os.path.join(current_directory, "themes", theme)
        is_exist = os.path.exists(path)
        if not is_exist:
            raise FileNotFoundError(f"Theme directory does not exist! Please make sure a proper theme is present in themes directory")
        generator(**config)

    if args.directory:
        shutil.rmtree(args.directory) if os.path.exists(args.directory) else None
        os.rename("_output", args.directory)

    if args.serve:
        bestatic_serv(args.directory) if args.directory else bestatic_serv()


if __name__ == '__main__':
    main()
