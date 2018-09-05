import os
import boto3
import time
import json

def handler(event,context):
    print(event)
    return 'Hello world'

def handlerChecker(event,context):
    print(event)
    while (True):
        clientSF = boto3.client('stepfunctions')
        responseSF = clientSF.get_activity_task(
            activityArn=os.environ['activityName'],
            workerName='Lambda'
        )
        print(responseSF)
        clientLambda = boto3.client('lambda')
        responseLambda = clientLambda.invoke_async(
            FunctionName=os.environ['executorName'],
            InvokeArgs=json.dumps({"taskToken": responseSF['taskToken'],"input": responseSF['input']})
        )
        print(responseLambda)
    return 'Hello world'

def handlerProc(event,context):
    print(event)
    time.sleep(1)
    clientSF = boto3.client('stepfunctions')
    responseSF = clientSF.send_task_success(
        taskToken=event['taskToken'],
        output=event['input'] + ' Step function'
    )
    return event['Input'] + ' Step function'