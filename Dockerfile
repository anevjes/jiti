# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code into the container at /app
COPY jiti-mcp-server/ .

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Define environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Run the server — transport, host, and port are configured in server.py
CMD ["python", "server.py"]
