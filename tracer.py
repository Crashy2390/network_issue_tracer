import datetime
import shlex
import os
import platform

from argparse import ArgumentParser
from subprocess import call, PIPE, STDOUT
from time import sleep

ERROR_LOG_FILE = "network_errors.txt"
TIMEOUT = 20


class Tracer():

    def __init__(self, target, output_path):
        self.target = target
        self.output_path = output_path
        self.windows = platform.system() == "Windows"

    def is_network_alive(self):
        cmd = "ping -c 1 {}".format(self.target)
        if self.windows:
            cmd = "ping /n 1 {}".format(self.target)
        args = shlex.split(cmd)
        return call(args, stdout=PIPE, stderr=STDOUT) == 0

    def start_monitoring(self):
        while True:
            if not self.is_network_alive():
                print("Network not alive, sleeping")
                with open(os.path.join(self.output_path, ERROR_LOG_FILE), "w+") as error_file:
                    log_line = "{} network unreachable.\n".format(
                        datetime.datetime.now())
                    error_file.write(log_line)
                sleep(TIMEOUT)
            else:
                sleep(0.5)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-o", "--output_path",
                        action="store", dest="output_path")
    parser.add_argument("-t", "--target", action="store", dest="target")
    args = parser.parse_args()

    if not args.output_path or not args.target:
        parser.print_help()
        exit(1)
    print("output_path: {}".format(args.output_path))
    print("target: {}".format(args.target))

    tracer = Tracer(args.target, args.output_path)
    tracer.start_monitoring()
