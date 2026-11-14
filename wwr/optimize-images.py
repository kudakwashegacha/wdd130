from pathlib import Path
from PIL import Image
import io

# Find the rafting images folder
project_folder = Path(__file__).parent
images_folder = project_folder / "images"

# Save optimized copies in a separate folder
output_folder = images_folder / "optimized"
output_folder.mkdir(exist_ok=True)

# Image formats to process (photographs only)
extensions = {".jpg", ".jpeg", ".jfif"}

for image_path in images_folder.iterdir():

    if image_path.suffix.lower() not in extensions:
        continue

    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image.thumbnail((1200, 1200))

            quality = 85
            output = io.BytesIO()

            while quality >= 20:
                output = io.BytesIO()
                image.save(
                    output,
                    format="JPEG",
                    quality=quality,
                    optimize=True
                )

                if output.tell() <= 125 * 1024:
                    break

                quality -= 5

            # If needed, reduce dimensions further
            while output.tell() > 125 * 1024:
                image.thumbnail(
                    (int(image.width * 0.85), int(image.height * 0.85))
                )
                output = io.BytesIO()
                image.save(output, format="JPEG", quality=20, optimize=True)

            new_path = output_folder / (image_path.stem + "_optimized.jpg")
            new_path.write_bytes(output.getvalue())

            print(
                f"{image_path.name}: "
                f"{image_path.stat().st_size / 1024:.1f} KB -> "
                f"{new_path.stat().st_size / 1024:.1f} KB"
            )

    except Exception as error:
        print(f"Could not process {image_path.name}: {error}")

print("Finished! Check the optimized folder.")
