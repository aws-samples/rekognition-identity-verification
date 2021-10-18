class InvalidImageUriException(Exception):
  '''
  Represents a failure due to unexpected s3_uri format.
  '''
  pass

class InvalidImageExtensionException(Exception):
  '''
  Represents a failure due to the file suffix being unsupported type.
  '''
  pass