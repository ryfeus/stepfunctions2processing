# stepfunctions2processing
Configuration with AWS step functions and lambdas which initiates processing from activity state

## Motivation

Currently AWS Step Function service provides the best way to unite together serverless processing and cluster processing. Serverless processing can be extremely useful for the cases when you need to have a very good scalability or cheap processing. But for the long or CPU heavy processing you may still need to use cluster. The current version of step function expects cluster (except for ECS and Batch) to make requests to the Step Function activity. For clusters with extremely expensive machines it may not be the best way for handling so this project allows to transform activity state into active processing trigger. Examples here also include AWS Batch and AWS Fargate

**TL;DR**: Project allows to initiate processing from AWS Step function instead of making state requests towards it.

## Examples

### AWS Lambda example

#### Scheme

![Image](https://s3.amazonaws.com/ryfeus-blog/images/stepFunction.png)


1. Step function process starts and input data is provided to lambda
2. Lambda processes data and produces json output which is then given to the activity.
3. Checker lambda makes regular requests to the activity in case activity is in "ActivityScheduled" state.
4. Activty returns token and input json.
5. Checker lambda initiates processing lambda which takes token and input json as input.
6. Processing lambda conducts processing part and return token and output json to activity.
7. Step functions provides output json from the activity as output


### AWS Fargate example

#### How to deploy

1. Push docker image into ECR (https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html)
2. Update serverless.yml with image name and instance parameters
3. Install and configure serverless (https://serverless.com/framework/docs/providers/aws/guide/installation/)
4. Install plugins serverless-step-functions and serverless-pseudo-parameters
5. Run ```serverless deploy```

#### Scheme

![Image](https://s3.amazonaws.com/ryfeus-blog/images/FargateScheme.png)

### AWS Batch example

#### How to deploy

1. Push docker image into ECR (https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html)
2. Update serverless.yml with image name and instance parameters
3. Install and configure serverless (https://serverless.com/framework/docs/providers/aws/guide/installation/)
4. Install plugins serverless-step-functions and serverless-pseudo-parameters
5. Run ```serverless deploy```

#### Scheme

![Image](https://s3.amazonaws.com/ryfeus-blog/images/BatchScheme.png)

## Tools

Project utilises serverless framework with plugin for step functions for orchestration and deployment of the application.

## References

- https://github.com/nathanpeck/aws-cloudformation-fargate
- https://gist.github.com/lizrice/5889f33511aab739d873cb622688317e

## Next steps

- [x] Add AWS Batch processing example
- [x] Add AWS Fargate processing example
- Create example for deep learning/machine learning training processes
