import streamlit as st
from google.cloud import aiplatform
import pandas as pd
from PIL import Image
import io
import json
import re
from google.oauth2 import service_account

# Initialize Streamlit page configuration
st.set_page_config(
    page_title="Fruit and Vegetable Shelf Life Estimator",
    layout="wide",
    page_icon="🥬"
)

# Custom CSS for better UI
st.markdown("""
    <style>
   .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
   .stButton>button:hover {
        background-color: #45a049;
    }
   .reportview-container {
        background: #fafafa;
    }
   .main {
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Load Google Cloud credentials
try:
    credentials_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    project_id = st.secrets["GOOGLE_CLOUD_PROJECT"]
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location="us-central1", credentials=credentials)
    
    # Initialize the Llama 3.2 VL model
    model_resource_name = "projects/{}/locations/us-central1/models/{}".format(project_id, "your-llama-3.2-vl-model-id")
    st.success("Model loaded successfully")

except Exception as e:
    st.error(f"Error loading credentials: {str(e)}")
    st.stop()

# Initialize session state for produce tracking
if 'produce_data' not in st.session_state:
    st.session_state.produce_data = []

def analyze_image(image):
    # Assuming Llama 3.2 VL model is a Vertex AI Image Classification/Annotation model
    # You might need to adjust this to match your model's prediction call
    client = aiplatform.PredictionClient(credentials=credentials)
    with io.BytesIO() as buffered_image:
        image.save(buffered_image, format='PNG')
        buffered_image.seek(0)
        response = client.predict(
            endpoint=model_resource_name,
            instances=[{"content": buffered_image.getvalue()}],
            parameters={}
        ).predictions
    
    # Parse response to extract relevant information
    # This part heavily depends on the model's output format, adjust accordingly
    analysis = []
    for prediction in response:
        for annotation in prediction:
            if annotation.display_name in ["Name of the fruit/vegetable", "Minimum Estimated shelf life", 
                                           "Optimal storage temperature range", "Optimal humidity range", 
                                           "Refrigeration Required", "One key storage tip"]:
                analysis.append(f"{annotation.display_name}:{annotation.text}")
    
    # Special handling for Optimal Storage Conditions
    optimal_conditions = [line for line in analysis if 'Optimal storage temperature range' in line or 'Optimal humidity range' in line]
    if optimal_conditions:
        temp_range = [line for line in optimal_conditions if 'Optimal storage temperature range' in line]
        humidity_range = [line for line in optimal_conditions if 'Optimal humidity range' in line]
        if temp_range and humidity_range:
            optimal_conditions = [f"Optimal Storage Conditions: Temperature: {temp_range[0].split(':')[1].strip()}, Humidity: {humidity_range[0].split(':')[1].strip()}"]
        elif temp_range:
            optimal_conditions = [f"Optimal Storage Conditions: {temp_range[0]}"]
        else:
            optimal_conditions = [f"Optimal Storage Conditions: {humidity_range[0]}"]
        analysis = [line for line in analysis if 'Optimal storage temperature range' not in line and 'Optimal humidity range' not in line]
        analysis.extend(optimal_conditions)
    
    return "\n".join(analysis)

def parse_produce_details(analysis):
    details = {
        "Name": "Not identified",
        "Estimated Shelf Life": "Not estimated",
        "Optimal Storage Conditions": "Not specified",
        "Refrigeration Required": "Not specified",
        "Storage Tip": "Not provided"
    }
    
    if analysis:
        lines = analysis.split('\n')
        for line in lines:
            if 'Name of the fruit/vegetable:' in line:
                details["Name"] = line.split(':', 1)[1].strip()
            elif 'Minimum Estimated shelf life:' in line:
                details["Estimated Shelf Life"] = line.split(':', 1)[1].strip()
            elif 'Optimal Storage Conditions:' in line:
                details["Optimal Storage Conditions"] = line.split(':', 1)[1].strip()
            elif 'Refrigeration Required:' in line:
                details["Refrigeration Required"] = line.split(':', 1)[1].strip()
            elif 'One key storage tip:' in line:
                details["Storage Tip"] = line.split(':', 1)[1].strip()
    
    # Remove leading asterisks from all fields
    for key in details:
        if isinstance(details[key], str) and details[key].startswith('**'):
            details[key] = details[key].lstrip('* ')
    
    return details

def update_produce_data(details):
    # Check if produce already exists
    for produce in st.session_state.produce_data:
        if produce['Name'].lower() == details['Name'].lower():
            # Update existing entry
            produce.update(details)
            return
    
    # Add new entry if not found
    st.session_state.produce_data.append(details)

def main():
    st.title("Fruit and Vegetable Shelf Life Estimator")
    
    uploaded_file = st.file_uploader("Choose an image of a fruit or vegetable", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Resize image for display
        max_width = 300
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        resized_image = image.resize(new_size)
        
        # Display resized image
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(resized_image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("Estimate Shelf Life"):
                with st.spinner("Analyzing image..."):
                    analysis = analyze_image(image)
                    if analysis:
                        details = parse_produce_details(analysis)
                        update_produce_data(details)
                    
                        st.subheader("Produce Details:")
                        for key, value in details.items():
                            st.write(f"**{key}:** {value}")
                    else:
                        st.error("Unable to analyze the image. Please try again with a different image.")
    
    st.subheader("Analyzed Produce History")
    if st.session_state.produce_data:
        df = pd.DataFrame(st.session_state.produce_data)
        
        # Reorder columns
        columns_order = ['Name', 'Estimated Shelf Life', 'Optimal Storage Conditions', 'Refrigeration Required', 'Storage Tip']
        df = df[columns_order]
        
        # Style the dataframe
        styled_df = df.style.set_properties(**{'text-align': 'left'})
        styled_df = styled_df.set_table_styles([
            {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'left')]},
            {'selector': 'td', 'props': [('max-width', '200px'), ('white-space', 'normal')]}
        ])
        
        st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("No produce analyzed yet.")

if __name__ == "__main__":
    main()
