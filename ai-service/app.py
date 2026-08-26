import sys
import huggingface_hub

# --- CACHE-BUSTING FIX: Trick the broken cached gradio into working ---
if not hasattr(huggingface_hub, 'HfFolder'):
    class DummyHfFolder:
        def get_token(self): return None
    huggingface_hub.HfFolder = DummyHfFolder

import os
import joblib
import numpy as np
import pandas as pd
import gradio as gr

# --- 1. PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "model_artifacts")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

# --- 2. LOAD ARTIFACTS ---
print("Loading trained model and encoders...")
model = joblib.load(os.path.join(ARTIFACTS_DIR, 'ai_model.joblib'))
le_symptoms = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_symptoms.joblib'))
le_diagnosis = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_diagnosis.joblib'))
le_mood = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_mood.joblib'))
le_stress = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_stress.joblib'))
le_disorder = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_disorder.joblib'))
le_urgency = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_urgency.joblib'))
le_therapy = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_therapy.joblib'))
le_selfcare = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_selfcare.joblib'))
ui_choices = joblib.load(os.path.join(ARTIFACTS_DIR, 'ui_choices.joblib'))

# --- 3. PREDICTION FUNCTION ---
def predict_mental_health(symptoms, duration, prev_diagnosis, therapy_history, medication, mood, stress_level):
    try:
        symptoms_enc = le_symptoms.transform([symptoms])[0]
        duration_enc = duration / 51.0 
        
        if prev_diagnosis in le_diagnosis.classes_: prev_diag_enc = le_diagnosis.transform([prev_diagnosis])[0]
        else: prev_diag_enc = 0 

        if mood in le_mood.classes_: mood_enc = le_mood.transform([mood])[0]
        else: mood_enc = 0

        if stress_level in le_stress.classes_: stress_enc = le_stress.transform([stress_level])[0]
        else: stress_enc = 0

        therapy_enc = 1 if therapy_history == "Yes" else 0
        med_enc = 1 if medication == "Yes" else 0

        X_input = np.array([[symptoms_enc, duration_enc, prev_diag_enc, therapy_enc, med_enc, mood_enc, stress_enc]])
        prediction_encoded = model.predict(X_input)[0]
        
        return {
            "Diagnosis / Condition": str(le_disorder.inverse_transform([prediction_encoded[0]])[0]),
            "Urgency Level": str(le_urgency.inverse_transform([prediction_encoded[1]])[0]),
            "Suggested Therapy": str(le_therapy.inverse_transform([prediction_encoded[2]])[0]),
            "Self-care Advice": str(le_selfcare.inverse_transform([prediction_encoded[3]])[0])
        }
    except Exception as e:
        return {"Error": str(e)}

# --- 4. AUTHENTICATION FUNCTION ---
def mock_login(email: str, password: str):
    if email and password: return {"success": True, "token": "fake-jwt-token-12345", "role": "admin"}
    return {"success": False, "message": "Missing credentials"}

# --- 5. BUILD GRADIO INTERFACES ---
predictor_ui = gr.Interface(
    fn=predict_mental_health,
    inputs=[
        gr.Dropdown(label="Symptoms", choices=ui_choices["symptoms"]),
        gr.Number(label="Duration (weeks)", value=4),
        gr.Dropdown(label="Previous Diagnosis", choices=ui_choices["prev_diag"]),
        gr.Radio(["Yes", "No"], label="Therapy History"),
        gr.Radio(["Yes", "No"], label="Medication"),
        gr.Dropdown(label="Mood", choices=ui_choices["mood"]),
        gr.Dropdown(label="Stress Level", choices=ui_choices["stress"])
    ],
    outputs="json",
    title="MindCare AI Predictor",
    api_name="/predict"
)

auth_ui = gr.Interface(
    fn=mock_login,
    inputs=[gr.Textbox(label="Email"), gr.Textbox(label="Password")],
    outputs="json",
    api_name="/auth/login"
)

demo = gr.TabbedInterface(
    interface_list=[predictor_ui, auth_ui], 
    tab_names=["MindCare Predictor", "Auth API (For React)"]
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
