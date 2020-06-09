FROM tensorflow/tensorflow:1.12.0-gpu-py3
RUN pip3 install boto3
ENV PATH="/opt/ml/code:${PATH}"
COPY . /opt/ml/code/
WORKDIR /opt/ml/code
RUN chmod 777 /opt/ml/code/train