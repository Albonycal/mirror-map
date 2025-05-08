# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Add --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file into the container at /app
COPY main.py .

# Make port 8050 available - Gunicorn will bind to this
EXPOSE 8050

# Run the application using Gunicorn
# 'main:server' tells Gunicorn to look for the 'server' object in the 'main.py' file
# '--bind 0.0.0.0:8050' makes the app accessible from outside the container on port 8050
# You can adjust the number of workers (-w) based on your needs
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8050", "main:server"]
