# Setup Guide for Real-Time Drowsiness Detection System

## Quick Start

### 1. Install Dependencies

Run this command in the project directory:

```bash
venv\Scripts\pip install -r requirements.txt
```

### 2. Run the Application

**Option A: Using OpenCV Cascade Classifiers (No dlib required)**
```bash
venv\Scripts\python.exe drowsiness_yawn_nolibdlib.py
```

**Option B: Using dlib (Advanced, requires CMake)**
```bash
venv\Scripts\python.exe drowsiness_yawn.py
```

### 3. Using the Application

- The application opens your webcam and displays a video stream
- **Press 'q'** to quit the application
- The system will:
  - Detect your eyes and check if they're closed
  - Detect if you're yawning
  - Play an alarm sound if drowsiness or yawning is detected

## Requirements

The project uses the following packages:

- **opencv-python** - Computer vision library for image processing
- **imutils** - Helper functions for OpenCV
- **numpy** - Numerical computing
- **scipy** - Scientific computing
- **playsound** - For playing alarm sounds
- **cmake** - Required for building dlib (optional)
- **dlib** - Advanced face landmark detection (optional)

## File Descriptions

- `drowsiness_yawn.py` - Original implementation using dlib for detailed face landmarks (requires dlib installation)
- `drowsiness_yawn_nolibdlib.py` - Simplified implementation using only OpenCV cascade classifiers (recommended)
- `haarcascade_frontalface_default.xml` - Pre-trained face detection cascade classifier
- `shape_predictor_68_face_landmarks.dat` - Pre-trained dlib model for facial landmarks (for drowsiness_yawn.py)
- `Alert.wav` - Audio alarm file for alerts
- `requirements.txt` - Python package dependencies

## Troubleshooting

### Issue: Camera not detected
- Check if your webcam is connected and working
- Try with different webcam index: `python drowsiness_yawn_nolibdlib.py -w 0` (default)
- Or use: `python drowsiness_yawn_nolibdlib.py -w 1` for a different camera

### Issue: dlib installation fails
- Install CMake first: `pip install cmake`
- Make sure you have a C++ compiler installed (Visual Studio or MinGW on Windows)
- Use the non-dlib version instead: `drowsiness_yawn_nolibdlib.py`

### Issue: No sound when alarm triggers
- Check if `Alert.wav` file exists in the project directory
- Check your system volume settings
- Check if audio permissions are enabled

## Command Line Arguments

Both scripts support the following arguments:

```bash
-w, --webcam    : Webcam index (default: 0)
-a, --alarm     : Path to alarm WAV file (default: Alert.wav)
```

Example:
```bash
python drowsiness_yawn_nolibdlib.py -w 1 -a Alert.wav
```

## System Requirements

- Python 3.7 or higher
- Windows 7+, Linux, or macOS
- Webcam/Camera connected to your computer
- Minimum 2GB RAM
- Multi-core processor recommended for real-time processing

## Performance Tips

- Run in a well-lit environment for better face detection
- Keep your face within 1-2 feet of the camera
- Avoid wearing sunglasses or hats that might interfere with detection
- The non-dlib version (drowsiness_yawn_nolibdlib.py) is faster and lighter

## License

This project is open source and available under the MIT License.
