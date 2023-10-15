from PIL import Image
import os
import time
from setrepcli import *
from constants import *
import sys

class WmPos:
    CENTERED = 'centered'
    TOP_LEFT = 'top-left'
    TOP_CENTER = 'top-center'
    TOP_RIGHT = 'top-right'
    BOTTOM_LEFT = 'bottom-left'
    BOTTOM_CENTER = 'bottom-center'
    BOTTOM_RIGHT = 'bottom-right'


dr = SetRepClient(SETREP_BASE_URL, os.environ.get('AI_API_USER_KEY'), os.environ.get('AI_API_TOKEN'), APP_CODE)

def get_full_filepath(file_name):
# Check if the file name contains a path
    if os.path.dirname(file_name) == "":
    # If no path, return the filename with the script's directory path
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    else:
    # If path, return only the filename
        return file_name

def add_watermark(
    original_image_path: str, 
    watermark_image_path: str, 
    watermark_opacity: float = 1, 
    watermark_position: str = WmPos.BOTTOM_RIGHT, 
    watermark_scaling_percentage: float = 5, 
    watermark_border_percentage: float = 2
):
# Load original image
    original = Image.open(original_image_path).convert("RGBA")
    original_width, original_height = original.size
# Load watermark image
    watermark = Image.open(watermark_image_path).convert("RGBA")
# Resize the watermark
    new_watermark_height = int(original_height * (watermark_scaling_percentage / 100))
    aspect_ratio = watermark.width / watermark.height
    new_watermark_width = int(new_watermark_height * aspect_ratio)
    watermark = watermark.resize((new_watermark_width, new_watermark_height))
# Adjust watermark opacity
    watermark = Image.blend(Image.new("RGBA", watermark.size), watermark, watermark_opacity)
