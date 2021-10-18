
class NoFacesDetectedException(Exception):
  '''
  Represents a failure due to no faces detected.
  '''
  pass

class TooManyFacesDetectedException(Exception):
  '''
  Represents a failure due to too many faces detected.
  '''
  pass

class InvalidPoseDetectedException(Exception):
  '''
  Represents a failure due to the user wearing sunglasses.
  '''
  pass

class SunglassesDetectedException(Exception):
  '''
  Represents a failure due to the user wearing sunglasses.
  '''
  pass