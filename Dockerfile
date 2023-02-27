# Use the base image as the base image
FROM docker.io/hygoogi/jamminiz-base:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the Python source code to the container
COPY . .

# Run the Python application when the container starts
CMD [ "python", "main.py" ]
