from tkinter import *
from tkinter.ttk import *
import threading
from instamatic.utils.spinbox import Spinbox


class ExperimentalCtrl(LabelFrame):
    """docstring for ExperimentalCtrl"""
    def __init__(self, parent):
        LabelFrame.__init__(self, parent, text="Stage Control")
        self.parent = parent

        self.init_vars()

        frame = Frame(self)

        b_stage_stop = Button(frame, text="Stop stage", command=self.stage_stop)
        b_stage_stop.grid(row=0, column=2, sticky="W")

        cb_nowait = Checkbutton(frame, text="Wait for stage", variable=self.var_stage_wait)
        cb_nowait.grid(row=0, column=3)

        b_find_eucentric_height = Button(frame, text="Find eucentric height", command=self.find_eucentric_height)
        b_find_eucentric_height.grid(row=0, column=0, sticky="EW", columnspan=2)

        Label(frame, text="Mode:").grid(row=8, column=0, sticky="W")
        self.o_mode = OptionMenu(frame, self.var_mode, 'diff', 'diff', 'mag1', 'mag2', 'lowmag', 'samag', command=self.set_mode)
        self.o_mode.grid(row=8, column=1, sticky="W", padx=10)

        frame.pack(side="top", fill="x", padx=10, pady=10)

        frame = Frame(self)

        Label(frame, text="Angle (-)", width=20).grid(row=1, column=0, sticky="W")
        Label(frame, text="Angle (0)", width=20).grid(row=2, column=0, sticky="W")
        Label(frame, text="Angle (+)", width=20).grid(row=3, column=0, sticky="W")
        Label(frame, text="Alpha wobbler (±)", width=20).grid(row=4, column=0, sticky="W")
        
        Label(frame, text="Stage(XY)", width=20).grid(row=5, column=0, sticky="W")
        
        e_negative_angle = Spinbox(frame, width=10, textvariable=self.var_negative_angle, from_=-90, to=90, increment=5)
        e_negative_angle.grid(row=1, column=1, sticky="EW")
        e_neutral_angle = Spinbox(frame, width=10, textvariable=self.var_neutral_angle, from_=-90, to=90,  increment=5)
        e_neutral_angle.grid(row=2, column=1, sticky="EW")
        e_positive_angle = Spinbox(frame, width=10, textvariable=self.var_positive_angle, from_=-90, to=90,  increment=5)
        e_positive_angle.grid(row=3, column=1, sticky="EW")
        
        e_alpha_wobbler = Spinbox(frame, width=10, textvariable=self.var_alpha_wobbler, from_=-90, to=90,  increment=1)
        e_alpha_wobbler.grid(row=4, column=1, sticky="EW")
        self.b_start_wobble = Button(frame, text="Start", command=self.start_alpha_wobbler)
        self.b_start_wobble.grid(row=4, column=2, sticky="W")
        self.b_stop_wobble = Button(frame, text="Stop", command=self.stop_alpha_wobbler, state=DISABLED)
        self.b_stop_wobble.grid(row=4, column=3, sticky="W")

        e_stage_x = Entry(frame, width=10, textvariable=self.var_stage_x)
        e_stage_x.grid(row=5, column=1, sticky="EW")
        e_stage_y = Entry(frame, width=10, textvariable=self.var_stage_y)
        e_stage_y.grid(row=5, column=2, sticky="EW")

        b_negative_angle = Button(frame, text="Set", command=self.set_negative_angle)
        b_negative_angle.grid(row=1, column=2, sticky="W")
        b_neutral_angle = Button(frame, text="Set", command=self.set_neutral_angle)
        b_neutral_angle.grid(row=2, column=2, sticky="W")
        b_positive_angle = Button(frame, text="Set", command=self.set_positive_angle)
        b_positive_angle.grid(row=3, column=2, sticky="W")
        b_stage = Button(frame, text="Set", command=self.set_stage)
        b_stage.grid(row=5, column=3, sticky="W")
        b_stage_get = Button(frame, text="Get", command=self.get_stage)
        b_stage_get.grid(row=5, column=4, sticky="W")

        # frame.grid_columnconfigure(1, weight=1)
        frame.pack(side="top", fill="x", padx=10, pady=10)

        frame = Frame(self)
        
        Label(frame, text="Brightness", width=20).grid(row=11, column=0, sticky="W")
        e_brightness = Entry(frame, width=10, textvariable=self.var_brightness)
        e_brightness.grid(row=11, column=1, sticky="W")

        b_brightness = Button(frame, text="Set", command=self.set_brightness)
        b_brightness.grid(row=11, column=2, sticky="W")

        b_brightness_get = Button(frame, text="Get", command=self.get_brightness)
        b_brightness_get.grid(row=11, column=3, sticky="W")

        slider = Scale(frame, variable=self.var_brightness, from_=0, to=2**16-1, orient=HORIZONTAL, command=self.set_brightness)
        slider.grid(row=12, column=0, columnspan=3, sticky="EW")

        frame.pack(side="top", fill="x", padx=10, pady=10)

        frame = Frame(self)
        
        Label(frame, text="DiffFocus", width=20).grid(row=11, column=0, sticky="W")
        e_difffocus = Entry(frame, width=10, textvariable=self.var_difffocus)
        e_difffocus.grid(row=11, column=1, sticky="W")

        b_difffocus = Button(frame, text="Set", command=self.set_difffocus)
        b_difffocus.grid(row=11, column=2, sticky="W")

        b_difffocus_get = Button(frame, text="Get", command=self.get_difffocus)
        b_difffocus_get.grid(row=11, column=3, sticky="W")

        slider = Scale(frame, variable=self.var_difffocus, from_=0, to=2**16-1, orient=HORIZONTAL, command=self.set_difffocus)
        slider.grid(row=12, column=0, columnspan=3, sticky="EW")

        frame.pack(side="top", fill="x", padx=10, pady=10)


        from instamatic import TEMController
        self.ctrl = TEMController.get_instance()

    def init_vars(self):
        self.var_negative_angle = DoubleVar(value=-40)
        self.var_neutral_angle = DoubleVar(value=0)
        self.var_positive_angle = DoubleVar(value=40)

        self.var_mode = StringVar(value="diff")

        self.var_alpha_wobbler = DoubleVar(value=5)

        self.var_stage_x = IntVar(value=0)
        self.var_stage_y = IntVar(value=0)
        
        self.var_brightness = IntVar(value=65535)
        self.var_difffocus = IntVar(value=65535)

        self.var_stage_wait = BooleanVar(value=True)

    def set_trigger(self, trigger=None, q=None):
        self.triggerEvent = trigger
        self.q = q

    def set_mode(self, event=None):
        self.ctrl.mode = self.var_mode.get()

    def set_brightness(self, event=None):
        self.var_brightness.set((self.var_brightness.get()))
        self.q.put(("ctrl", { "task": "brightness.set", 
                              "value": self.var_brightness.get() } ))
        self.triggerEvent.set()

    def get_brightness(self, event=None):
        self.var_brightness.set(self.ctrl.brightness.get())

    def set_difffocus(self, event=None):
        self.var_difffocus.set((self.var_difffocus.get()))
        self.q.put(("ctrl", { "task": "difffocus.set", 
                              "value": self.var_difffocus.get() } ))
        self.triggerEvent.set()

    def get_difffocus(self, event=None):
        self.var_difffocus.set(self.ctrl.difffocus.get())

    def set_negative_angle(self):
        self.q.put(("ctrl", { "task": "stage.set", 
                              "a": self.var_negative_angle.get(),
                              "wait": self.var_stage_wait.get()  } ))
        self.triggerEvent.set()

    def set_neutral_angle(self):
        self.q.put(("ctrl", { "task": "stage.set", 
                              "a": self.var_neutral_angle.get(),
                              "wait": self.var_stage_wait.get()  } ))
        self.triggerEvent.set()

    def set_positive_angle(self):
        self.q.put(("ctrl", { "task": "stage.set", 
                              "a": self.var_positive_angle.get(),
                              "wait": self.var_stage_wait.get()  } ))
        self.triggerEvent.set()

    def set_stage(self):
        self.q.put(("ctrl", { "task": "stage.set", 
                              "x": self.var_stage_x.get(),
                              "y": self.var_stage_y.get(),
                              "wait": self.var_stage_wait.get() } ))
        self.triggerEvent.set()

    def get_stage(self, event=None):
        x, y, _, _, _ = self.ctrl.stage.get()
        self.var_stage_x.set(int(x))
        self.var_stage_y.set(int(y))

    def start_alpha_wobbler(self):
        self.wobble_stop_event = threading.Event()

        self.b_stop_wobble.config(state=NORMAL)
        self.b_start_wobble.config(state=DISABLED)

        self.q.put(("ctrl", { "task": "stage.alpha_wobbler",
                              "delta": self.var_alpha_wobbler.get(),
                              "event": self.wobble_stop_event } ))
        self.triggerEvent.set()

    def stop_alpha_wobbler(self):
        self.wobble_stop_event.set()

        self.b_stop_wobble.config(state=DISABLED)
        self.b_start_wobble.config(state=NORMAL)

    def stage_stop(self):
        self.q.put(("ctrl", { "task": "stage.stop" } ))
        self.triggerEvent.set()

    def find_eucentric_height(self):
        self.q.put(("ctrl", { "task": "find_eucentric_height" } ))
        self.triggerEvent.set()


def microscope_control(controller, **kwargs):
    from operator import attrgetter

    task = kwargs.pop("task")

    f = attrgetter(task)(controller.ctrl)  # nested getattr
    f(**kwargs)


from .base_module import BaseModule
module = BaseModule("ctrl", "control", True, ExperimentalCtrl, commands={
    "ctrl": microscope_control
    })


if __name__ == '__main__':
    root = Tk()
    ExperimentalCtrl(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

