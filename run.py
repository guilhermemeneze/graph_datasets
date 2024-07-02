import streamlit as st
from PIL import Image
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import json

# Function to authenticate and create a PyDrive client using the provided tokens
def authenticate_with_tokens():
    gauth = GoogleAuth()

    # Load the OAuth2 tokens from a JSON string (assuming you have the token JSON)
    token_json = '''
    {
        "issued_at": "1420258685042",
        "scope": "READ",
        "application_name": "ce1e94a2-9c3e-42fa-a2c6-1ee01815476b",
        "refresh_token_issued_at": "1420258685042",
        "status": "approved",
        "refresh_token_status": "approved",
        "api_product_list": "[PremiumWeatherAPI]",
        "expires_in": "1799",
        "developer.email": "tesla@weathersample.com",
        "organization_id": "0",
        "token_type": "BearerToken",
        "refresh_token": "IFl7jlijYuexu6XVSSjLMJq8SVXGOAAq",
        "client_id": "5jUAdGv9pBouF0wOH5keAVI35GBtx3dT",
        "access_token": "I6daIgMSiUgYX1K2qgQWPi37ztS6",
        "organization_name": "docs",
        "refresh_token_expires_in": "28799",
        "refresh_count": "0"
    }
    '''
    tokens = json.loads(token_json)

    gauth.credentials = {
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_expiry': tokens['expires_in'],
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': tokens['client_id'],
        'client_secret': 'YOUR_CLIENT_SECRET',  # Replace with your client secret
        'scopes': ['https://www.googleapis.com/auth/drive']
    }

    drive = GoogleDrive(gauth)
    return drive

# Function to save annotations to Google Drive
def save_annotations_to_drive(annotations, folder_id, drive):
    # Create a DataFrame and save as CSV
    df = pd.DataFrame(annotations, columns=['Image Name', 'Class'])
    file_path = "annotations.csv"
    df.to_csv(file_path, index=False)

    # Create a file in Google Drive
    gfile = drive.CreateFile({'parents': [{'id': folder_id}], 'title': 'annotations.csv'})
    gfile.SetContentFile(file_path)
    gfile.Upload()

    st.success(f"Annotations saved to Google Drive in folder ID: {folder_id}")

# Streamlit app
st.title("Image Annotation Tool")

# Image upload
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'class_label' not in st.session_state:
    st.session_state.class_label = None

# CSS to style the annotated button
st.markdown(
    """
    <style>
    .annotated {
        background-color: green !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if uploaded_files:
    total_images = len(uploaded_files)
    current_file = uploaded_files[st.session_state.current_index]

    # Display the current image
    image = Image.open(current_file)
    st.image(image, caption=f'Uploaded Image: {current_file.name}', use_column_width=True)

    # Function to handle annotation
    def annotate_image():
        if st.session_state.class_label is not None:
            st.session_state.annotations[current_file.name] = st.session_state.class_label

    # Class selection using radio buttons
    st.write("Select class for this image:")
    class_options = ['None'] + ['Unreadable','Bacterial feeder', 'Fungal feeder', 'Plant parasite', 'Omnivore', 'Predator']
    current_annotation = st.session_state.annotations.get(current_file.name, 'None')

    selected_class = st.radio("Class", class_options, index=class_options.index(current_annotation))

    # Update class_label if a valid class is selected
    st.session_state.class_label = selected_class if selected_class != 'None' else None

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous Image") and st.session_state.current_index > 0:
            annotate_image()
            st.session_state.current_index = (st.session_state.current_index - 1) % total_images
            st.session_state.class_label = None
            st.experimental_rerun()
    with col3:
        if st.button("Next Image") and st.session_state.current_index < total_images - 1:
            annotate_image()
            st.session_state.current_index = (st.session_state.current_index + 1) % total_images
            st.session_state.class_label = None
            st.experimental_rerun()

    # Indicate annotated images
    annotated_images = [file.name for file in uploaded_files if file.name in st.session_state.annotations]
    st.write(f"Annotated images: {', '.join(annotated_images)}")

    # Save annotations
    folder_id = "1cH0XlTJDGriYfVbSeUDSFsDdxEloSJUq"  # The Google Drive folder ID
    if st.button("Save Annotations"):
        annotations_list = [(name, label) for name, label in st.session_state.annotations.items()]
        drive = authenticate_with_tokens()
        save_annotations_to_drive(annotations_list, folder_id, drive)
        # Reset session state
        st.session_state.annotations = {}
        st.session_state.current_index = 0


