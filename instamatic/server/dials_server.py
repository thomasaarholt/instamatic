import sys
import subprocess as sp
from socket import *
import datetime

from instamatic import config
import logging
import threading
from pathlib import Path

import pickle
import ast


try:
    EXE = Path(sys.argv[1])
except:
    EXE = Path(config.cfg.dials_script)

CWD = EXE.parent

HOST = config.cfg.indexing_server_host
PORT = config.cfg.indexing_server_port
BUFF = 1024


def parse_dials_index_log(fn="dials.index.log"):
    with open(fn, "r") as f:
        print("Unit cell = ...")


def run_dials_indexing(data):
    cmd = [str(EXE), data["path"]]
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    fn = config.logs_drc / f"Dials_indexing_{date}.log"
    unitcelloutput = []

    p = sp.Popen(cmd, cwd=CWD, stdout = sp.PIPE)
    for line in p.stdout:
        if b'Unit cell:' in line:
            print(line.decode('utf-8'))
            unitcelloutput = line

    if unitcelloutput:
        with open(fn, "a") as f:
            f.write(f"\nData Path: {data["path"]}\n")
            f.write("{}".format(unitcelloutput[4:].decode('utf-8')))
            f.write(f"Rotation range: {data["rotrange"]} degrees\n")
            f.write(f"Number of frames: {data["nframes"]}\n")
            f.write(f"Oscillation angle: {data["osc"]} deg\n\n\n\n")
            print(f"Indexing result written to dials indexing log file; path: {data["path"]}")
    
    p.wait()
    unitcelloutput = []
    now = datetime.datetime.now().strftime("%H:%M:%S.%f")
    print(f"{now} | DIALS indexing has finished")


def handle(conn):
    """Handle incoming connection."""
    ret = 0

    while True:
        data = conn.recv(BUFF).decode()
        data = ast.literal_eval(data)
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")

        if not data:
            break
    
        print(f"{now} | {data}")
        if data == "close":
            print(f"{now} | Closing connection")
            break

        elif data == "kill":
            print(f"{now} | Killing server")
            ret = 1
            break

        else:
            conn.send(b"OK")
            run_dials_indexing(data)

    conn.send(b"Connection closed")
    conn.close()
    print("Connection closed")

    return ret


def main():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    logfile = config.logs_drc / f"instamatic_indexing_server_{date}.log"
    logging.basicConfig(format="%(asctime)s | %(module)s:%(lineno)s | %(levelname)s | %(message)s", 
                        filename=logfile, 
                        level=logging.DEBUG)
    logging.captureWarnings(True)
    log = logging.getLogger(__name__)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(5)

    log.info(f"Indexing server (DIALS) listening on {HOST}:{PORT}")
    log.info(f"Running command: {EXE}")
    print(f"Indexing server (DIALS) listening on {HOST}:{PORT}")
    print(f"Running command: {EXE}")

    with s:
        while True:
            conn, addr = s.accept()
            log.info('Connected by %s', addr)
            print('Connected by', addr)
            threading.Thread(target=handle, args=(conn,)).start()

    
if __name__ == '__main__':
    main()
