# -*- coding: utf-8 -*-
"""super_resolution.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1h4BYWZht8rhiYf47G8FWwyfdyJH7hm8u
"""

import cv2
from cv2 import dnn_superres
import os

# Function to validate paths
def validate_path(path, is_directory=False):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")
    if is_directory and not os.path.isdir(path):
        raise NotADirectoryError(f"Expected a directory, but got a file: {path}")
    return path

# Initialize super-resolution object
sr = dnn_superres.DnnSuperResImpl_create()

# Specify your FSRCNN model path and validate it
model_path = '/content/drive/MyDrive/NatureNexis_SuperRes/FSRCNN_x4.pb'
validate_path(model_path)
sr.readModel(model_path)

# Set the model and scale
sr.setModel('fsrcnn', 4)

# Enable CUDA for acceleration (if supported, fallback to CPU otherwise)
try:
    sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    print("CUDA acceleration enabled.")
except Exception as e:
    print(f"CUDA not available or an error occurred: {e}. Falling back to CPU.")
    sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Specify dataset and output folder
dataset_path = '/content/drive/MyDrive/NatureNexis_SuperRes/dataset'
output_folder = '/content/drive/MyDrive/NatureNexis_SuperRes/output_dataset'
validate_path(dataset_path, is_directory=True)
os.makedirs(output_folder, exist_ok=True)

# Supported image extensions
supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff','.webp')

# Recursive function to process images
def process_images_in_directory(directory, sr, output_folder):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if not file_name.lower().endswith(supported_extensions):
                print(f"Skipping non-image file: {file_name}")
                continue

            # Full path to the image
            image_path = os.path.join(root, file_name)

            # Load the image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not load image: {file_name}")
                continue

            try:
                # Upsample the image using the FSRCNN model
                upscaled_image = sr.upsample(image)

                # Save the upscaled image
                relative_path = os.path.relpath(image_path, dataset_path)  # Maintain subdirectory structure
                upscaled_image_path = os.path.join(output_folder, relative_path)
                os.makedirs(os.path.dirname(upscaled_image_path), exist_ok=True)
                cv2.imwrite(upscaled_image_path, upscaled_image)

                print(f"Super-resolution applied to {file_name}. Saved as {upscaled_image_path}.")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

# Process images recursively
process_images_in_directory(dataset_path, sr, output_folder)

print("Processing complete! Upscaled images are saved in the output folder.")

import cv2
import numpy as np
import os
from torchvision import transforms
from PIL import Image

