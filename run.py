# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 12:18:56 2024

@author: Badger
"""

import streamlit as st
from PIL import Image
import pandas as pd
import os

# Function to save annotations to a CSV file
def save_annotations(annotations, directory):
    df = pd.DataFrame(annotations, columns=['Image Name', 'Class'])
    
    # Find a unique filename
    base_filename = "annotations"
    extension = ".csv"
    save_path = os.path.join(directory, base_filename + extension)
    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(directory, f"{base_filename}({counter}){extension}")
        counter += 1
    
    df.to_csv(save_path, index=False)
    st.success(f"Annotations saved to {save_path}")

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

    # Directory input for saving annotations
    save_path_directory = st.text_input("Enter directory to save annotations:", "C:\\Users\\Badger\\Downloads")
    if not os.path.exists(save_path_directory):
        st.warning(f"Directory {save_path_directory} does not exist. Please enter a valid directory.")
    
    # Save annotations
    if st.button("Save Annotations") and os.path.exists(save_path_directory):
        annotations_list = [(name, label) for name, label in st.session_state.annotations.items()]
        save_annotations(annotations_list, save_path_directory)
        # Reset session state
        st.session_state.annotations = {}
        st.session_state.current_index = 0






