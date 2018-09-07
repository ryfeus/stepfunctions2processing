# stepfunctions2processing
Configuration with AWS step functions and lambdas which initiates processing from activity state

## Motivation

Currently AWS Step Function service provides the best way to unite together serverless processing and cluster processing. Serverless processing can be extremely useful for the cases when you need to have a very good scalability or cheap processing. But for the long or CPU heavy processing you may still need to use cluster. The current version of step function expects cluster to make requests to the Step Function activity. For clusters with extremely expensive machines it may not be the best way for handling so this project allows to transform activity state into active processing trigger. This could be extremely convenient to use with AWS Batch or AWS Fargate.

**TL;DR**: Project allows to initiate processing from AWS Step function instead of making state requests towards it.

## Scheme

![Image](https://s3.amazonaws.com/ryfeus-blog/images/stepFunction.png)


1. Step function process starts and input data is provided to lambda
2. Lambda processes data and produces json output which is then given to the activity.
3. Checker lambda makes regular requests to the activity in case activity is in "ActivityScheduled" state.
4. Activty returns token and input json.
5. Checker lambda initiates processing lambda which takes token and input json as input.
6. Processing lambda conducts processing part and return token and output json to activity.
7. Step functions provides output json from the activity as output

## Tools

Project utilises serverless framework with plugin for step functions for orchestration and deployment of the application.

## Next steps

- Add AWS Batch processing example
- Add AWS Fargate processing example
- Create example for deep learning/machine learning training processes
