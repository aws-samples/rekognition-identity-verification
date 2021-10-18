import boto3


class TransientError(Exception):
  '''
  Represents a retryable error.
  '''
  pass

class NonRecoverableError(Exception):
  '''
  Represents a hard failure from DynamoDB.
  '''
  pass

class ExceptionUtil:
  
  @staticmethod
  def normalize_for_step_functions(ddb_client:boto3.client, error:Exception)->Exception:
    '''
    Creates a generic error to return to the StepFunction caller.
      This approach simplifies the state machine's retry policy.
    '''
    hard_failures = [
      ddb_client.exceptions.ConditionalCheckFailedException,
      ddb_client.exceptions.ResourceNotFoundException,
      ddb_client.exceptions.ItemCollectionSizeLimitExceededException,
    ]

    retryable = [
      ddb_client.exceptions.ProvisionedThroughputExceededException,
      ddb_client.exceptions.TransactionConflictException,
      ddb_client.exceptions.RequestLimitExceeded,
      ddb_client.exceptions.InternalServerError,
    ]

    if error in hard_failures:
      return NonRecoverableError(error.__class__.__name__)
    elif error in retryable:
      return TransientError(error.__class__.__name__)
    else:
      return error
