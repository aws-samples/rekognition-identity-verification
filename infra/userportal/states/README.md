# UserPortal Step Functions

When users interact with the [UserPortal Gateway](../gateway.py), the request processing happens with Amazon Step Function Express.

Step Functions is a serverless orchestration service that lets you combine AWS Lambda functions and other AWS services to build business-critical applications. Through Step Functions' graphical console, you see your application's workflow as a series of event-driven steps. Step Functions is based on state machines and tasks.

## What input do the state machines expect

Each Step Function state machine initialize with the below example state document.  Callers can place arbitrary metadata in the **Properties** property bag.  The Image must be either **PNG** or **JPG** format, encoded as `utf8(base64(image_bytes))`.

```json
{
  "inputRequest": {
    "UserId": "string",
    "Image": "base64(bytes) with utf8 encoding",
    "Properties": {
      "Key1": "Value1",
      "Key2": "Value2"
    }
  }
}
```

## How do I use the state document

Any state other than a **Fail** state can include **InputPath**, **ResultPath**, or **OutputPath**. These allow you to use a path to filter the JSON as it moves through your workflow.

For [example](https://docs.aws.amazon.com/step-functions/latest/dg/input-output-example.html), start with the AWS Lambda function and state machine described in the Creating a Step Functions State Machine That Uses Lambda tutorial. Modify the state machine so that it includes the following **InputPath**, **ResultPath**, and **OutputPath**.

| Parameter| Usage | Example|
|----------|------|----------|
| InputPath | Select the task's input |  `$.inputRequest` |
| OutPath | Specify a subset of the task's output | `$.Payload.FaceDetails` |
| ResultPath | Specify where to persist the output | `$.myStepName` |
