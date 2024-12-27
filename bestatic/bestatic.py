import argparse
import os
import datetime
import sys
import time
import frontmatter
import yaml
import shutil
import multiprocessing
import watchdog.events
import watchdog.observers
from bestatic.generator import generator
from bestatic.httpserver import bestatic_serv
from bestatic.quickstart import quickstart
from bestatic.newcontent import newpost, newpage
import bestatic


def run_server(directory):
    bestatic_serv(directory) if directory else bestatic_serv()


def run_watcher(config, *directoryname):
    class RebuildEventHandler(watchdog.events.PatternMatchingEventHandler):
        # last_rebuild_time = datetime.datetime.now()
        # delay = datetime.timedelta(seconds=1)
        def __init__(self):
            self.config = config
            dir_ignore = os.path.join(os.getcwd(), directoryname[0]) if directoryname[0] else None
            if directoryname[0]:
                super().__init__(patterns=['*'], ignore_patterns=['*~', '.*', os.path.join(os.getcwd(), "_output"),
                                                                  dir_ignore], ignore_directories=True)
            else:
                super().__init__(patterns=['*'], ignore_patterns=['*~', '.*', os.path.join(os.getcwd(), "_output")],
                                 ignore_directories=True)

        def on_any_event(self, event):
            if not event.is_directory and event.event_type in ["modified", "created", "moved", "deleted"]:
                print(f"Event type: File {event.event_type}")
                print(f"File Path: {event.src_path}")
                # current_time = datetime.datetime.now()
                # if (current_time - RebuildEventHandler.last_rebuild_time) > self.delay:
                print("Triggering rebuild...")
                
                if event.src_path.endswith(("bestatic.yaml", "config.yaml")):
                    print("Detected configuration change...")
                    config_file = "bestatic.yaml"
                    if not os.path.isfile(config_file):
                        config_file = "config.yaml"
                    with open(config_file, mode="rb") as ft:
                        self.config = yaml.load(ft, Loader=yaml.Loader)
                    if not os.path.exists(os.path.join(os.getcwd(), "themes", self.config["theme"])):
                        raise FileNotFoundError(
                            f"Theme directory does not exist! Please make sure a proper theme is present inside "
                            f"the 'themes' directory")
                generator(**self.config)

                if directoryname[0] and os.path.exists(directoryname[0]):
                    shutil.rmtree(directoryname[0])
                    os.rename("_output", directoryname[0])
                else:
                    pass
                print("Rebuild is successful!!\nClick http://localhost:8080 to visit "
                        "the live website again.\nMonitoring files again...\n"
                        "Press Ctrl+C to stop anytime...")

    event_handler = RebuildEventHandler()
    observer = watchdog.observers.Observer()

    directories_to_watch = [
        "themes",
        "posts",
        "pages",
        "static-content",
        "_includes"
    ]

    for directory in directories_to_watch:
        directory_path = os.path.join(os.getcwd(), directory)
        if os.path.exists(directory_path):
            observer.schedule(event_handler, directory_path, recursive=True)
        else:
            pass

    observer.schedule(event_handler, os.getcwd(), recursive=False)

    observer.start()

    try:
        print("\nConstantly watching for changes in files...\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    return None


def main():
    parser = argparse.ArgumentParser(description="Program to accept command-line inputs in Bestatic...")
    parser.add_argument("action", nargs="?", choices=["generator", "quickstart", "version", "newpage", "newpost"],
                        default="generator",
                        help="""
                        How it works:
                        1) 'bestatic version': Prints the currently installed version of bestatic. \t
                        2) 'bestatic quickstart': Creates a 'bestatic.yaml' file by accepting user input, 
                        creates two pages and two posts, and finally build the website in '_output' directory. \t
                        3) 'bestatic newpage filepath' or 'betatic newpost filepath':  Creates a new page (inside './pages' directory)
                        or new post (inside './posts' directory), respectively, at the specified filepath. See 'filepath' argument for more details.
                        4) 'bestatic' or 'bestatic generator':  If 'bestatic.yaml' file or 'themes' directory is not 
                        present in current working directory, bestatic prints that message.
                        If everything is in order in current working directory, bestatic build your website into '_output' directory.
                        """)

    parser.add_argument("filepath", nargs="?", help="For newpost or newpage argument, specify the filepath. "
                                                    "The.md extension will "
                                                    "be added automatically. If subdirectories do not exist, bestatic will"
                                                    " create them. For e.g., 'bestatic newpost sub/directory/test1' will"
                                                    " create 'test1.md' inside './sub/directory/' directory.")
    parser.add_argument("--directory", "-d", help="Specify a custom directory where you want to get the final "
                                                  "compiled version of the website (and serve from there). If not specified,"
                                                  " bestatic will generate the website in '_output' directory by default.")
    parser.add_argument("--theme", "-t", help="Specify the theme. If nothing is specified, bestatic will "
                                              "use the 'Amazing' theme, provided is there in the 'themes' directory."
                                              " You can create your own theme or download more from the GitHub repo")
    parser.add_argument("--serve", "-s", action="store_true", help="Start server after the build. You can visit"
                                                                   " https://localhost:8080 to visit the live version of your"
                                                                   " webpage locally.")
    parser.add_argument("--autoreload", "-a", action="store_true",
                        help="When '-a' or '--autoreload' is specified, bestatic will watch the current directory "
                             "recursively for for any changes in files and then will automatically rebuild the website. "
                             "Use 'bestatic -sa' and reload https://localhost:8080 to see your changes in action live!")

    parser.add_argument("--projectsite", "-p", help="Use this flag if and only if you are deploying your "
                                                    "website as a Github (or Gitlab) Pages 'Project site' (and not "
                                                    "as a 'User site'), without a custom domain or subdomain. For example, "
                                                    "you are deploying your site to https://<username>.github.io/<repository> "
                                                    "and not to https://<username>.github.io or https://yourdomain.com."
                                                    " Please use this format: bestatic -p https://<username>.github.io/<repository>.")

    args = parser.parse_args()

    if args.action == "quickstart":
        if args.theme:
            config = quickstart(args.theme)
        else:
            config = quickstart()

        generator(**config)

        # config = quickstart()
        # generator(**config)
    elif args.action == "version":
        print(f'Bestatic version: {bestatic.__version__}')
    elif args.action == "newpost":
        if not args.filepath:
            raise ValueError("Please specify filepath to use 'newpost' function.")
        else:
            os.chdir(os.getcwd())
            try:
                # Try bestatic.yaml first, then config.yaml as fallback (Introduced in v 0.0.29)
                config_file = "bestatic.yaml"
                if not os.path.isfile(config_file):
                    config_file = "config.yaml"
                with open(config_file, mode="rb") as ft:
                    config = yaml.load(ft, Loader=yaml.Loader)
                time_format = config.get('time_format', "%B %d, %Y")
            except:
                time_format = "%B %d, %Y"  # fallback            
            newpost(args.filepath, time_format)

    elif args.action == "newpage":
        if not args.filepath:
            raise ValueError("Please specify filepath to use 'newpage' function.")
        else:
            os.chdir(os.getcwd())
            newpage(args.filepath)
    else:
        current_directory = os.getcwd()
        config_file = os.path.join(current_directory, "bestatic.yaml")
        if not os.path.isfile(config_file):
            config_file = os.path.join(current_directory, "config.yaml")
        
        if not os.path.isfile(config_file) or not os.path.exists(os.path.join(current_directory, "themes")):
            print("\nThank you for trying out Bestatic!\n"
                  "Please note that you need to have have a 'bestatic.yaml' file and 'themes' directory within the working directory "
                  "to correctly build the site.\nYou can generate a bestatic.yaml file by running 'bestatic quickstart'. \n"
                  "You can download a theme from the GitHub repo.\n"
                  "After having those in current directory, please run the program again.\n"
                  "If you are starting the program graphically from desktop or start manu icon, please retry launching "
                  "it from the command line and from the correct directory. \n\n"
                  "This program will exit soon. Please visit https://www.bestaticpy.com for more information.\n")
            time.sleep(4)
            sys.exit(1)

        with open(config_file, mode="rb") as ft:
            config = yaml.load(ft, Loader=yaml.Loader)

        if args.theme:
            config["theme"] = args.theme

        theme = config["theme"]

        path = os.path.join(current_directory, "themes", theme)
        is_exist = os.path.exists(path)
        if not is_exist:
            raise FileNotFoundError(
                f"Theme directory does not exist! Please make sure a proper theme is present inside 'themes' directory")

        if args.projectsite:
            config["projectsite"] = args.projectsite

        generator(**config)
        print("Bestatic has completed execution...")
        time.sleep(1)

    if args.directory:
        shutil.rmtree(args.directory) if os.path.exists(args.directory) else None
        os.rename("_output", args.directory)

    if args.autoreload and args.serve:
        # Start server in a separate process
        server_process = multiprocessing.Process(target=run_server, args=(args.directory,))
        server_process.start()

        try:
            run_watcher(config, args.directory)
        except KeyboardInterrupt:
            server_process.terminate()  # Terminate the server process
            server_process.join()  # Wait for the process to finish
        else:
            print("Bestatic will now stop watching files...")

    elif args.serve and not args.autoreload:
        bestatic_serv(args.directory) if args.directory else bestatic_serv()
    return None


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
