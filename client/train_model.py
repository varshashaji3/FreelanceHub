import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.naive_bayes import GaussianNB  # Import Naive Bayes model
import joblib
import os

# Define the path for saving model files
model_dir = 'C:\\Users\\LENOVO\\Desktop\\freelancehub\\freelancehub\\models'

# Load the dataset
data = pd.read_csv('C:/Users/LENOVO/Desktop/freelancehub/client/data.csv')

# Check for missing values
print("Missing values in each column:\n", data.isnull().sum())

# Ensure column names are stripped of any extra spaces
data.columns = data.columns.str.strip()

# Convert categorical columns to numeric using Label Encoding
categorical_columns = ['Category', 'Complexity']
label_encoders = {}

for col in categorical_columns:
    le = LabelEncoder()
    data[col] = data[col].astype(str)
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Define features and target variable
X = data[['ProposedDeadline', 'FreelancerID', 'Category', 'Complexity']]
y = data['CompletedOntime'].apply(lambda x: 1 if x == 'TRUE' else 0)

# Print data shapes
print(f"Data shape: {data.shape}")
print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Print shapes after split
print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"y_test shape: {y_test.shape}")

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Initialize the model
model = GaussianNB()  # Change to Naive Bayes model

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save the model, scaler, and label encoders
model_path = os.path.join(model_dir, 'final_model.pkl')
scaler_path = os.path.join(model_dir, 'final_scaler.pkl')
le_path = os.path.join(model_dir, 'final_label_encoders.pkl')

joblib.dump(model, model_path)
joblib.dump(scaler, scaler_path)
joblib.dump(label_encoders, le_path)

print("Model, scaler, and label encoders saved successfully.")

def predict_for_freelancer(freelancer_id):
    # Predict for a specific FreelancerID
    freelancer_data = data[data['FreelancerID'] == freelancer_id]

    if not freelancer_data.empty:
        X_freelancer = freelancer_data[['ProposedDeadline', 'FreelancerID', 'Category', 'Complexity']]
        X_freelancer_scaled = scaler.transform(X_freelancer)
        freelancer_prediction = model.predict(X_freelancer_scaled)
        print(f"Predictions for FreelancerID {freelancer_id}: {freelancer_prediction}")
    else:
        print(f"No data found for FreelancerID {freelancer_id}.")
