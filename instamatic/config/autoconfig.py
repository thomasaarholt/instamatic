from instamatic.tools import relativistic_wavelength
import yaml
from instamatic import config
from pathlib import Path
import shutil

def list_representer(dumper, data):
    """For cleaner printing of lists in yaml files"""
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)


yaml.representer.Representer.add_representer(list, list_representer)


def get_tvips_calibs(ctrl, rng: list, mode: str, wavelength: float) -> dict:
    """Loop over magnification ranges and return calibrations from EMMENU"""

    if mode == "diff":
        print("Warning: Pixelsize can be a factor 10 off in diff mode (bug in EMMENU)")

    calib_range = {}

    BinX, BinY = ctrl.cam.getBinning()
    assert BinX == BinY, "Binnings differ in X and Y direction?! (X: {BinX} | Y: {BinY})"

    ctrl.mode(mode)

    for mag in rng:
        ctrl.magnification.set(mag)
        d = ctrl.cam.getCurrentCameraInfo()

        PixelSizeX = d["PixelSizeX"]
        PixelSizeY = d["PixelSizeY"]
        assert PixelSizeX == PixelSizeY, "Pixelsizes differ in X and Y direction?! (X: {PixelSizeX} | Y: {PixelSizeY})"

        if mode == "diff":
            pixelsize = np.sin(PixelSizeX / 1_000_000) / wavelength  #  µrad/px -> rad/px -> px/Å
        else:
            pixelsize = PixelSizeX

        calib_range[mode] = pixelsize

    return calib_range


def choice_prompt(choices: list=[], default=None, question: str="Which one?"):
    """Simple cli to prompt for a list of choices"""
    print()
    choices = "jeol fei simulate".split()

    if default:
        default_choice = choices.index(default)
        suffix = f" [{default}]"
    else:
        suffix = ""

    for i, choice in enumerate(choices):
        print(f"{i+1: 2d}: {choice}")

    q = input(f"\nWhich microscope can I connect to?{suffix} >> ")
    if not q:
        picked = default_choice
    else:
        q = int(q) - 1
        picked = choices[q]

    return picked


def main():
    """
    This tool will help to set up the configuration files for `instamatic`
    It establishes a connection to the microscope and reads out the camera lengths
    and magnification ranges
    """

    ### Connect to microscope

    tem_name = choice_prompt(choices="jeol fei simulate".split(),
                             default="simulate",
                             question="Which microscope can I connect to?")

    ### Connect to camera

    cam_name = choice_prompt(choices="None gatan tvips simulate".split(),
                             default="simulate",
                             question="Which camera can I connect to?")

    ## Fetch camera config

    drc = Path(__file__).parent
    choices = list(drc.glob("camera/*.yaml"))
    choices.append(None)

    cam_config = choice_prompt(choices=choices,
                               default=None,
                               question="Which camera type do you want to use (select closest one and modify if needed)?")

    ### Instantiate microscope / camera connection

    from instamatic.TEMController.microscope import get_tem
    from instamatic.camera.camera import get_cam
    from instamatic.TEMController.TEMController import TEMController

    cam = get_cam(cam_name)() if cam_name else None
    tem = get_tem(tem_name)()

    ctrl = TEMController(tem=tem, cam=cam)
    ranges = ctrl.magnification.get_ranges()

    ht = ctrl.high_tension  # in V

    wavelength = relativistic_wavelength(ht)

    tem_config = {}
    tem_config["name"] = tem_name
    tem_config["wavelength"] = wavelength

    for mode, rng in ranges.items():
        tem_config["range_"+mode] = rng

    calib_config = {}
    calib_config["name"] = tem_name

    ### Find magnification ranges

    for mode, rng in ranges.items():
        if cam_name == "tvips":
            pixelsizes = get_tvips_calibs(ctrl=ctrl, rng=rng, mode=mode, wavelength=wavelength)
        else:
            pixelsizes = {r: 1.0 for r in rng}
        calib_config["pixelsize_"+mode] = pixelsizes

        stagematrices = {r: [1, 0, 0, 1] for r in rng}

        calib_config["stagematrix_"+mode] = stagematrices

    ### Write/copy configs

    tem_config_fn = f"{tem_name}_tem.yaml"
    calib_config_fn = f"{tem_name}_calib.yaml"
    if cam_config:
        cam_config_fn = f"{cam_name}_cam.yaml"
        shutil.copyfile(cam_config, cam_config_fn)

    yaml.dump(tem_config, open(tem_config_fn, "w"), sort_keys=False)
    yaml.dump(calib_config, open(calib_config_fn, "w"), sort_keys=False)
    
    print()
    print(f"Wrote files config files:")
    print(f"    Copy {tem_config_fn} -> `{config.config_drc / tem_config_fn}`")
    print(f"    Copy {calib_config_fn} -> `{config.config_drc / calib_config_fn}`")
    if cam_config:
        print(f"    Copy {cam_config_fn} -> `{config.config_drc / cam_config_fn}`")
    print()
    print(f"In `{config.config_drc / 'global.yaml'}`:")
    print(f"    microscope: {tem_name}_tem")
    print(f"    calibration: {tem_name}_calib")
    if cam_config:
        print(f"    camera: {cam_name}_cam")
    print()
    print(f"Todo: Check and update the pixelsizes in `{calib_config_fn}`")
    print( "    In real space, pixelsize in nm")
    print( "    In reciprocal space, pixelsize in px/Angstrom")


if __name__ == '__main__':
    main()
