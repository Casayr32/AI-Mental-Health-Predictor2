import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
import joblib
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'dataset.csv')
artifacts_dir = os.path.join(base_dir, 'model_artifacts')

def train_and_save_model():
    print("Loading dataset...")
    df = pd.read_csv(csv_path)

    # Fill NaN values
    df['Previous Diagnosis'] = df['Previous Diagnosis'].fillna('None')

    # Define exact columns
    input_features = ['Symptoms', 'Duration (weeks)', 'Previous Diagnosis', 'Therapy History', 'Medication', 'Mood', 'Stress Level']
    target_features = ['Diagnosis / Condition', 'Urgency Level', 'Suggested Therapy', 'Self-care Advice']

    X_raw = df[input_features].copy()
    Y_raw = df[target_features].copy()

    print("Encoding input data...")

    # Encode Categorical Inputs
    le_symptoms = LabelEncoder()
    X_raw['Symptoms'] = le_symptoms.fit_transform(X_raw['Symptoms'].astype(str))

    le_diagnosis = LabelEncoder()
    X_raw['Previous Diagnosis'] = le_diagnosis.fit_transform(X_raw['Previous Diagnosis'].astype(str))

    le_mood = LabelEncoder()
    X_raw['Mood'] = le_mood.fit_transform(X_raw['Mood'].astype(str))

    le_stress = LabelEncoder()
    X_raw['Stress Level'] = le_stress.fit_transform(X_raw['Stress Level'].astype(str))

    # Encode Numerical/Binary Inputs
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

    print("Training AI Model...")
    base_model = RandomForestClassifier(n_estimators=100, random_state=42)
    model = MultiOutputClassifier(base_model, n_jobs=-1)
    model.fit(X, Y_encoded)

    print("Saving model and encoders...")
    os.makedirs(artifacts_dir, exist_ok=True)

    # Save all artifacts
    joblib.dump(model, os.path.join(artifacts_dir, 'ai_model.joblib'))
    joblib.dump(le_symptoms, os.path.join(artifacts_dir, 'le_symptoms.joblib'))
    joblib.dump(le_diagnosis, os.path.join(artifacts_dir, 'le_diagnosis.joblib'))
    joblib.dump(le_mood, os.path.join(artifacts_dir, 'le_mood.joblib'))
    joblib.dump(le_stress, os.path.join(artifacts_dir, 'le_stress.joblib'))
    joblib.dump(le_disorder, os.path.join(artifacts_dir, 'le_disorder.joblib'))
    joblib.dump(le_urgency, os.path.join(artifacts_dir, 'le_urgency.joblib'))
    joblib.dump(le_therapy, os.path.join(artifacts_dir, 'le_therapy.joblib'))
    joblib.dump(le_selfcare, os.path.join(artifacts_dir, 'le_selfcare.joblib'))

    print("\n✅ SUCCESS: Model trained and saved successfully!")

if __name__ == '__main__':
    train_and_save_model()
