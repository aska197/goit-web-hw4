# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
RUN pip install flask

# Copy the rest of the application code into the container
COPY . .

# Expose port 3000 to allow communication to/from the container
EXPOSE 3000

# Command to run the Flask application
CMD ["python", "main.py"]

