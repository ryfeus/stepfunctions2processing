## Java Application with Amazon CodeGuru Profiler on AWS Batch

### Description

This is a demo Java application with Amazon CodeGuru Profiler on AWS Batch, wrapped by AWS Step Functions. You can use the same project settings to deploy your application and test it how it performs in the cloud and get recommendations.

### How to set up

#### Build and test Java application locally

You will need to have Java 8 and Maven installed. You will also need to have your AWS credentials set up locally (https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html). Also, you will need to set up profiling group “demoApplication” in CodeGuru dashboard (https://console.aws.amazon.com/codeguru/profiler/search).

```
cd aws-batch-with-profiler/docker
mvn clean compile assembly:single
java -jar target/demo-1.0.0-jar-with-dependencies.jar
```

#### Build and save docker container

You will need to replace accountId and regionId with your account id and region id.
```
cd aws-batch-with-profiler/docker
aws ecr get-login-password --region <regionId> | docker login --username AWS --password-stdin <accountId>.dkr.ecr.<regionId>.amazonaws.com
aws ecr create-repository --repository-name test-java-app-with-profiler
docker tag test-java-app-with-profiler:latest <accountId>.dkr.ecr.<regionId>.amazonaws.com/test-java-app-with-profiler:latest
docker push <accountId>.dkr.ecr.<regionId>.amazonaws.com/test-java-app-with-profiler:latest
```

#### Deploy AWS Batch and AWS Step functions and AWS Lambda

You will need to have node and npm installed.
```
cd aws-batch-with-profiler/aws-batch
npm install
serverless deploy
```

#### Invoke Step Function

You can use link from previous command to invoke AWS Step Functions.
```
curl https://<urlPrefix>.execute-api.<regionId>.amazonaws.com/dev/startFunction
```
