import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from PIL import Image
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import joblib
import streamlit as st
model_pipeline = joblib.load('sgd_classifier_model.joblib')

# Load the SGD classifier, TF-IDF vectorizer, and label encoder
sgd_classifier = joblib.load('sgd_classifier_model.joblib')
label_encoder = joblib.load('label_encoder.joblib')

# Load the logo image
logo = Image.open('logo.png')

# Function to clean and preprocess text
def preprocess_text(text):
    text = re.sub(r'http\S+|www\S+|@\S+|#\S+|[^A-Za-z\s]', '', text)
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

# Function for binary cyberbullying detection
def binary_cyberbullying_detection(text):
    try:
        # Preprocess the input text
        preprocessed_text = preprocess_text(text)

        # Make prediction using the loaded pipeline
        prediction = model_pipeline.predict([preprocessed_text])

        # Check for offensive words
        with open('en.txt', 'r') as f:
            offensive_words = [line.strip() for line in f]

        offending_words = [word for word in preprocessed_text.split() if word in offensive_words]

        return prediction[0], offending_words
    except Exception as e:
        st.error(f"Error in binary_cyberbullying_detection: {e}")
        return None, None

# Function for multi-class cyberbullying detection
def multi_class_cyberbullying_detection(text):
    try:
        # Preprocess the input text
        preprocessed_text = preprocess_text(text)

        # Make prediction
        decision_function_values = sgd_classifier.decision_function([preprocessed_text])[0]

        # Get the predicted class index
        predicted_class_index = np.argmax(decision_function_values)

        # Get the predicted class label using the label encoder
        predicted_class_label = label_encoder.inverse_transform([predicted_class_index])[0]

        return predicted_class_label, decision_function_values
    except Exception as e:
        st.error(f"Error in multi_class_cyberbullying_detection: {e}")
        return None

def detect():
    st.title('Cyberbullying Detection App')

    # Input text box
    user_input = st.text_area("Share your thoughts:", "", key="user_input")

    # Make binary prediction and check for offensive words
    binary_result, offensive_words = binary_cyberbullying_detection(user_input)

    # View flag for detailed predictions
    view_flagging_reasons = binary_result == 1
    view_predictions = st.checkbox("View Flagging Reasons", value=view_flagging_reasons)

    # Check if the user has entered any text
    if user_input:
        st.markdown("<div class='st-bw'>", unsafe_allow_html=True)

        # Display binary prediction only if "View Flagging Reasons" is checked
        if view_predictions and binary_result == 1:
            st.write(f"Binary Cyberbullying Prediction: {'Cyberbullying' if binary_result == 1 else 'Not Cyberbullying'}")

        # Check for offensive words and display warning
        if offensive_words and (view_predictions or binary_result == 0):
            # Adjust the warning message based on cyberbullying classification
            if binary_result == 1:
                st.warning(f"This text contains offensive language. Consider editing. Detected offensive words: {offensive_words}")
            else:
                st.warning(f"While this text is not necessarily cyberbullying, it may contain offensive language. Consider editing. Detected offensive words: {offensive_words}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Make multi-class prediction
        multi_class_result = multi_class_cyberbullying_detection(user_input)
        if multi_class_result is not None:
            predicted_class, prediction_probs = multi_class_result
            st.markdown("<div class='st-eb'>", unsafe_allow_html=True)

            if view_predictions:
                st.write(f"Multi-Class Predicted Class: {predicted_class}")

            st.markdown("</div>", unsafe_allow_html=True)

            # Check if classified as cyberbullying
            if predicted_class != 'not_cyberbullying':
                st.error(f"Please edit your text before resending. Your text contains content that may appear as bullying to other users' {predicted_class.replace('_', ' ').title()}.")
            elif offensive_words and not view_predictions:
                st.warning("While this text is not necessarily cyberbullying, it may contain offensive language. Consider editing.")
            else:
                # Display message before sending
                st.success('This text is safe to send.')
def main():
    st.set_page_config(
        page_title="Cyberbullying Detection App",
        page_icon=logo,
        layout="centered"
    )

    detect()

if __name__ == "__main__":
    main()
