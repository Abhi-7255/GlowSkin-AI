# Use a Python image
FROM python:3.9-slim

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container
COPY --chown=user . $HOME/app

# Install requirements (OpenCV needs some extra system libraries to run on Linux)
USER root
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
USER user
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 7860
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]