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

# Optimize Instagram and X social media icons (PNG)
png_files = ["instagram.png", "x-rafting-logo.png"]

for filename in png_files:
    image_path = images_folder / filename

    if not image_path.exists():
        print(f"File not found: {filename}")
        continue

    try:
        with Image.open(image_path) as original:
            # Preserve transparency
            image = original.convert("RGBA")

            # Resize icons to a reasonable size
            image.thumbnail((256, 256), Image.Resampling.LANCZOS)

            output = io.BytesIO()
            image.save(output, format="PNG", optimize=True)

            # Reduce dimensions further if still above 125 KB
            while output.tell() > 125 * 1024 and max(image.size) > 32:
                new_size = (
                    max(32, int(image.width * 0.85)),
                    max(32, int(image.height * 0.85))
                )

                image = image.resize(
                    new_size,
                    Image.Resampling.LANCZOS
                )

                output = io.BytesIO()
                image.save(output, format="PNG", optimize=True)

            # Give the files descriptive names
            if filename == "instagram.png":
                new_name = "instagram-social-media-icon.png"
            else:
                new_name = "x-social-media-icon.png"

            new_path = output_folder / new_name
            new_path.write_bytes(output.getvalue())

            print(
                f"{filename}: "
                f"{image_path.stat().st_size / 1024:.1f} KB -> "
                f"{new_path.stat().st_size / 1024:.1f} KB"
            )

            if new_path.stat().st_size <= 125 * 1024:
                print("SUCCESS: Below 125 KB!")
            else:
                print("WARNING: Still above 125 KB.")

    except Exception as error:
        print(f"Could not process {filename}: {error}")

print("Finished! Check the optimized folder.")
