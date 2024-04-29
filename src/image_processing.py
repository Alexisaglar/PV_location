import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image from file
file_path = "data/image.png"
image = cv2.imread(file_path, cv2.IMREAD_COLOR)

# Convert image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use Canny edge detection
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# Detect points that form a line
lines = cv2.HoughLinesP(
    edges, 1, np.pi / 180, threshold=20, minLineLength=40, maxLineGap=6
)


# Function to calculate the angle of a line
def calculate_angle(x1, y1, x2, y2):
    angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
    # Adjusting angle to be relative to north (vertical in the image)
    if angle < 0:
        angle += 180
    return angle


# Function to draw the angle on the image
def draw_angle(image, angle, position):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (255, 255, 255)  # Blue color in BGR
    line_type = 2

    cv2.putText(
        image, str(int(angle)), position, font, font_scale, font_color, line_type
    )


# Draw lines on the image, calculate their angles, and print them
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
    angle = calculate_angle(x1, y1, x2, y2)
    midpoint = ((x1 + x2) // 2, (y1 + y2) // 2)
    draw_angle(image, angle, midpoint)

# Convert to RGB for visualization
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Show the result with matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(image_rgb)
plt.axis("off")  # Turn off axis numbers and ticks
plt.title("Image with Detected Lines and Their Angles")
plt.savefig("data/image_processed")
plt.show()
