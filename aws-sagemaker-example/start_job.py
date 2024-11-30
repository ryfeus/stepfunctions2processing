import boto3
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.config import Config as BotocoreConfig
import math
from fire import Fire
import numpy as np

# Initialize Boto3 SageMaker client
sagemaker_client = boto3.client(
    "sagemaker",
    config=BotocoreConfig(
        connect_timeout=5, read_timeout=5, retries={"max_attempts": 10}
    ),
)
s3_output_path = "s3://<bucket_name>/"
ecr_name = "<ecr_name>"

datasets_prefixes = [
    "candle",
    "capsules",
    "cashew",
    "chewinggum",
    "fryum",
    "macaroni1",
    "macaroni2",
    "pcb1",
    "pcb2",
    "pcb3",
    "pcb4",
    "pipe_fryum",
]

hyperparameters = {
    "batch-size": "128", # Change to 256
    "epochs": "25", 
    "learning-rate": "0.0001"
}


def start_training_job_single(prefix: str = "pcb1", enable_spot: bool = False):
    """
    Run single training job.
    """
    job_name = f"anomaly-training-job-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    return start_training_job(
        job_name,
        hyperparameters=hyperparameters,
        prefix=prefix,
        enable_spot=enable_spot,
    )


def start_training_jobs_batch(total_jobs: int = 20, batch_size: int = 20, enable_spot: bool = True, suffix: str = ""):
    """
    Run batch of training jobs.
    """
    return start_batched_training_jobs(
        total_jobs, batch_size, base_hyperparameters=hyperparameters, enable_spot=enable_spot, suffix=suffix
    )


def list_and_aggregate_roc_auc(
    status_filter: str = "Completed", suffix: str = ""
):
    """
    List and aggregate ROC AUC across completed SageMaker training jobs.
    """
    name_contains = f"anomaly-training-job-batch-{suffix}"
    training_jobs = list_training_jobs(status_filter, name_contains)
    aggregate_roc_auc(training_jobs)


def start_training_job(
    job_name: str,
    hyperparameters: dict,
    prefix: str = "pcb1",
    enable_spot: bool = False,
):
    # Training job configuration
    stopping_condition = {
        "MaxRuntimeInSeconds": 86400,
    }
    if enable_spot:
        stopping_condition["MaxWaitTimeInSeconds"] = 86400

    training_job_params = {
        "TrainingJobName": job_name,
        "AlgorithmSpecification": {
            "TrainingImage": f"483826776245.dkr.ecr.us-west-2.amazonaws.com/vedmich-dev317-01:latest",
            "TrainingInputMode": "Pipe",
            "EnableSageMakerMetricsTimeSeries": True,
            "MetricDefinitions": [
                {
                    "Name": "ROC AUC",
                    "Regex": "ROC AUC: (.*)",
                },
                {
                    "Name": "Loss",
                    "Regex": "Loss: (.*)",
                },
            ],
        },
        "InputDataConfig": [
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"{s3_output_path}VisA_pytorch/1cls/{prefix}/",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "application/x-image",
                "InputMode": "File",
            },
        ],
        "OutputDataConfig": {"S3OutputPath": s3_output_path},
        "RoleArn": "arn:aws:iam::483826776245:role/service-role/AmazonSageMaker-ExecutionRole-20231108T173338",
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": "ml.p3.2xlarge",
            "VolumeSizeInGB": 30,
        },
        "StoppingCondition": stopping_condition,
        "HyperParameters": hyperparameters,
        "EnableManagedSpotTraining": enable_spot,
    }

    # Start training job
    response = sagemaker_client.create_training_job(**training_job_params)
    print(f"Training job starting: {response['TrainingJobArn']}")
    return response


