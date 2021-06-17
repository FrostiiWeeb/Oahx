import subprocess
import argparse
import sys

class OGit():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("run", help="run the program")
        args = self.parser.parse_args(sys.argv[1:2])
        if args.run == "run":
            print(subprocess.check_output('git rm -r --cached . && git add . && git commit -m "ok" && git push heroku master', shell=True))
        
OGit()     
