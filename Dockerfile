# Use standard Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /home/user/app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your code AND your dataset.csv into the container
COPY . .

# Train the model during the build process
RUN python train_model.py

# Run the Gradio app when the container starts
CMD ["python", "app.py"]
