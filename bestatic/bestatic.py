import argparse
import os
import datetime
import sys
import time
import frontmatter
import yaml
import shutil
import multiprocessing
import signal
import watchdog.events
import watchdog.observers
from bestatic.generator import generator
from bestatic.httpserver import bestatic_serv
from bestatic.quickstart import quickstart
from bestatic.newcontent import newpost, newpage
import bestatic
import pdb

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
                super().__init__(patterns=['*'], ignore_patterns=['*~', os.path.join(os.getcwd(), "_output"),
                                                                  dir_ignore], ignore_directories=True)
            else:
                super().__init__(patterns=['*'], ignore_patterns=['*~', os.path.join(os.getcwd(), "_output")],
                                 ignore_directories=True)

        def on_any_event(self, event):
            if not event.is_directory:
                print(f"Event type: File {event.event_type}")
                print(f"File Path: {event.src_path}")
                if event.event_type in ["modified", "created", "moved", "deleted"]:
                    # current_time = datetime.datetime.now()
                    # if (current_time - RebuildEventHandler.last_rebuild_time) > self.delay:
                    print("Triggering rebuild...")
                    if event.src_path.endswith("config.yaml"):
                        print("Detected configuration change...")
                        with open("config.yaml", mode="rb") as ft:
                            self.config = yaml.safe_load(ft)
                        if not os.path.exists(os.path.join(os.getcwd(), "themes", config["theme"])):
                            raise FileNotFoundError(
                                f"Theme directory does not exist! Please make sure a proper theme is present inside "
                                f"the 'themes' directory")
                    generator(**self.config)

                    if directoryname[0] and os.path.exists(directoryname[0]):
                        shutil.rmtree(directoryname[0])
                        os.rename("_output", directoryname[0])
                    else:
                        pass
                    print("Rebuild is sucessful!!\nClick http://localhost:8080 to visit "
                          "the live website again.\nMonitoring files again...\n"
                          "Press Ctrl+C to stop anytime...")

    event_handler = RebuildEventHandler()
    observer = watchdog.observers.Observer()

    directories_to_watch = [
        "themes",
        "posts",
        "pages",
        "static-content"
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
    parser = argparse.ArgumentParser(description="Program to accept command-line arguments in Bestatic")
    parser.add_argument("action", nargs="?", choices=["generator", "quickstart", "version", "newpage", "newpost"],
                        default="generator",
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
    parser.add_argument("--autoreload", "-a", action="store_true",
                        help="Start watching for file changes and automatically rebuild the website.")

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
        current_directory = os.getcwd()
        if not os.path.isfile(os.path.join(current_directory,"config.yaml")) or not os.path.exists(os.path.join(current_directory,"themes")):
            print("\nThank you for trying out Bestatic!\n"
                  "Please note that you need to have have a 'config.yaml' file and 'themes' folder in the working directory "
                  "to correctly build the site.\nYou can generate a config.yaml file by running 'bestatic quickstart'. \n"
                  "You can download a theme from the github repo.\n"
                  "After having those in current directory, please run the program again.\n\n"
                  "This program will exit soon. Please visit https://www.bestaticpy.com for more information.\n")
            time.sleep(2)
            sys.exit(1)
        with open("config.yaml", mode="rb") as ft:
            config = yaml.safe_load(ft)
        if args.theme:
            config["theme"] = args.theme

        theme = config["theme"]

        path = os.path.join(current_directory, "themes", theme)
        is_exist = os.path.exists(path)
        if not is_exist:
            raise FileNotFoundError(
                f"Theme directory does not exist! Please make sure a proper theme is present inside 'themes' directory")
        generator(**config)

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
        run_server(args.directory) if args.directory else run_server()

if __name__ == '__main__':
    main()
