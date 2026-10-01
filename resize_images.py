import os
from PIL import Image

IMAGE_DIR = os.path.join("assets", "images")
MAX_WIDTH = 500

for filename in os.listdir(IMAGE_DIR):
    if filename.lower().endswith(".png"):
        filepath = os.path.join(IMAGE_DIR, filename)
        try:
            with Image.open(filepath) as img:
                if img.width > MAX_WIDTH:
                    w_percent = MAX_WIDTH / float(img.width)
                    new_height = int(float(img.height) * float(w_percent))
                    resized_img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(filepath, format="PNG", optimize=True)
                    print(f"Da giam: {filename}")
        except Exception as e:
            print(f"Loi: {filename} - {e}")

print("Hoan tat!")