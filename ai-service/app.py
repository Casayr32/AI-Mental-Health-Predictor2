import os
import joblib
import numpy as np
import gradio as gr

# --- 1. LOAD ARTIFACTS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "model_artifacts")

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

# --- 2. PREDICTION FUNCTION ---
def predict_mental_health(symptoms, duration, prev_diagnosis, therapy_history, medication, mood, stress_level):
    try:
        # Encode inputs exactly like training
        symptoms_enc = le_symptoms.transform([symptoms])[0]
        duration_enc = duration / 51.0 
        
        # Handle unseen labels safely
        if prev_diagnosis in le_diagnosis.classes_:
            prev_diag_enc = le_diagnosis.transform([prev_diagnosis])[0]
        else:
            prev_diag_enc = 0 

        if mood in le_mood.classes_:
            mood_enc = le_mood.transform([mood])[0]
        else:
            mood_enc = 0

        if stress_level in le_stress.classes_:
            stress_enc = le_stress.transform([stress_level])[0]
        else:
            stress_enc = 0

        therapy_enc = 1 if therapy_history == "Yes" else 0
        med_enc = 1 if medication == "Yes" else 0

        # Create array (MUST match the exact column order from train_model.py)
        X_input = np.array([[symptoms_enc, duration_enc, prev_diag_enc, therapy_enc, med_enc, mood_enc, stress_enc]])

        # Predict
        prediction_encoded = model.predict(X_input)[0]
        
        # Decode back to text
        diagnosis = le_disorder.inverse_transform([prediction_encoded[0]])[0]
        urgency = le_urgency.inverse_transform([prediction_encoded[1]])[0]
        therapy = le_therapy.inverse_transform([prediction_encoded[2]])[0]
        selfcare = le_selfcare.inverse_transform([prediction_encoded[3]])[0]

        return {
            "Diagnosis / Condition": str(diagnosis),
            "Urgency Level": str(urgency),
            "Suggested Therapy": str(therapy),
            "Self-care Advice": str(selfcare)
        }
    except Exception as e:
        return {"Error": f"Prediction failed: {str(e)}"}

# --- 3. GRADIO INTERFACE ---
# WARNING: Replace the choices=[] lists below with the ACTAL text options from your dataset.csv!
demo = gr.Interface(
    fn=predict_mental_health,
    inputs=[
        gr.Dropdown(label="Symptoms", choices=["Anxiety", "Depression", "Panic Attacks"]), # UPDATE CHOICES
        gr.Number(label="Duration (weeks)", value=4),
        gr.Dropdown(label="Previous Diagnosis", choices=["None", "ADHD", "Bipolar"]), # UPDATE CHOICES
        gr.Radio(["Yes", "No"], label="Therapy History"),
        gr.Radio(["Yes", "No"], label="Medication"),
        gr.Dropdown(label="Mood", choices=["Sad", "Anxious", "Normal"]), # UPDATE CHOICES
        gr.Dropdown(label="Stress Level", choices=["Low", "Medium", "High"]) # UPDATE CHOICES
    ],
    outputs="json",
    title="MindCare AI Predictor",
    description="Multi-output mental health prediction model."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
