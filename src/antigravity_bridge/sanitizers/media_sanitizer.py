"""
Media and Document Sanitizer for Antigravity Cloud Bridge (GEMINI.md Rule 1 Compliance).
Enforces pure #FFFFFF signature backgrounds, centered passport photos, and sub-1MB PDF compression.
"""

import os
import sys
from PIL import Image, ImageOps

def sanitize_signature(input_path, output_path=None, max_size_kb=100, max_dim=600):
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_sanitized.jpg"

    img = Image.open(input_path).convert("RGBA")
    gray = img.convert("L")
    inverted = ImageOps.invert(gray)
    
    threshold = 200
    mask = inverted.point(lambda p: 255 if p > (255 - threshold) else 0)
    bbox = mask.getbbox()

    if bbox:
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        pad_x = int(width * 0.05)
        pad_y = int(height * 0.05)

        img_w, img_h = img.size
        crop_box = (
            max(0, bbox[0] - pad_x),
            max(0, bbox[1] - pad_y),
            min(img_w, bbox[2] + pad_x),
            min(img_h, bbox[3] + pad_y)
        )
        img = img.crop(crop_box)

    rgb_img = img.convert("RGB")
    pixels = rgb_img.load()
    w, h = rgb_img.size

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if r > 185 and g > 185 and b > 185:
                pixels[x, y] = (255, 255, 255)

    if max(w, h) > max_dim:
        rgb_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    quality = 90
    rgb_img.save(output_path, "JPEG", quality=quality, optimize=True)
    
    while os.path.getsize(output_path) > max_size_kb * 1024 and quality > 30:
        quality -= 10
        rgb_img.save(output_path, "JPEG", quality=quality, optimize=True)

    return output_path

def sanitize_photo(input_path, output_path=None, max_size_kb=200, max_dim=600):
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_sanitized.jpg"

    img = Image.open(input_path).convert("RGB")
    w, h = img.size

    target_aspect = 3.0 / 4.0
    current_aspect = w / float(h)

    if current_aspect > target_aspect:
        new_w = int(h * target_aspect)
        offset = (w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, h))
    elif current_aspect < target_aspect:
        new_h = int(w / target_aspect)
        offset = (h - new_h) // 2
        img = img.crop((0, offset, w, offset + new_h))

    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    quality = 90
    img.save(output_path, "JPEG", quality=quality, optimize=True)

    while os.path.getsize(output_path) > max_size_kb * 1024 and quality > 40:
        quality -= 10
        img.save(output_path, "JPEG", quality=quality, optimize=True)

    return output_path

def sanitize_pdf(input_path, output_path=None, max_size_bytes=1048576):
    import pymupdf

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_under_1MB.pdf"

    initial_size = os.path.getsize(input_path)
    if initial_size <= max_size_bytes:
        return input_path

    doc = pymupdf.open(input_path)
    doc.save(output_path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    doc.close()

    if os.path.getsize(output_path) <= max_size_bytes:
        return output_path

    # Second pass: re-rasterize pages at 180 DPI
    doc = pymupdf.open(input_path)
    new_doc = pymupdf.open()

    for page in doc:
        pix = page.get_pixmap(dpi=180)
        img_bytes = pix.tobytes("jpeg", jpg_quality=80)
        img_doc = pymupdf.open("jpeg", img_bytes)
        pdf_bytes = img_doc.convert_to_pdf()
        page_pdf = pymupdf.open("pdf", pdf_bytes)
        new_doc.insert_pdf(page_pdf)
        img_doc.close()
        page_pdf.close()

    new_doc.save(output_path, garbage=4, deflate=True)
    new_doc.close()
    doc.close()
    return output_path
