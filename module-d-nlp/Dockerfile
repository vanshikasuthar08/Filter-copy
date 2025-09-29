# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Run uvicorn server when the container launches
# The port here is the INTERNAL port inside the container.
# We will connect it to our localhost ports in the docker-compose file.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]