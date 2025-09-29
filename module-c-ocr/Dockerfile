# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies needed by OpenCV and Tesseract
# The package name has been corrected from libgl1-mesa-glx to libgl1
RUN apt-get update && apt-get install -y libgl1 tesseract-ocr tesseract-ocr-mal

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Run uvicorn server when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
