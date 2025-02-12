from instamatic import config

default_tem = config.microscope.name

__all__ = ["Microscope"]


def get_tem(name: str):
    """Grab tem class"""

    if config.cfg.tem_require_admin:
        from instamatic import admin
        if not admin.is_admin():
            raise PermissionError("Access to the TEM interface requires admin rights.")

    if name == "jeol":
        from .jeol_microscope import JeolMicroscope as cls
    elif name == "fei":
        from .fei_microscope import FEIMicroscope as cls
    elif name == "fei_simu":
        from .fei_simu_microscope import FEISimuMicroscope as cls
    elif name == "simulate":
        from .simu_microscope import SimuMicroscope as cls
    else:
        raise ValueError(f"No such microscope: `{name}`")

    return cls


def Microscope(name: str=None, use_server: bool=False):
    """Generic class to load microscope interface class

    name: str
        Specify which microscope to use, must be one of `jeol`, `fei_simu`, `simulate`
    use_server: bool
        Connect to microscope server running on the host/port defined in the config file

    returns: TEM interface class
    """
    if name == None:
        name = default_tem
    elif name != config.cfg.microscope:
        config.load(microscope_name=name)
        name = config.cfg.microscope

    if use_server:
        from .microscope_client import MicroscopeClient
        tem = MicroscopeClient(name)
    else:
        cls = get_tem(name)
        tem = cls()

    return tem