def enhance_images_batch(source_dir, output_dir="enhanced_outputs", upscale_factor=4, apply_clahe=True):
    """
    Enhance a batch of images using super-resolution and optional CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Parameters:
        source_dir (str): Path to the directory containing input images.
        output_dir (str): Directory to save the enhanced images.
        upscale_factor (int): Factor by which to upscale the images.
        apply_clahe (bool): Whether to apply CLAHE for contrast enhancement.
    """
    # Validate source directory
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(f"Source path is not a directory: {source_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Supported image formats
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')

    # Load SRGAN or ESRGAN pre-trained model (can replace with a specific model for better quality)
    print("Loading super-resolution model...")
    sr_model = cv2.dnn_superres.DnnSuperResImpl_create()
    sr_model.readModel("/content/drive/MyDrive/NatureNexis_SuperRes/EDSR_x4.pb")  # Replace with your preferred model path
    sr_model.setModel("edsr", upscale_factor)

    # Process each image in the directory
    for file_name in os.listdir(source_dir):
        if not file_name.lower().endswith(supported_extensions):
            print(f"Skipping non-image file: {file_name}")
            continue

        # Full path to the image
        image_path = os.path.join(source_dir, file_name)
        print(f"Processing image: {image_path}")

        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read the image at {image_path}")
            continue

        try:
            # Apply super-resolution
            enhanced_image = sr_model.upsample(image)

            # Apply CLAHE for contrast enhancement (optional)
            if apply_clahe:
                lab = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)

                # Apply CLAHE to L-channel
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)

                # Merge the CLAHE-enhanced L-channel back with A and B channels
                enhanced_image = cv2.merge((cl, a, b))
                enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_LAB2BGR)

            # Save the enhanced image
            output_path = os.path.join(output_dir, file_name)
            cv2.imwrite(output_path, enhanced_image)
            print(f"Saved enhanced image to: {output_path}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

def display_enhanced_images(output_dir):
    """
    Display enhanced images from the output directory.

    Parameters:
        output_dir (str): Directory containing enhanced images.
    """
    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        print(f"No enhanced images found in the directory: {output_dir}")
        return

    # Display each enhanced image
    for file_name in os.listdir(output_dir):
        image_path = os.path.join(output_dir, file_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read the image at {image_path}")
            continue

        # Convert BGR (OpenCV format) to RGB (Matplotlib format)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 8))
        plt.imshow(image_rgb)
        plt.axis("off")
        plt.title(f"Enhanced Image: {file_name}")
        plt.show()

if __name__ == "__main__":
    # Example usage
    input_directory = "/content/drive/MyDrive/NatureNexis_SuperRes/dataset"  # Replace with your dataset path
    output_directory = "/content/drive/MyDrive/NatureNexis_SuperRes/output_dataset"  # Replace with your desired output path

    # Enhance images in the dataset
    enhance_images_batch(input_directory, output_dir=output_directory, upscale_factor=4, apply_clahe=True)

    # Display enhanced results
    display_enhanced_images(output_directory)

# Install dependencies
!pip install ultralytics opencv-python matplotlib

import cv2
from ultralytics import YOLO
import os
import matplotlib.pyplot as plt

def detect_animals_batch(source_dir, output_dir="outputs", conf_threshold=0.3, device="cuda"):
    """
    Perform animal detection on a batch of images using YOLOv8.

    Parameters:
        source_dir (str): Path to the directory containing input images.
        output_dir (str): Directory to save the output images.
        conf_threshold (float): Confidence threshold for detection.
        device (str): Device to run the YOLO model ('cuda' or 'cpu').
    """
    # Validate source directory
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(f"Source path is not a directory: {source_dir}")

    # Load YOLOv8 model
    try:
        model = YOLO("yolov8n.pt")  # Replace with custom weights if available
        print(f"YOLO model loaded.")
    except Exception as e:
        raise RuntimeError(f"Error loading YOLO model: {e}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Supported image formats
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')

    # Process each image in the directory
    for file_name in os.listdir(source_dir):
        if not file_name.lower().endswith(supported_extensions):
            print(f"Skipping non-image file: {file_name}")
            continue

        # Full path to the image
        image_path = os.path.join(source_dir, file_name)
        print(f"Processing image: {image_path}")

        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read the image at {image_path}")
            continue

        try:
            # Perform detection with the specified device
            results = model.predict(source=image_path, conf=conf_threshold, device=device, save=False, show=False)

            # Debugging: Print detection results
            print(f"Detections for {file_name}:")
            print(results[0].boxes)  # Print bounding boxes for debugging

            # Extract the annotated image
            annotated_image = results[0].plot()

            # Save the output image
            output_path = os.path.join(output_dir, file_name)
            cv2.imwrite(output_path, annotated_image)
            print(f"Saved annotated image to: {output_path}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

def display_results(output_dir):
    """
    Display results of the detection from the output directory.

    Parameters:
        output_dir (str): Directory containing annotated images.
    """
    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        print(f"No results found in the directory: {output_dir}")
        return

    # Display each image in the output directory
    for file_name in os.listdir(output_dir):
        image_path = os.path.join(output_dir, file_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read the image at {image_path}")
            continue

        # Convert BGR (OpenCV format) to RGB (Matplotlib format)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 8))
        plt.imshow(image_rgb)
        plt.axis("off")
        plt.title(f"Detected Animals: {file_name}")
        plt.show()

if __name__ == "__main__":
    # Example usage
    input_directory = "/content/drive/MyDrive/NatureNexis_SuperRes/output_dataset"  # Replace with your dataset path
    output_directory = "/content/drive/MyDrive/NatureNexis_SuperRes/detected_dataset"  # Replace with your desired output path

    # Detect animals in the dataset
    detect_animals_batch(input_directory, output_dir=output_directory, conf_threshold=0.3, device="cuda")

    # Display results
    display_results(output_directory)