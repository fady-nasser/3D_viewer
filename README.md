# Medical 3D Visualization System

A Unity-based medical visualization application for interactive 3D exploration of human anatomical systems using advanced rendering techniques.

## Overview

This application provides medical professionals and students with an immersive 3D visualization tool for exploring human anatomy. It combines multiple rendering techniques and navigation modes to offer comprehensive anatomical understanding.

## Demo Video
https://drive.google.com/file/d/10PocC6wu4w2pUkZ2jirWeLdnkwD8KSph/view?usp=sharing

## ScreenShots
![Image1](Screenshots/Screenshot%202025-11-14%20185730.png)
![Image2](Screenshots/Screenshot%202025-11-14%20185752.png)
![Image3](Screenshots/Screenshot%202025-11-14%20185819.png)
![Image4](Screenshots/Screenshot%202025-11-14%20190003.png)
![Image5](Screenshots/Screenshot%202025-11-14%20190104.png)
![Image6](Screenshots/Screenshot%202025-11-14%20190025.png)

## Anatomical Systems

The application supports visualization of four major anatomical systems:

- **Cardiovascular System** - Heart and blood vessels with flow visualization
- **Musculoskeletal System** - Bones, muscles, and connective tissues
- **Dental System** - Teeth and oral structures
- **Nervous System** - Brain, spinal cord, and nerve pathways

## Visualization Modes

### 1. Surface Rendering
Traditional 3D model rendering displaying the external surfaces of anatomical structures.

### 2. Clipping Planes
Interactive cross-sectional visualization using three orthogonal planes:
- **Sagittal Plane** - Divides left and right
- **Coronal Plane** - Divides front and back
- **Axial Plane** - Divides top and bottom

Each plane can be moved independently using dedicated sliders to reveal internal structures.

### 3. Curved NPR (Non-Photorealistic Rendering)
Stylized rendering technique for enhanced visualization and feature emphasis.

## Navigation Modes

### 1. Fly-Through Navigation
Free-form camera movement allowing users to navigate around and through anatomical structures.

### 2. Focus Navigation
Camera control centered on specific anatomical features for detailed examination.

### 3. Moving Stuff Navigation (Cardiovascular Only)
Unique blood flow simulation where the camera moves along with red blood cells through the cardiovascular system, providing an immersive journey through the heart and vessels.

## Technical Architecture

### Core Scripts

#### `Clipping.cs`
Manages the Clipping Planes visualization mode:
- Controls three orthogonal planes (Sagittal, Coronal, Axial)
- Updates plane textures based on slider input
- Synchronizes plane position with corresponding slice images

#### `runPython.cs`
Handles Python script execution from within Unity:
- Opens command prompt
- Executes specified Python files
- Triggered by UI button presses

### Python Pipeline

#### `generateSlices.py`
Preprocesses medical imaging data:
- **Input**: NIfTI (`.nii`) medical image files
- **Output**: PNG slice images organized by viewing plane
- **Process**:
  1. Reads NIfTI file
  2. Extracts slices for each anatomical plane
  3. Organizes output into three folders:
     - `Axial/` - Horizontal slices
     - `Sagittal/` - Left-right slices
     - `Coronal/` - Front-back slices
  4. Saves each slice as a PNG image

#### Curved NPR Python Script
Handles non-photorealistic rendering calculations and processing.

## Data Pipeline

```
NIfTI File (.nii)
    ↓
generateSlices.py
    ↓
├── Axial/*.png
├── Sagittal/*.png
└── Coronal/*.png
    ↓
Unity Clipping Planes
```

## How Clipping Planes Work

1. Medical data is preprocessed using `generateSlices.py` to generate PNG slices
2. Slices are organized into three folders by anatomical plane
3. In Unity, three planes are positioned orthogonally
4. Each plane has an associated slider in the UI
5. Moving a slider:
   - Updates the plane's position in 3D space
   - Changes the plane's texture to the corresponding slice PNG
   - Provides real-time cross-sectional views

## Requirements

### Unity
- Unity 2020.3 LTS or higher (recommended)

### Python
- Python 3.x
- Required libraries:
  - nibabel (for NIfTI file handling)
  - numpy
  - PIL/Pillow (for image processing)

## Setup

1. Clone the repository
2. Open the project in Unity
3. Ensure Python is installed and accessible from command line
4. Install required Python dependencies:
   ```bash
   pip install nibabel numpy pillow
   ```
5. Place NIfTI files in the appropriate input directory
6. Run `generateSlices.py` to preprocess medical data
7. Open the desired scene in Unity and press Play

## Project Structure

```
Assets/
├── Scripts/
│   ├── Clipping.cs
│   ├── runPython.cs
│   └── [Other navigation and rendering scripts]
├── Scenes/
│   ├── ClippingPlanes.unity
│   ├── [Other visualization scenes]
└── Data/
    ├── Axial/
    ├── Sagittal/
    └── Coronal/

Python/
├── generateSlices.py
└── Curved_MPR.py
```

## Usage

1. Launch the application
2. Select an anatomical system (Cardiovascular, Musculoskeletal, Dental, or Nervous)
3. Choose a visualization mode (Surface Rendering, Clipping Planes, or Curved NPR)
4. Select a navigation mode appropriate for your exploration needs
5. For Clipping Planes:
   - Use the three sliders to move each plane
   - Observe how internal structures are revealed at each cross-section

## Features

- Multi-system anatomical visualization
- Real-time cross-sectional imaging
- Interactive plane manipulation
- Blood flow simulation (cardiovascular system)
- Multiple rendering techniques
- Intuitive navigation controls

## Future Enhancements

- Additional anatomical systems
- VR/AR support
- Annotation and measurement tools
- Multi-user collaboration features
- Enhanced NPR styles
