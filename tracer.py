import datetime
import shlex
import os
import platform
import psycopg2

from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT
from time import sleep

ERROR_LOG_FILE = "network_errors.txt"
TIMEOUT = 20


class Tracer():

    def __init__(self, target, output_path):
        self.target = target
        self.output_path = output_path
        self.windows = platform.system() == "Windows"
        self.db = DB()

    def is_network_alive(self):
        cmd = "ping -c 1 {}".format(self.target)
        if self.windows:
            cmd = "ping /n 1 {}".format(self.target)
        args = shlex.split(cmd)
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        return p.returncode == 0, output.decode("utf-8").rstrip(), err.decode("utf-8").rstrip()

    def start_monitoring(self):
        while True:
            success, output, error = self.is_network_alive()
            if not success:
                print("Network not alive, sleeping")
                with open(os.path.join(self.output_path, ERROR_LOG_FILE), "a+") as error_file:
                    datetime = datetime.datetime.now()
                    log_line = "{} network unreachable due to {} - {}.\n".format(
                        datetime, output, error)
                    error_file.write(log_line)
                    self.db.add_error(datetime, "network unreachable due to {} - {}".format(output, error))
                sleep(TIMEOUT)
            else:
                sleep(0.5)


class DB():

    def __init__(self):
        self.conn = psycopg2.connect('dbname=network')
        self.cur = conn.cursor()

    def add_error(self, datetime, error):
        query = """
        INSERT INTO
            wifi_errors
        VALUES
            (%s, %s)
        """
        values = (datetime, error)
        self.cur.execute(query, values)

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
