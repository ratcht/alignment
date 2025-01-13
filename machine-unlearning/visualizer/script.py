from PIL import Image
import numpy as np

# Create a simple 28x28 test image (a vertical line)
test_image = np.zeros((28, 28), dtype=np.uint8)
test_image[:, 14] = 255  # Draw a vertical line in the middle
Image.fromarray(test_image).save('test_digit.png')