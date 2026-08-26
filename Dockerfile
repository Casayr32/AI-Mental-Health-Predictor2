FROM python:3.9-slim

# Set base directory
WORKDIR /home/user/app

# Copy everything from your repo into the container
COPY . .

# Change directory INTO your ai-service folder where the code lives
WORKDIR /home/user/app/ai-service

# Upgrade pip first for reliability, then install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Run the training script from inside that folder
RUN python train_model.py

# Start the app from inside that folder
CMD ["python", "app.py"]
