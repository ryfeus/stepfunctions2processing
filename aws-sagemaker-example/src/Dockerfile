FROM --platform=linux/amd64 nvidia/cuda:12.6.2-cudnn-runtime-ubuntu22.04

# Install Python and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.9 \
        python3-pip \
        && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python and pip
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Install Python dependencies
COPY requirements.txt /opt/ml/code/requirements.txt
RUN pip install --no-cache-dir -r /opt/ml/code/requirements.txt

# Set up environment variables for SageMaker
ENV PATH="/opt/ml/code:${PATH}"

# Copy the training code into the container at /opt/ml/code
COPY train /opt/ml/code/train

# Set the working directory to /opt/ml/code
WORKDIR /opt/ml/code

# Empty the entrypoint and set permissions for the training script
RUN chmod 777 /opt/ml/code/train
ENTRYPOINT []