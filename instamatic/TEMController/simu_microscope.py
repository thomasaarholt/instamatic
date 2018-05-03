from instamatic import config

NTRLMAPPING = {
   "GUN1" : 0,
   "GUN2" : 1,
   "CLA1" : 2,
   "CLA2" : 3,
   "SHIFT" : 4,
   "TILT" : 5,
   "ANGLE" : 6,
   "CLS" : 7,
   "IS1" : 8,
   "IS2" : 9,
   "SPOT?" : 10,
   "PLA" : 11,
   "OLS" : 12,
   "ILS" : 13
}

FUNCTION_MODES = ('mag1', 'mag2', 'lowmag', 'samag', 'diff')

# constants for Jeol Hex value
ZERO = 32768
MAX = 65535
MIN = 0


class SimuMicroscope(object):
    """docstring for microscope"""
    def __init__(self, name="simulate"):
        super(SimuMicroscope, self).__init__()
        import random
        
        self.Brightness_value = random.randint(MIN, MAX)

        self.GunShift_x = random.randint(MIN, MAX)
        self.GunShift_y = random.randint(MIN, MAX)

        self.GunTilt_x = random.randint(MIN, MAX)
        self.GunTilt_y = random.randint(MIN, MAX)

        self.BeamShift_x = random.randint(MIN, MAX)
        self.BeamShift_y = random.randint(MIN, MAX)

        self.BeamTilt_x = random.randint(MIN, MAX)
        self.BeamTilt_y = random.randint(MIN, MAX)

        self.ImageShift1_x = random.randint(MIN, MAX)
        self.ImageShift1_y = random.randint(MIN, MAX)
        
        self.ImageShift2_x = random.randint(MIN, MAX)
        self.ImageShift2_y = random.randint(MIN, MAX)

        self.StagePosition_x = random.randint(-100000, 100000)
        self.StagePosition_y = random.randint(-100000, 100000)
        self.StagePosition_z = random.randint(-10000,  10000)
        self.StagePosition_a = random.randint(-40, 40)
        self.StagePosition_b = random.randint(-40, 40)

        # self.FunctionMode_value = random.randint(0, 2)
        self.FunctionMode_value = 0

        self.DiffractionFocus_value = random.randint(MIN, MAX)

        self.DiffractionShift_x = random.randint(MIN, MAX)
        self.DiffractionShift_y = random.randint(MIN, MAX)

        self.name = name
        self.MAGNIFICATIONS      = config.microscope.specifications["MAGNIFICATIONS"]
        self.MAGNIFICATION_MODES = config.microscope.specifications["MAGNIFICATION_MODES"]
        self.CAMERALENGTHS       = config.microscope.specifications["CAMERALENGTHS"]

        self.FUNCTION_MODES = FUNCTION_MODES
        self.NTRLMAPPING = NTRLMAPPING

        self.ZERO = ZERO
        self.MAX = MAX
        self.MIN = MIN

        # self.Magnification_value = random.choice(self.MAGNIFICATIONS)
        self.Magnification_value = 2500
        self.Magnification_value_diff = 300

        self.beamblank = False

        self.condensorlensstigmator_x = random.randint(MIN, MAX)
        self.condensorlensstigmator_y = random.randint(MIN, MAX)

        self.intermediatelensstigmator_x = random.randint(MIN, MAX)
        self.intermediatelensstigmator_y = random.randint(MIN, MAX)

        self.objectivelensstigmator_x = random.randint(MIN, MAX)
        self.objectivelensstigmator_y = random.randint(MIN, MAX)

        self.spotsize = 1

        self.screenposition_value = 'up'

        self.condensorlens1_value = random.randint(MIN, MAX)
        self.condensorlens2_value = random.randint(MIN, MAX)
        self.condensorminilens_value = random.randint(MIN, MAX)
        self.objectivelensecoarse_value = random.randint(MIN, MAX)
        self.objectivelensefine_value = random.randint(MIN, MAX)
        self.objectiveminilens_value = random.randint(MIN, MAX)

    def load_specifications(self):
        config.load_microscope(self.name)

        self.MAGNIFICATIONS      = config.CFG.microscope.specifications["MAGNIFICATIONS"]
        self.MAGNIFICATION_MODES = config.CFG.microscope.specifications["MAGNIFICATION_MODES"]
        self.CAMERALENGTHS       = config.CFG.microscope.specifications["CAMERALENGTHS"]

    def getBrightness(self):
        return self.Brightness_value

    def setBrightness(self, value):
        self.Brightness_value = value

    def getMagnification(self):
        if self.getFunctionMode() == "diff":
            return self.Magnification_value_diff
        else:
            return self.Magnification_value

    def setMagnification(self, value):
        if value not in self.MAGNIFICATIONS:
            value = min(self.MAGNIFICATIONS, key=lambda x: abs(x-value))
        
        # get best mode for magnification
        for k in sorted(self.MAGNIFICATION_MODES.keys(), key=self.MAGNIFICATION_MODES.get): # sort by values
            v = self.MAGNIFICATION_MODES[k]
            if v <= value:
                new_mode = k

        current_mode = self.getFunctionMode()
        if current_mode != new_mode:
            self.setFunctionMode(new_mode)

        # calculate index
        ## i = 0-24 for lowmag
        ## i = 0-29 for mag1
        selector = self.MAGNIFICATIONS.index(value) - self.MAGNIFICATIONS.index(self.MAGNIFICATION_MODES[new_mode])
                
        if self.getFunctionMode() == "diff":
            self.Magnification_value_diff = value
        else:
            self.Magnification_value = value

    def getMagnificationIndex(self):
        value = self.getMagnification()
        return self.MAGNIFICATIONS.index(value)

    def setMagnificationIndex(self, index):
        value = self.MAGNIFICATIONS[index]
        self.setMagnification(value)

    def getGunShift(self):
        return self.GunShift_x, self.GunShift_y

    def setGunShift(self, x, y):
        self.GunShift_x = x
        self.GunShift_y = y
    
    def getGunTilt(self):
        return self.GunTilt_x, self.GunTilt_y 
    
    def setGunTilt(self, x, y):
        self.GunTilt_x = x
        self.GunTilt_y = y

    def getBeamShift(self):
        return self.BeamShift_x, self.BeamShift_y

    def setBeamShift(self, x, y):
        self.BeamShift_x = x
        self.BeamShift_y = y

    def getBeamTilt(self):
        return self.BeamTilt_x, self.BeamTilt_y
    
    def setBeamTilt(self, x, y):
        self.BeamTilt_x = x
        self.BeamTilt_y = y

    def getImageShift1(self):
        return self.ImageShift1_x, self.ImageShift1_y

    def setImageShift1(self, x, y):
        self.ImageShift1_x = x
        self.ImageShift1_y = y

    def getImageShift2(self):
        return self.ImageShift2_x, self.ImageShift2_y

    def setImageShift1(self, x, y):
        self.ImageShift1_x = x
        self.ImageShift1_y = y
        
    def getImageShift2(self):
        return self.ImageShift2_x, self.ImageShift2_y

    def setImageShift2(self, x, y):
        self.ImageShift2_x = x
        self.ImageShift2_y = y

    def getStagePosition(self):
        return self.StagePosition_x, self.StagePosition_y, self.StagePosition_z, self.StagePosition_a, self.StagePosition_b

    def isStageMoving(self):
        return False

    def waitForStage(self, delay=0.1):
        while self.isStageMoving():
            time.sleep(delay)

    def setStageX(self, value, wait=True):
        self.StagePosition_x = value
        if True:
            self.waitForStage()

    def setStageY(self, value, wait=True):
        self.StagePosition_y = value
        if True:
            self.waitForStage()

    def setStageZ(self, value, wait=True):
        self.StagePosition_z = value
        if True:
            self.waitForStage()

    def setStageA(self, value, wait=True):
        self.StagePosition_a = value
        if True:
            self.waitForStage()

    def setStageB(self, value, wait=True):
        self.StagePosition_b = value
        if True:
            self.waitForStage()

    def setStageXY(self, x, y, wait=True):
        self.StagePosition_x = x
        self.StagePosition_y = y
        if wait:
            self.waitForStage()

    def stopStage(self):
        pass

    def setStagePosition(self, x=None, y=None, z=None, a=None, b=None, wait=True):
        if z is not None:
            self.setStageZ(z, wait=wait)
        if a is not None:
            self.setStageA(a, wait=wait)
        if b is not None:
            self.setStageB(b, wait=wait)

        if (x is not None) and (y is not None):
            self.setStageXY(x=x, y=y, wait=wait)
        else:
            if x is not None:
                self.setStageX(x, wait=wait)     
            if y is not None:
                self.setStageY(y, wait=wait)

    def getFunctionMode(self):
        """mag1, mag2, lowmag, samag, diff"""
        mode = self.FunctionMode_value
        return FUNCTION_MODES[mode]

    def setFunctionMode(self, value):
        """mag1, mag2, lowmag, samag, diff"""
        if isinstance(value, str):
            try:
                value = FUNCTION_MODES.index(value)
            except ValueError:
                raise ValueError("Unrecognized function mode: {}".format(value))
        self.FunctionMode_value = value

    def getDiffFocus(self):
        if not self.getFunctionMode() == "diff":
            raise ValueError("Must be in 'diff' mode to get DiffFocus")
        return self.DiffractionFocus_value

    def setDiffFocus(self, value):
        """IL1"""
        if not self.getFunctionMode() == "diff":
            raise ValueError("Must be in 'diff' mode to set DiffFocus")
        self.DiffractionFocus_value = value

    def getDiffShift(self):
        return self.DiffractionShift_x, self.DiffractionShift_y

    def setDiffShift(self, x, y):
        self.DiffractionShift_x = x
        self.DiffractionShift_y = y

    def releaseConnection(self):
        print("Connection to microscope released")

    def isBeamBlanked(self, value):
        return self.beamblank

    def setBeamBlank(self, mode):
        """True/False or 1/0"""
        self.beamblank = mode

    def getCondensorLensStigmator(self):
        return self.condensorlensstigmator_x, self.condensorlensstigmator_y

    def setCondensorLensStigmator(self, x, y):
        self.condensorlensstigmator_x = x
        self.condensorlensstigmator_y = y
        
    def getIntermediateLensStigmator(self):
        return self.intermediatelensstigmator_x, self.intermediatelensstigmator_y

    def setIntermediateLensStigmator(self, x, y):
        self.intermediatelensstigmator_x = x
        self.intermediatelensstigmator_y = y

    def getObjectiveLensStigmator(self):
        return self.objectivelensstigmator_x, self.objectivelensstigmatir_y

    def setObjectiveLensStigmator(self, x, y):
        self.objectivelensstigmator_x = x
        self.objectivelensstigmator_y = y

    def getSpotSize(self):
        """0-based indexing for GetSpotSize, add 1 for consistency"""
        return self.spotsize

    def getScreenPosition(self):
        return self.screenposition_value

    def setScreenPosition(self, value):
        """value = 'up' or 'down'"""
        self.screenposition_value = value

    def setSpotSize(self, value):
        self.spotsize = value

    def getCondensorLens1(self):
        return self.condensorlens1_value

    def getCondensorLens2(self):
        return self.condensorlens2_value

    def getCondensorMiniLens(self):
        return self.condensorminilens_value

    def getObjectiveLenseCoarse(self):
        return self.objectivelensecoarse_value

    def getObjectiveLenseFine(self):
        return self.objectivelensefine_value
    
    def getObjectiveMiniLens(self):
        return self.objectiveminilens_value
