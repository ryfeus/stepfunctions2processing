import boto3
import json
import io
import random
import string
from datetime import datetime

def handlerPreprocessing(event,context):
	letters = string.ascii_lowercase
	suffix = ''.join(random.choice(letters) for i in range(10))
	jobParameters = {
		'name': 'model-trainining-'+str(datetime.date(datetime.now()))+'-'+suffix,
		'hyperparameters': {
			'num_of_epochs': '4'
		}
	}
	return jobParameters

def handlerPostprocessing(event,context):
	print(event)
	return event