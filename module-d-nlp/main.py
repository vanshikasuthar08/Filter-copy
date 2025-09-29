import joblib
from fastapi import FastAPI
from pydantic import BaseModel

# We will create the extractor.py file next
from extractor import extract_entities

app = FastAPI()

# Load the Scikit-learn models ONCE when the app starts
try:
    dept_model = joblib.load("department_classifier.pkl")
    doctype_model = joblib.load("doctype_classifier.pkl")
except FileNotFoundError:
    print("ERROR: Models not found. Please run train.py first.")
    dept_model = None
    doctype_model = None

class DocumentRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze_document(request: DocumentRequest):
    if not dept_model or not doctype_model:
        return {"error": "Models are not loaded."}
    
    # --- 1. Classify ---
    # The predict method returns an array with one item, so we take the first one [0]
    dept_label = dept_model.predict([request.text])[0]
    doctype_label = doctype_model.predict([request.text])[0]

    # Scikit-learn models don't give confidence scores by default in this setup,
    # so we'll just return a placeholder for the demo.
    dept_confidence = 0.95 
    doctype_confidence = 0.95

    # --- 2. Extract Entities (We will add this back in the next step) ---
    entities = extract_entities(request.text)
    
    # --- 3. Priority Scoring (Simple Rules) ---
    priority_score = 5 # Default priority
    if "urgent" in request.text.lower() or "due immediately" in request.text.lower():
        priority_score = 10
    if doctype_label == 'invoice':
        priority_score += 2
    
    # Build the final response
    response = {
        "department": {"label": dept_label, "confidence": f"{dept_confidence:.2f}"},
        "doc_type": {"label": doctype_label, "confidence": f"{doctype_confidence:.2f}"},
        "entities": entities,
        "priority_score": min(priority_score, 10) # Cap score at 10
    }

    return response

@app.get("/")
def root():
    return {"message": "Module D - NLP Analyzer is running with Scikit-learn!"}