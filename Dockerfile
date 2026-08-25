FROM python:3.9-slim

WORKDIR /home/user/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train the model during the Hugging Face build
RUN python train_model.py

# Start the Gradio app
CMD ["python", "app.py"]
