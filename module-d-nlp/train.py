import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import joblib # For saving the model

print("Loading and preparing data...")
df = pd.read_csv("documents.csv")

# --- Train Department Classifier ---
print("Training Department Classifier...")
# Create a pipeline: text -> numbers -> classifier
department_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42)),
])

# Train the model on the full dataset
department_pipeline.fit(df['text'], df['department'])

# Save the trained pipeline
joblib.dump(department_pipeline, 'department_classifier.pkl')
print("Department classifier saved to department_classifier.pkl\n")


# --- Train Document Type Classifier ---
print("Training Document Type Classifier...")
doctype_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42)),
])

# Train the model
doctype_pipeline.fit(df['text'], df['doc_type'])

# Save the trained pipeline
joblib.dump(doctype_pipeline, 'doctype_classifier.pkl')
print("Document Type classifier saved to doctype_classifier.pkl")
