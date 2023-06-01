# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt into the container at /app
COPY app/requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app/ /app

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Tells Docker how to test a Streamlit container to check that it is still working. 
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app.py when the container launches
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]