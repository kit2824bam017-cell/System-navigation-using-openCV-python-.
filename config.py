"""
Configuration settings for Hand Gesture Mouse Control
"""

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_INDEX = 0

# Hand detection settings
MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.8
MAX_NUM_HANDS = 1

# Mouse control settings
SMOOTHENING_FACTOR = 7
CLICK_THRESHOLD = 30
SCROLL_SENSITIVITY = 3

# Gesture debounce settings (in seconds)
CLICK_DEBOUNCE_TIME = 0.3
SCROLL_DEBOUNCE_TIME = 0.1

# Control area margins (pixels from edge)
CONTROL_MARGIN = 100

# Colors (BGR format)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
