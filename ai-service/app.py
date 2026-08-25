import os
import gc
import joblib
import numpy as np
import pandas as pd
import gradio as gr
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

# --- 1. PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "model_artifacts")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'ai_model.joblib')
CHOICES_PATH = os.path.join(ARTIFACTS_DIR, 'ui_choices.joblib')

# --- 2. AUTO-TRAINING LOGIC ---
if not os.path.exists(MODEL_PATH):
    print("❌ Model not found. Starting training process right now...")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        df['Previous Diagnosis'] = df['Previous Diagnosis'].fillna('None')

        input_features = ['Symptoms', 'Duration (weeks)', 'Previous Diagnosis', 'Therapy History', 'Medication', 'Mood', 'Stress Level']
        target_features = ['Diagnosis / Condition', 'Urgency Level', 'Suggested Therapy', 'Self-care Advice']

        X_raw = df[input_features].copy()
        Y_raw = df[target_features].copy()

        print("Encoding input data...")
        le_symptoms = LabelEncoder()
        X_raw['Symptoms'] = le_symptoms.fit_transform(X_raw['Symptoms'].astype(str))

        le_diagnosis = LabelEncoder()
        X_raw['Previous Diagnosis'] = le_diagnosis.fit_transform(X_raw['Previous Diagnosis'].astype(str))

        le_mood = LabelEncoder()
        X_raw['Mood'] = le_mood.fit_transform(X_raw['Mood'].astype(str))

        le_stress = LabelEncoder()
        X_raw['Stress Level'] = le_stress.fit_transform(X_raw['Stress Level'].astype(str))

        X_raw['Duration (weeks)'] = X_raw['Duration (weeks)'] / 51.0 
        X_raw['Therapy History'] = X_raw['Therapy History'].map({'Yes': 1, 'No': 0}).fillna(0)
        X_raw['Medication'] = X_raw['Medication'].map({'Yes': 1, 'No': 0}).fillna(0)

        X = X_raw.values

        print("Encoding target data...")
        le_disorder = LabelEncoder()
        le_urgency = LabelEncoder()
        le_therapy = LabelEncoder()
        le_selfcare = LabelEncoder()

        Y_encoded = np.column_stack([
            le_disorder.fit_transform(Y_raw['Diagnosis / Condition'].astype(str)),
            le_urgency.fit_transform(Y_raw['Urgency Level'].astype(str)),
            le_therapy.fit_transform(Y_raw['Suggested Therapy'].astype(str)),
            le_selfcare.fit_transform(Y_raw['Self-care Advice'].astype(str))
        ])

        # Save UI choices NOW so we don't have to read the CSV again later
        ui_choices = {
            "symptoms": df['Symptoms'].dropna().unique().tolist(),
            "prev_diag": df['Previous Diagnosis'].fillna('None').unique().tolist(),
            "mood": df['Mood'].dropna().unique().tolist(),
            "stress": df['Stress Level'].dropna().unique().tolist()
        }

        print("Training AI Model (Optimized for low memory)...")
        # CHANGED TO 30 TREES TO SAVE RAM
        base_model = RandomForestClassifier(n_estimators=30, random_state=42)
        model = MultiOutputClassifier(base_model, n_jobs=-1)
        model.fit(X, Y_encoded)

        print("Saving model and encoders...")
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(le_symptoms, os.path.join(ARTIFACTS_DIR, 'le_symptoms.joblib'))
        joblib.dump(le_diagnosis, os.path.join(ARTIFACTS_DIR, 'le_diagnosis.joblib'))
        joblib.dump(le_mood, os.path.join(ARTIFACTS_DIR, 'le_mood.joblib'))
        joblib.dump(le_stress, os.path.join(ARTIFACTS_DIR, 'le_stress.joblib'))
        joblib.dump(le_disorder, os.path.join(ARTIFACTS_DIR, 'le_disorder.joblib'))
        joblib.dump(le_urgency, os.path.join(ARTIFACTS_DIR, 'le_urgency.joblib'))
        joblib.dump(le_therapy, os.path.join(ARTIFACTS_DIR, 'le_therapy.joblib'))
        joblib.dump(le_selfcare, os.path.join(ARTIFACTS_DIR, 'le_selfcare.joblib'))
        joblib.dump(ui_choices, CHOICES_PATH)
        
        # FREE UP RAM
        del df, X_raw, Y_raw, X, Y_encoded, model, base_model
        gc.collect()
        
        print("✅ SUCCESS: Model trained, saved, and memory cleared!")

    except Exception as e:
        print(f"🔴 TRAINING FAILED: {str(e)}")

# --- 3. LOAD ARTIFACTS ---
print("Loading trained model and encoders...")
model = joblib.load(MODEL_PATH)
le_symptoms = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_symptoms.joblib'))
le_diagnosis = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_diagnosis.joblib'))
le_mood = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_mood.joblib'))
le_stress = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_stress.joblib'))
le_disorder = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_disorder.joblib'))
le_urgency = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_urgency.joblib'))
le_therapy = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_therapy.joblib'))
le_selfcare = joblib.load(os.path.join(ARTIFACTS_DIR, 'le_selfcare.joblib'))

# Load choices from saved file instead of reading CSV again!
ui_choices = joblib.load(CHOICES_PATH)

# --- 4. PREDICTION FUNCTION ---
def predict_mental_health(symptoms, duration, prev_diagnosis, therapy_history, medication, mood, stress_level):
    try:
        symptoms_enc = le_symptoms.transform([symptoms])[0]
        duration_enc = duration / 51.0 
        
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

        X_input = np.array([[symptoms_enc, duration_enc, prev_diag_enc, therapy_enc, med_enc, mood_enc, stress_enc]])
        prediction_encoded = model.predict(X_input)[0]
        
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
        return {"Error": str(e)}

# --- 5. AUTHENTICATION FUNCTION ---
def mock_login(email: str, password: str):
    print(f"Login attempt for: {email}")
    if email and password:
        return {"success": True, "token": "fake-jwt-token-12345", "role": "admin"}
    return {"success": False, "message": "Missing credentials"}

# --- 6. BUILD GRADIO INTERFACES ---
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

# --- 7. COMBINE AND LAUNCH ---
demo = gr.TabbedInterface(
    interface_list=[predictor_ui, auth_ui], 
    tab_names=["MindCare Predictor", "Auth API (For React)"]
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