def start_training_job_with_retries(job_name, hyperparameters):
    response = ""
    for try_num in range(4):
        try:
            response = start_training_job(job_name, hyperparameters)
            break
        except Exception as e:
            sleep_time = 1 + math.pow(2, try_num)
            logger.error(f"Caught exception {e}, sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)
    return response


def start_batched_training_jobs(total_jobs, batch_size, base_hyperparameters, enable_spot: bool = False, suffix: str=""):
    job_count = 0
    while job_count < total_jobs:
        # Calculate how many jobs to start in this batch
        jobs_in_this_batch = min(batch_size, total_jobs - job_count)

        # Use ThreadPoolExecutor to manage parallel job creation within this batch
        with ThreadPoolExecutor(max_workers=jobs_in_this_batch) as executor:
            futures = []
            for i in range(jobs_in_this_batch):
                job_name = f"anomaly-training-job-batch-{suffix}-{job_count + i}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
                hyperparameters = base_hyperparameters.copy()
                hyperparameters["job_specific_param"] = str(
                    job_count + i
                )  # Custom param for each job if needed
                prefix = datasets_prefixes[job_count % len(datasets_prefixes)]
                futures.append(
                    executor.submit(
                        start_training_job, job_name, hyperparameters, prefix, enable_spot
                    )
                )

            # Collect results for the current batch
            for future in as_completed(futures):
                try:
                    response = future.result()
                    print(f"Training job started: {response['TrainingJobArn']}")
                except Exception as e:
                    print(f"Error in training job: {e}")

        # Update the job count after finishing the batch
        job_count += jobs_in_this_batch
        print(f"Batch completed. {job_count}/{total_jobs} jobs started.")


def list_training_jobs(status_filter="Completed", name_contains="anomaly-training-job"):
    """
    List training jobs in SageMaker with an optional status filter.
    """
    training_jobs = []
    response = sagemaker_client.list_training_jobs(
        SortBy="CreationTime",
        SortOrder="Descending",
        MaxResults=100,  # Adjust the number of results as needed
        StatusEquals=status_filter,  # 'InProgress', 'Completed', 'Failed', etc., or None for all,
        NameContains=name_contains,
    )

    training_jobs.extend(response["TrainingJobSummaries"])

    # Pagination for more training jobs (if needed)
    while "NextToken" in response:
        response = sagemaker_client.list_training_jobs(
            SortBy="CreationTime",
            SortOrder="Descending",
            MaxResults=100,
            StatusEquals=status_filter,
            NameContains=name_contains,
            NextToken=response["NextToken"],
        )
        training_jobs.extend(response["TrainingJobSummaries"])

    return training_jobs


def get_roc_auc_for_job(training_job_name):
    """
    Get the ROC AUC metric for a specific SageMaker training job.
    """
    response = sagemaker_client.describe_training_job(TrainingJobName=training_job_name)

    # Search for the ROC AUC metric in the job's final metrics
    roc_auc_values = []
    if "FinalMetricDataList" in response:
        for metric in response["FinalMetricDataList"]:
            if metric["MetricName"] == "ROC AUC":
                roc_auc_values.append(metric["Value"])
                print(
                    f"Training Job: {training_job_name}, ROC AUC: {metric['Value']:.4f}"
                )

    return roc_auc_values


def aggregate_roc_auc(training_jobs):
    """
    Aggregate ROC AUC metrics across multiple training jobs.
    """
    all_roc_auc_values = []
    for job in training_jobs:
        roc_auc_values = get_roc_auc_for_job(job["TrainingJobName"])
        all_roc_auc_values.extend(roc_auc_values)

    if all_roc_auc_values:
        mean_roc_auc = np.mean(all_roc_auc_values)
        median_roc_auc = np.median(all_roc_auc_values)
        max_roc_auc = np.max(all_roc_auc_values)
        min_roc_auc = np.min(all_roc_auc_values)
        print("\nAggregate ROC AUC Metrics:")
        print(f"Mean ROC AUC:\t{mean_roc_auc:.4f}")
        print(f"Median ROC AUC:\t{median_roc_auc:.4f}")
        print(f"Max ROC AUC:\t{max_roc_auc:.4f}")
        print(f"Min ROC AUC:\t{min_roc_auc:.4f}")
    else:
        print("No ROC AUC metrics found across the listed training jobs.")


if __name__ == "__main__":
    res = Fire(
        {
            "start_training_job_single": start_training_job_single,
            "start_training_jobs_batch": start_training_jobs_batch,
            "list_training_jobs": list_training_jobs,
            "list_and_aggregate_roc_auc": list_and_aggregate_roc_auc,
        }
    )
