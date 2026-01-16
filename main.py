"""
Main entry point for Hand Gesture Mouse Control
"""


import sys
import os
from gesture_controller import HandGestureController

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import cv2
        import mediapipe
        import pyautogui
        import numpy
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install requirements using: pip install -r requirements.txt")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("Hand Gesture Mouse Control System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check camera availability
    import cv2
    test_cap = cv2.VideoCapture(0)
    if not test_cap.isOpened():
        print("✗ Camera not accessible. Please check your camera connection.")
        sys.exit(1)
    test_cap.release()
    print("✓ Camera is accessible")
    
    # Display usage instructions
    print("\nGesture Controls:")
    print("• Index finger only: Move mouse cursor")
    print("• Index + Middle finger: Left click")
    print("• Index + Middle + Ring finger: Right click") 
    print("• Thumb + Index finger: Drag")
    print("• 4+ fingers extended: Scroll mode")
    print("• Closed fist: Stop all actions")
    print("\nKeyboard Controls:")
    print("• Press 'q' to quit")
    print("• Press 'r' to reset all states")
    print("\n" + "=" * 50)
    
    input("Press Enter to start the gesture control system...")
    
    try:
        # Initialize and run the gesture controller
        controller = HandGestureController()
        controller.run()
    except Exception as e:
        print(f"Error running gesture controller: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
