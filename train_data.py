import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib

# Load the dataset
df = pd.read_csv('train data.csv')
print(df.head())

# Preprocess the data
X = df['text']  # Feature
y = df['label']  # Label

# Convert text data into numerical data
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save the model and vectorizer
joblib.dump(model, 'intent_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

# Function to predict intent with fallback
def predict_intent(query):
    query_vec = vectorizer.transform([query])
    intents_proba = model.predict_proba(query_vec)[0]
    max_proba_index = np.argmax(intents_proba)
    max_proba = intents_proba[max_proba_index]
    if max_proba < 0.3:  # Adjust the threshold as needed
        return 'fallback_intent'
    else:
        return model.classes_[max_proba_index]

# Test the predict_intent function
query = "launch YouTube"
intent = predict_intent(query)
print(intent)
