# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /
WORKDIR /

# Avoid timezone interactive selection
ENV DEBIAN_FRONTEND=noninteractive

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Add the current directory contents into the container at /
ADD . /

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
# EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "topic.py"]
