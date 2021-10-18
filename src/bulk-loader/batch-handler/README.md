# Bulk Loader Batch Handler

Amazon S3 Batch enumerates the Amazon S3 Inventory and calls this function once per S3 object.

This function will read the specified image file (e.g., **foo.png** or **bar.jpeg**) and determine if it qualifies for processing.

Images that qualify require additional metadata, which the [IRegistrationDataProvider](lib/models.py) must extract.  This information can come from RDS or some other external system.  The [S3TagUserRegistrationInfo](lib/registrationproviders.py) is an example that uses Amazon S3 Object Tags.  Most likely, customers will need to implement their own class to describe their specific business rules.

## What is the IRegistrationDataProvider

This interface receives a reference to the current Amazon S3 Batch Task, and must return the UserRegistrationInfo.  The **task** contains properties for determining the image's location (e.g., `s3://bucket/path/to/file.jpeg`).

Presently, the **UserRegistrationInfo.user_id** property is the only required value.  It is recommended that customers include additional metadata in the **properties** dictionary.

```python
class IRegistrationDataProvider:
  '''
  Represents an interface for querying user registration data.
  '''
  def get_registration_date(self, task:BatchTask)->UserRegistrationInfo:
    raise NotImplementedError()

class MyCustomProvider(IRegistrationDataProvider):
  ... omitted ...
  
  def get_registration_date(self, task:BatchTask)->UserRegistrationInfo:
    info = UserRegistrationInfo()
    info.user_id = get_userid_from_task(task)
    info.properties = get_properties_from_rds(user_id)
    return info

  ... omitted ...
```

## How do I use MyCustomProvider

In **handler.py** specify the configuration toward the top of the file.

```python
'''
Important: Configure your registration source here 
'''
#registration_data_provider = S3TagUserRegistrationInfo(region_name=environ.get('REGION'))
registration_data_provider = MyCustomProvider(region_name=environ.get('REGION'))
```