# Calculate watermark position
    min_dimension = min(original_width, original_height)
    border_distance = int(min_dimension * (watermark_border_percentage / 100))
    if watermark_position == "centered":
        position = ((original_width - new_watermark_width) // 2, (original_height - new_watermark_height) // 2)
    elif watermark_position == "top-left":
        position = (border_distance, border_distance)
    elif watermark_position == "top-center":
        position = ((original_width - new_watermark_width) // 2, border_distance)
    elif watermark_position == "top-right":
        position = (original_width - new_watermark_width - border_distance, border_distance)
    elif watermark_position == "bottom-left":
        position = (border_distance, original_height - new_watermark_height - border_distance)
    elif watermark_position == "bottom-center":
        position = ((original_width - new_watermark_width) // 2, original_height - new_watermark_height - border_distance)
    elif watermark_position == "bottom-right":
        position = (original_width - new_watermark_width - border_distance, original_height - new_watermark_height - border_distance)
    else:
        raise ValueError("Invalid watermark_position value")
# Create a new image with the same size and mode as the original image
    combined = Image.new("RGBA", original.size)
# Paste the original image onto the combined image
    combined.paste(original, (0,0), original)
# Paste the watermark onto the combined image
    combined.paste(watermark, position, watermark)
# Save the resulting image
    original_name, original_extension = os.path.splitext(os.path.basename(original_image_path))
    timestamp = time.strftime("%Y%m%d%H%M%S")
    new_image_name = f"{original_name}_wm_{timestamp}{original_extension}"
    new_image_path = os.path.join(os.path.dirname(original_image_path), new_image_name)
    combined.save(new_image_path, format=original.format)
    return new_image_path

def get_input_data():
    original_image_path: str = None
    while not original_image_path:
        original_image_path = input("Enter the path to the original image ('q' to exit): ").strip()
        if original_image_path.lower() == 'q': 
            exit()    
        if original_image_path:
            original_image_path = get_full_filepath(original_image_path)
        if not os.path.exists(original_image_path):
            original_image_path = None
            print("[Error] Image file does not exists. Retry...")
    watermark_image_path: str = None
    while not watermark_image_path:
        watermark_image_path = input("Enter the path to the watermark image ('q' to exit): ").strip()    
        if watermark_image_path.lower() == 'q': 
            exit()    
        if watermark_image_path:
            watermark_image_path = get_full_filepath(watermark_image_path)
        if not os.path.exists(watermark_image_path):
            watermark_image_path = None
            print("[Error] Image file does not exists. Retry...")
    dr.set_key_value('main', 'watermark_image_path', watermark_image_path)
    watermark_opacity = None
    while not watermark_opacity:
        try:
            watermark_opacity = input("Enter the watermark opacity (0-1, optional): ").strip()
            if watermark_opacity:
                watermark_opacity = float(watermark_opacity)
            else:
                watermark_opacity = DFT_WATERMARK_OPACITY
            if watermark_opacity < 0 or watermark_opacity > 1:
                watermark_opacity = None
                print("[Error] Opacity must be a float between 0 and 1. Retry...")
        except ValueError:
            watermark_opacity = None
            print("[Error] Invalid numerical input. OMust be number. Retry...")
    dr.set_key_value('main', 'watermark_opacity', watermark_opacity)
    watermark_position = None
    valid_positions = ["centered", "top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"]
    while not watermark_position:
        watermark_position = input("Enter the watermark position (optional) (centered, top-left, top-center, top-right, bottom-left, bottom-center, bottom-right): ").strip().lower()
        if not watermark_position: 
            watermark_position = DFT_WATERMARK_POSITION
        if watermark_position not in valid_positions:
            watermark_position = None
            print(f"[Error] Invalid watermark position. Retry hoosing from {', '.join(valid_positions)}...")
    dr.set_key_value('main', 'watermark_position', watermark_position)
    watermark_scaling_percentage = None
    while not watermark_scaling_percentage:
        try:
            watermark_scaling_percentage = input("Enter the watermark scaling percentage (optional): ").strip()
            if watermark_scaling_percentage:
                watermark_scaling_percentage = float(watermark_scaling_percentage)
            else:
                watermark_scaling_percentage = DFT_WATERMARK_SCALING_PERCENTAGE
            if watermark_scaling_percentage <= 0:
                watermark_scaling_percentage = None
                print("[Error] Watermark scaling percentage must be a positive number. Retry...")
        except ValueError:
            watermark_scaling_percentage = None
            print("[Error] Invalid numerical input. OMust be number. Retry...")
    dr.set_key_value('main', 'watermark_scaling_percentage', watermark_scaling_percentage)
    watermark_border_percentage = None
    while not watermark_border_percentage:
        try:
            watermark_border_percentage = input("Enter the watermark border percentage (optional): ").strip()
            if watermark_border_percentage:
                watermark_border_percentage = float(watermark_border_percentage)
            else:
                watermark_border_percentage = DFT_WATERMARK_BORDER_PERCENTAGE
            if watermark_border_percentage < 0:
                watermark_border_percentage = None
                print("[Error] Watermark border percentage must be a non-negative number.")
        except ValueError:
            watermark_border_percentage = None
            print("[Error] Invalid numerical input. OMust be number. Retry...")
    dr.set_key_value('main', 'watermark_border_percentage', watermark_border_percentage)
    return original_image_path, watermark_image_path, watermark_opacity, watermark_position, watermark_scaling_percentage, watermark_border_percentage


if __name__ == '__main__':

    dft_watermark_image_path: str = dr.get_key_value('main', 'watermark_image_path')
    if dft_watermark_image_path and (not os.path.exists(dft_watermark_image_path)):
        dft_watermark_image_path = None

    original_image_path: str = None
    if dft_watermark_image_path:
        if len(sys.argv) > 1:
            try:
                original_image_path = get_full_filepath(sys.argv[1].strip())
                if original_image_path and (not os.path.exists(original_image_path)):
                    original_image_path = None
            except:
                original_image_path = None
            while not original_image_path:
                original_image_path = input("Enter the path to the original image ('q' to exit): ").strip()
                if original_image_path.lower() == 'q': 
                    exit()    
                if original_image_path:
                    original_image_path = get_full_filepath(original_image_path)
                if not os.path.exists(original_image_path):
                    original_image_path = None
                    print("[Error] Image file does not exists. Retry...")

    res: str = None

    if original_image_path:
        watermark_opacity: float = None 
        watermark_opacity = dr.get_key_value('main', 'watermark_opacity')
        if watermark_opacity:
            watermark_opacity = float(watermark_opacity)
        else:
            watermark_opacity = DFT_WATERMARK_OPACITY
        watermark_position: str = None
        watermark_position = dr.get_key_value('main', 'watermark_position')
        if not watermark_position:
            watermark_position = DFT_WATERMARK_POSITION
        watermark_scaling_percentage: float = None
        watermark_scaling_percentage = dr.get_key_value('main', 'watermark_scaling_percentage')
        if watermark_scaling_percentage:
            watermark_scaling_percentage = float(watermark_scaling_percentage)
        else:
            watermark_scaling_percentage = DFT_WATERMARK_SCALING_PERCENTAGE
        watermark_border_percentage: float = None
        watermark_border_percentage = dr.get_key_value('main', 'watermark_border_percentage')
        if watermark_border_percentage:
            watermark_border_percentage = float(watermark_border_percentage)
        else:
            watermark_border_percentage = DFT_WATERMARK_BORDER_PERCENTAGE
        res = add_watermark(original_image_path, dft_watermark_image_path, watermark_opacity, watermark_position, watermark_scaling_percentage, watermark_border_percentage)
    else:
        input_data = get_input_data()    
        if input_data is not None:
            res = add_watermark(*input_data)
        else:
            print("Invalid input. Please check the values and try again.")
    
    if res:
        print(f"Watermark added successfully in {res}")
