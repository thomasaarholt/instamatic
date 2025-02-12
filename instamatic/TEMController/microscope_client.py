import socket
import pickle
import time
import atexit
from functools import wraps
import subprocess as sp
from instamatic import config

import datetime
import threading


# HOST = 'localhost'
# PORT = 8088

HOST = config.cfg.tem_server_host
PORT = config.cfg.tem_server_port
BUFSIZE = 1024


class ServerError(Exception):
    pass


def kill_server(p):
    # p.kill is not adequate
    sp.call(['taskkill', '/F', '/T', '/PID',  str(p.pid)])


def start_server_in_subprocess():
   cmd = "instamatic.temserver.exe"
   p = sp.Popen(cmd, stdout=sp.DEVNULL)
   print(f"Starting TEM server ({HOST}:{PORT} on pid={p.pid})")
   atexit.register(kill_server, p)


class MicroscopeClient(object):
    """
    Simulates a Microscope object and synchronizes calls over a socket server.
    For documentation, see the actual python interface to the microscope API.
    """
    def __init__(self, name):
        super().__init__()
        
        self.name = name
        self._bufsize = BUFSIZE

        try:
            self.connect()
        except ConnectionRefusedError:
            start_server_in_subprocess()

            for t in range(30):
                try:
                    self.connect()
                except ConnectionRefusedError:
                    time.sleep(1)
                    if t > 3:
                        print("Waiting for server")
                    if t > 30:
                        raise RuntimeError("Cannot establish server connection (timeout)")
                else:
                    break

        self._init_dict()

        atexit.register(self.s.close)
    
    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print(f"Connected to TEM server ({HOST}:{PORT})")

    def __getattr__(self, func_name):

        try:
            wrapped = self._dct[func_name]
        except KeyError as e:
            raise AttributeError(f"`{self.__class__.__name__}` object has no attribute `{func_name}`") from e

        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            dct = {"func_name": func_name,
               "args": args,
               "kwargs": kwargs}
            return self._eval_dct(dct)

        return wrapper

    def _eval_dct(self, dct):
        """Takes approximately 0.2-0.3 ms per call if HOST=='localhost'"""
        # t0 = time.perf_counter()

        self.s.send(pickle.dumps(dct))
        response = self.s.recv(self._bufsize)
        if response:
            status, data = pickle.loads(response)

        if status == 200:
            return data

        elif status == 500:
            raise data

        else:
            raise ConnectionError(f"Unknown status code: {status}")

    def _init_dict(self):
        from instamatic.TEMController.microscope import get_tem
        tem = get_tem(self.name)

        self._dct = {key:value for key, value in  tem.__dict__.items() if not key.startswith("_")}

    def __dir__(self):
        return self._dct.keys()


class TraceVariable(object):
    """docstring for Tracer"""
    def __init__(self, func, interval=1.0, name="variable", verbose=False):
        super().__init__()
        self.name = name
        self.func = func
        self.interval = interval
        self.verbose = verbose

        self._traced = []

    def start(self):
        print(f"Trace started: {self.name}")
        self.update()

    def stop(self):
        self._timer.cancel()

        print(f"Trace canceled: {self.name}")

        return self._traced

    def update(self):
        ret = self.func()
        
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")
    
        if self.verbose:
            print(f"{now} | Trace {self.name}: {ret}")
    
        self._traced.append((now, ret))
        
        self._timer = threading.Timer(self.interval, self.update)
        self._timer.start()
