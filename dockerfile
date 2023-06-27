# Use an official Python runtime as the base image
FROM python:3.12-rc-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the server file into the container
COPY server.py .
COPY test_server.py .

# Expose the desired port
EXPOSE 5000

# Start the server
CMD [ "python", "server.py" ]
