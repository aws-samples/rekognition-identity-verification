from enum import Enum
from typing import List

class BatchJob:
  '''
  Represents the Amazon S3 Batch Job metadata.
  '''
  def __init__(self, props:dict) -> None:
    self.id:str = props['id']

class BatchTask:
  '''
  Represents an individual task within the BatchRequest message.
  '''
  def __init__(self, props:dict) -> None:
    self.taskId:str = props['taskId']
    self.s3Key:str = props['s3Key']
    self.s3BucketArn:str = props['s3BucketArn']
    self.s3VersionId:str = props['s3VersionId']

  @property
  def object_arn(self)->str:
    '''
    Gets the S3 objects fully qualified Amazon Resource Name. 
    '''
    return '{}/{}'.format(self.s3BucketArn, self.s3Key)

  @property
  def bucket_name(self)->str:
    '''
    Gets the name of the bucket holding the object.
    '''
    if self.s3BucketArn.startswith('arn'):
      return self.s3BucketArn.split(':')[-1]
    else:
      return self.s3BucketArn

class TaskResultCode(Enum):
  '''
  Represents the completion flag of a BatchTask.
  '''
  SUCCEEDED='Succeeded'
  TEMPORARY_FAILURE='TemporaryFailure'
  PERMANENT_FAILURE='PermanentFailure'

class BatchTaskResult:
  '''
  Represents the result of an individual BatchTask
  '''
  def __init__(self, taskId:str, resultCode:TaskResultCode, resultString:str='') -> None:
    self.taskId:str = taskId
    self.resultCode = resultCode
    self.resultString  = resultString

  def to_dict(self)->dict:
    return {
      'taskId': self.taskId,
      'resultCode': self.resultCode.value,
      'resultString': self.resultString,
    }

class BatchResponse:
  '''
  Represents the response to the storage operation.
  '''
  def __init__(self, invocationId:str) -> None:
    self.__invocationId:str = invocationId
    self.__results:List[BatchTaskResult] = []

  @property
  def invocationId(self)->str:
    return self.__invocationId

  @property
  def results(self)->List[BatchTaskResult]:
    return self.__results

  def to_dict(self)->dict:
    return {
      'invocationSchemaVersion': '1.0',
      'treatMissingKeysAs': 'PermanentFailure',
      'invocationId': self.invocationId,
      'results': [result.to_dict() for result in self.results ]
    }

class BatchRequest:
  '''
  Represents an incoming event from Amazon S3 Batch.
  '''
  def __init__(self, event:dict) -> None:
    self.invocationId = event['invocationId']
    self.job = BatchJob(event['job'])
    self.tasks = [BatchTask(task) for task in event['tasks']]

class UserRegistrationInfo:
  '''
  Represents the user registration metadata.
  '''
  def __init__(self) -> None:
    self.user_id = None
    self.properties = {}

  @property
  def user_id(self)->str:
    return self.__user_id

  @property
  def properties(self)->dict:
    return self.__properties

  @property
  def is_valid(self)->bool:
    return self.user_id is not None

  @user_id.setter
  def user_id(self,value:str)->None:
    self.__user_id = value

  @properties.setter
  def properties(self,value:dict)->None:
    self.__properties = value

  def to_dict(self)->dict:
    return {
      "UserId": self.user_id,
      "Properties": self.properties
    }

class IRegistrationDataProvider:
  '''
  Represents an interface for querying user registration data.
  '''
  def get_registration_date(self, task:BatchTask)->UserRegistrationInfo:
    raise NotImplementedError()
