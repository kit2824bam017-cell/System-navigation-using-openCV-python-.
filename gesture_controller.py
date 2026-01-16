"""
Hand Gesture Recognition Controller
Handles gesture detection and mouse control
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from config import *

class HandGestureController:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Screen and camera dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        self.frame_width = CAMERA_WIDTH
        self.frame_height = CAMERA_HEIGHT
        
        # Mouse control variables
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = SMOOTHENING_FACTOR
        
        # Gesture state tracking
        self.clicking = False
        self.right_clicking = False
        self.scrolling = False
        self.dragging = False
        
        # Time tracking for debouncing
        self.last_click_time = 0
        self.last_right_click_time = 0
        self.last_scroll_time = 0
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        # Gesture recognition variables
        self.finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        self.finger_pips = [3, 6, 10, 14, 18]  # PIP joints
        
    def get_landmark_positions(self, landmarks):
        """Extract landmark positions from MediaPipe results"""
        positions = []
        for landmark in landmarks.landmark:
            x = int(landmark.x * self.frame_width)
            y = int(landmark.y * self.frame_height)
            positions.append([x, y])
        return positions
    
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1 - p2)**2)
    
    def is_finger_extended(self, positions, finger_tip, finger_pip):
        """Check if a finger is extended (up)"""
        return positions[finger_tip] < positions[finger_pip]
    
    def get_fingers_up(self, positions):
        """Determine which fingers are extended"""
        fingers_up = []
        
        # Thumb (special case - check horizontal position)
        if positions[self.finger_tips[0]] > positions[self.finger_pips]:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # Other four fingers
        for i in range(1, 5):
            if self.is_finger_extended(positions, self.finger_tips[i], self.finger_pips[i]):
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        return fingers_up
    
    def recognize_gesture(self, positions):
        """Recognize hand gestures based on finger positions"""
        if len(positions) < 21:  # Need at least 21 landmarks
            return "none", []
        
        fingers_up = self.get_fingers_up(positions)
        total_fingers = fingers_up.count(1)
        
        # Gesture classification
        if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger
            return "move", fingers_up
        elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle
            return "left_click", fingers_up
        elif fingers_up == [0, 1, 1, 1, 0]:  # Index, middle, ring
            return "right_click", fingers_up
        elif fingers_up == [1, 1, 0, 0, 0]:  # Thumb and index (pinch)
            return "drag", fingers_up
        elif total_fingers >= 4:  # Four or more fingers
            return "scroll", fingers_up
        elif total_fingers == 0:  # Closed fist
            return "stop", fingers_up
        else:
            return "none", fingers_up
    
    def smooth_coordinates(self, x, y):
        """Apply coordinate smoothening for stable mouse movement"""
        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = x, y
        
        smooth_x = self.prev_x + (x - self.prev_x) / self.smoothening
        smooth_y = self.prev_y + (y - self.prev_y) / self.smoothening
        
        self.prev_x, self.prev_y = smooth_x, smooth_y
        return int(smooth_x), int(smooth_y)
    
    def convert_to_screen_coords(self, x, y):
        """Convert camera coordinates to screen coordinates"""
        # Map camera coordinates to screen coordinates
        screen_x = np.interp(x, (CONTROL_MARGIN, self.frame_width - CONTROL_MARGIN), 
                           (0, self.screen_width))
        screen_y = np.interp(y, (CONTROL_MARGIN, self.frame_height - CONTROL_MARGIN), 
                           (0, self.screen_height))
        return screen_x, screen_y
    
    def process_gesture(self, gesture, positions, fingers_up):
        """Process recognized gestures and perform corresponding mouse actions"""
        current_time = time.time()
        
        if gesture == "move" and len(positions) > 8:
            # Mouse movement using index finger tip
            x, y = positions[8]  # Index finger tip
            screen_x, screen_y = self.convert_to_screen_coords(x, y)
            smooth_x, smooth_y = self.smooth_coordinates(screen_x, screen_y)
            
            try:
                pyautogui.moveTo(smooth_x, smooth_y)
            except:
                pass  # Ignore any pyautogui errors
        
        elif gesture == "left_click":
            if not self.clicking and (current_time - self.last_click_time) > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.click()
                    self.clicking = True
                    self.last_click_time = current_time
                    print("Left click performed")
                except:
                    pass
        
        elif gesture == "right_click":
            if not self.right_clicking and (current_time - self.last_right_click_time) > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.rightClick()
                    self.right_clicking = True
                    self.last_right_click_time = current_time
                    print("Right click performed")
                except:
                    pass
        
        elif gesture == "scroll" and len(positions) > 8:
            if (current_time - self.last_scroll_time) > SCROLL_DEBOUNCE_TIME:
                # Use middle finger for scroll direction
                y_pos = positions[12][1]  # Middle finger tip
                
                if y_pos < self.frame_height // 3:  # Upper third - scroll up
                    try:
                        pyautogui.scroll(SCROLL_SENSITIVITY)
                        print("Scroll up")
                    except:
                        pass
                elif y_pos > (2 * self.frame_height) // 3:  # Lower third - scroll down
                    try:
                        pyautogui.scroll(-SCROLL_SENSITIVITY)
                        print("Scroll down")
                    except:
                        pass
                
                self.last_scroll_time = current_time
        
        elif gesture == "drag" and len(positions) > 8:
            # Drag functionality using pinch gesture
            if not self.dragging:
                try:
                    pyautogui.mouseDown()
                    self.dragging = True
                    print("Drag started")
                except:
                    pass
        
        elif gesture == "stop" or gesture == "none":
            # Reset all states
            if self.dragging:
                try:
                    pyautogui.mouseUp()
                    self.dragging = False
                    print("Drag ended")
                except:
                    pass
            
            self.clicking = False
            self.right_clicking = False
            self.scrolling = False
    
    def draw_ui_elements(self, frame, landmarks, gesture, fingers_up):
        """Draw UI elements on the frame"""
        # Draw hand landmarks
        if landmarks:
            self.mp_drawing.draw_landmarks(
                frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        # Draw control area rectangle
        cv2.rectangle(frame, 
                     (CONTROL_MARGIN, CONTROL_MARGIN), 
                     (self.frame_width - CONTROL_MARGIN, self.frame_height - CONTROL_MARGIN),
                     COLOR_BLUE, 2)
        
        # Draw gesture information
        gesture_text = f"Gesture: {gesture.replace('_', ' ').title()}"
        cv2.putText(frame, gesture_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_GREEN, 2)
        
        # Draw finger status
        finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        for i, (name, status) in enumerate(zip(finger_names, fingers_up)):
            color = COLOR_GREEN if status else COLOR_RED
            cv2.putText(frame, f"{name}: {'Up' if status else 'Down'}", 
                       (10, 70 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw instructions
        instructions = [
            "GESTURE CONTROLS:",
            "Index finger only: Move cursor",
            "Index + Middle: Left click", 
            "Index + Middle + Ring: Right click",
            "Thumb + Index: Drag",
            "4+ fingers: Scroll (up/down area)",
            "Fist: Stop all actions",
            "",
            "Press 'q' to quit, 'r' to reset"
        ]
        
        start_y = frame.shape[0] - len(instructions) * 20 - 10
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, start_y + i * 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1)
        
        # Draw status indicators
        status_y = 200
        if self.clicking:
            cv2.putText(frame, "LEFT CLICKING", (frame.shape[1] - 200, status_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_YELLOW, 2)
        if self.right_clicking:
            cv2.putText(frame, "RIGHT CLICKING", (frame.shape - 200, status_y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_YELLOW, 2)
        if self.dragging:
            cv2.putText(frame, "DRAGGING", (frame.shape - 200, status_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_YELLOW, 2)
    
    def reset_states(self):
        """Reset all gesture states"""
        if self.dragging:
            try:
                pyautogui.mouseUp()
            except:
                pass
        
        self.clicking = False
        self.right_clicking = False
        self.scrolling = False
        self.dragging = False
        self.prev_x, self.prev_y = 0, 0
        print("All states reset")
    
    def run(self):
        """Main execution loop"""
        # Initialize camera
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Hand Gesture Mouse Control Started!")
        print("Show your hand to the camera and use gestures to control the mouse")
        print("Press 'q' to quit, 'r' to reset states")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process hand detection
                results = self.hands.process(rgb_frame)
                
                gesture = "none"
                fingers_up = [0, 0, 0, 0, 0]
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Get landmark positions
                        positions = self.get_landmark_positions(hand_landmarks)
                        
                        # Recognize gesture
                        gesture, fingers_up = self.recognize_gesture(positions)
                        
                        # Process the gesture
                        self.process_gesture(gesture, positions, fingers_up)
                        
                        # Draw UI elements
                        self.draw_ui_elements(frame, hand_landmarks, gesture, fingers_up)
                        break  # Only process first hand
                else:
                    # No hand detected, draw basic UI
                    self.draw_ui_elements(frame, None, "none", [0, 0, 0, 0, 0])
                    # Reset states when no hand is detected
                    if gesture == "none":
                        self.clicking = False
                        self.right_clicking = False
                
                # Display the frame
                cv2.imshow("Hand Gesture Mouse Control", frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.reset_states()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Cleanup
            self.reset_states()
            cap.release()
            cv2.destroyAllWindows()
            print("Camera released and windows closed")
   