import streamlit as st
from PIL import Image
import pandas as pd
import os

# Function to save annotations locally in the same directory as the uploaded images
def save_annotations_locally(annotations, directory):
    df = pd.DataFrame(annotations, columns=['Image Name', 'Class'])

    # Ensure directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save to a file
    file_path = os.path.join(directory, "annotations.csv")
    df.to_csv(file_path, index=False)
    st.success(f"Annotations saved locally at {file_path}")

# Function to convert DataFrame to CSV for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

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
    class_options = ['None'] + ['Unreadable', 'Bacterial feeder', 'Fungal feeder', 'Plant parasite', 'Omnivore', 'Predator']
    current_annotation = st.session_state.annotations.get(current_file.name, 'None')

    selected_class = st.radio("Class", class_options, index=class_options.index(current_annotation))

    # Update class_label if a valid class is selected
    if selected_class != 'None':
        st.session_state.class_label = selected_class
    else:
        st.session_state.class_label = None

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Previous Image") and st.session_state.current_index > 0:
            annotate_image()
            st.session_state.current_index -= 1
            st.session_state.class_label = None
            st.experimental_rerun()
    with col3:
        if st.button("Next Image") and st.session_state.current_index < total_images - 1:
            annotate_image()
            st.session_state.current_index += 1
            st.session_state.class_label = None
            st.experimental_rerun()

    # Indicate annotated images
    annotated_images = [file.name for file in uploaded_files if file.name in st.session_state.annotations]
    st.write(f"Annotated images: {', '.join(annotated_images)}")

    # Save annotations and offer download button
    if st.button("Save Annotations"):
        annotations_list = [(img, cls) for img, cls in st.session_state.annotations.items()]
        save_annotations_locally(annotations_list, '.')
        df = pd.DataFrame(annotations_list, columns=['Image Name', 'Class'])
        csv_data = convert_df_to_csv(df)
        st.download_button(
            label="Download Annotations as CSV",
            data=csv_data,
            file_name="annotations.csv",
            mime="text/csv"
        )



