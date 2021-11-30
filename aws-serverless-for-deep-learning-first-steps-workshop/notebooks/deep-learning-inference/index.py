import boto3
import json
import io
import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image
interpreter = None

def handlerMapper(event,context):
  if (np.random.rand(1)>0.5):
    event['model_type'] = 'NewModel'
  else:
    event['model_type'] = 'OldModel'
  return event

def runInference(interpreter, input_data):
  input_details = interpreter.get_input_details()
  output_details = interpreter.get_output_details()
  interpreter.set_tensor(input_details[0]['index'], input_data)
  interpreter.invoke()
  output_data = interpreter.get_tensor(output_details[0]['index'])
  return output_data

def handlerInferenceNew(event, context):
  label_list = [
    'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag',
    'Ankle boot'
  ]
  global interpreter
  if interpreter is None:
    interpreter = tflite.Interpreter(model_path="models/converted_model_2.tflite")
    interpreter.allocate_tensors()

  input_image = Image.open("images/test.png")
  input_data = np.expand_dims(np.array(input_image, dtype=np.float32)/255, axis=0)
  
  output_data = runInference(interpreter, input_data)
  return {'feature_vector':output_data.tolist(), 'prediction':label_list[np.argmax(output_data)], 'model_type':'NewModel'}

def handlerInferenceOld(event, context):
  label_list = [
    'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag',
    'Ankle boot'
  ]
  global interpreter
  if interpreter is None:
    interpreter = tflite.Interpreter(model_path="models/converted_model_1.tflite")
    interpreter.allocate_tensors()

  if ('image' in event):
    input_data = loadImage('course-pdl-inference', event['image'])
  else:
    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)

  output_data = runInference(interpreter, input_data)
  return {'feature_vector':output_data.tolist(), 'prediction':label_list[np.argmax(output_data)], 'model_type':'OldModel'}

def handlerPublisher(event,context):
  print(event)
  return event