FROM python:3.9-slim

# Set base directory
WORKDIR /home/user/app

# Copy everything from your repo into the container
COPY . .

# Change directory INTO your ai-service folder where the code lives
WORKDIR /home/user/app/ai-service

# FORCE the platform to delete the old cached Gradio and install a working version
RUN pip install --no-cache-dir --force-reinstall gradio==3.50.2 huggingface_hub==0.19.4

# Install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run the training script from inside that folder
RUN python train_model.py

# Start the app from inside that folder
CMD ["python", "app.py"]
