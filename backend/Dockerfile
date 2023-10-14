# Use the official Python image as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

RUN pip install gunicorn==20.1.0 

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt --no-cache-dir


# Copy the rest of the application code into the container
COPY . /app/

# Expose the port that the application will run on
EXPOSE 8000

# Define the command to run your application
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "foodgram.wsgi"]
