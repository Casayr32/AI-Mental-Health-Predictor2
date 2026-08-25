import os
import joblib
import pandas as pd
import gradio as gr

# Load Model Artifacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model_artifacts")

model = joblib.load(os.path.join(MODEL_DIR, "best_model.joblib"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
features = joblib.load(os.path.join(MODEL_DIR, "features.joblib"))

def predict_mental_health(age, gender, family_history, work_interfere, no_employees, remote_work, tech_company, benefits, care_options):
    input_data = pd.DataFrame([{
        'Age': age,
        'Gender': gender,
        'family_history': family_history,
        'work_interfere': work_interfere,
        'no_employees': no_employees,
        'remote_work': remote_work,
        'tech_company': tech_company,
        'benefits': benefits,
        'care_options': care_options
    }])
    
    scaled_data = scaler.transform(input_data[features])
    prediction = model.predict(scaled_data)[0]
    probability = model.predict_proba(scaled_data)[0][1]
    
    result = "Needs Treatment" if prediction == 1 else "No Immediate Treatment Needed"
    return {
        "prediction": result,
        "confidence": float(probability)
    }

# Gradio Interface
demo = gr.Interface(
    fn=predict_mental_health,
    inputs=[
        gr.Number(label="Age", value=25),
        gr.Dropdown(["Male", "Female", "Other"], label="Gender"),
        gr.Radio(["Yes", "No"], label="Family History"),
        gr.Dropdown(["Never", "Rarely", "Sometimes", "Often"], label="Work Interfere"),
        gr.Dropdown(["1-5", "6-25", "26-100", "100-500", "500-1000", "More than 1000"], label="No. Employees"),
        gr.Radio(["Yes", "No"], label="Remote Work"),
        gr.Radio(["Yes", "No"], label="Tech Company"),
        gr.Radio(["Yes", "No", "Don't know"], label="Benefits"),
        gr.Radio(["Yes", "No", "Not sure"], label="Care Options")
    ],
    outputs="json",
    title="MindCare AI Predictor"
)

if __name__ == "__main__":
    demo.launch()
