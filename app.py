import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2
import io

# === Image Processing Function (without vignette) ===
def composite_with_shadow_and_enhance(person_img, bg_img):
    # === Step 1: Remove Background ===
    input_data = person_img.read()
    output_data = remove(input_data)
    person = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # === Step 2: Load Background ===
    bg = Image.open(bg_img).convert("RGBA")
    bg_width, bg_height = bg.size

    # === Step 3: Resize Person ===
    p_width, p_height = person.size
    target_h = int(bg_height * 0.6)
    scale = target_h / p_height
    person = person.resize((int(p_width * scale), target_h), Image.LANCZOS)

    # === Step 4: Brightness Matching ===
    person = ImageEnhance.Brightness(person).enhance(0.98)

    # === Step 5: Create Shadow ===
    alpha = person.split()[3]
    shadow = Image.new("RGBA", person.size, (0, 0, 0, 120))
    shadow.putalpha(alpha)
    blur_radius = int(person.height * 0.08)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # === Step 6: Positioning ===
    offset_x = int(person.width * 0.06)
    offset_y = int(person.height * 0.06)
    px = (bg_width - person.width) // 2
    py = bg_height - person.height
    temp_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    temp_layer.paste(shadow, (px + offset_x, py + offset_y), shadow)
    temp_layer.paste(person, (px, py), person)

    # === Step 7: Composite ===
    composite = Image.alpha_composite(bg, temp_layer)

    # === Step 8: Enhance ===
    comp_rgb = composite.convert("RGB")
    img_np = np.array(comp_rgb)

    # Highlights/Shadows (gamma)
    def adjust_gamma(img, gamma=0.95):
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(img, table)
    img_np = adjust_gamma(img_np)

    # Subtle Enhancements
    img_pil = Image.fromarray(img_np)
    img_pil = ImageEnhance.Contrast(img_pil).enhance(1.02)
    img_pil = ImageEnhance.Brightness(img_pil).enhance(1.02)
    img_pil = ImageEnhance.Color(img_pil).enhance(1.05)
    img_pil = ImageEnhance.Sharpness(img_pil).enhance(1.1)

    return img_pil

# === Streamlit UI ===
st.set_page_config(
    page_title="AI Photo Composite Editor",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 1.2em;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .upload-box {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    .result-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .stMarkdown {
        font-size: 1.2em;
    }
    .stSuccess {
        font-size: 1.2em;
        padding: 1rem;
        border-radius: 5px;
    }
    .stInfo {
        font-size: 1.2em;
        padding: 1rem;
        border-radius: 5px;
    }
    a {
        text-decoration: none !important;
        color: inherit !important;
    }
    .stImage {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stImage"] {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content
st.title("🎨 AI Photo Composite Editor")
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: #2c3e50;'>Create Professional Photo Composites</h2>
        <p style='color: #7f8c8d; font-size: 1.2em;'>Upload your images below to get started</p>
    </div>
""", unsafe_allow_html=True)

# Upload section
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📸 Person Image")
    st.markdown("Upload a clear photo of a person or object")
    person_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="person")

with col2:
    st.markdown("### 🏞️ Background Image")
    st.markdown("Upload a background image for the composite")
    bg_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="background")
st.markdown('</div>', unsafe_allow_html=True)

# Processing and Results
if person_file and bg_file:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    with st.spinner("🔄 Processing your images..."):
        final_image = composite_with_shadow_and_enhance(person_file, bg_file)

    st.success("✨ Your composite is ready!")
    
    # Display the result
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.image(final_image, width=1000)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download
    img_bytes = io.BytesIO()
    final_image.save(img_bytes, format='JPEG', quality=95)
    st.download_button(
        "📥 Download High Quality Image",
        data=img_bytes.getvalue(),
        file_name="composite_output.jpg",
        mime="image/jpeg",
        help="Click to download your composite image"
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👆 Please upload both a person image and a background image to create your composite.")

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid #eee;'>
        <p style='color: #7f8c8d;'>Made with ❤️ by Soha-n</p>
    </div>
""", unsafe_allow_html=True)
