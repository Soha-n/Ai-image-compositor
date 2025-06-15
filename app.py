import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2
import io

# === Image Processing Function ===
def composite_with_shadow_and_enhance(person_img, bg_img):
    try:
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

        # === Step 4: Adjust Brightness to Match Scene ===
        person = ImageEnhance.Brightness(person).enhance(0.9)

        # === Step 5: Create Soft Shadow ===
        alpha = person.split()[3]
        shadow = Image.new("RGBA", person.size, (0, 0, 0, 100))
        shadow.putalpha(alpha)
        blur_radius = int(person.height * 0.08)
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

        # === Step 6: Position Person and Shadow ===
        offset_x = int(person.width * 0.06)
        offset_y = int(person.height * 0.06)
        px = (bg_width - person.width) // 2
        py = bg_height - person.height
        temp_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        temp_layer.paste(shadow, (px + offset_x, py + offset_y), shadow)
        temp_layer.paste(person, (px, py), person)

        # === Step 7: Composite Layers ===
        composite = Image.alpha_composite(bg, temp_layer)

        # === Step 8: Convert to RGB & Apply Enhancements ===
        comp_rgb = composite.convert("RGB")
        img_np = np.array(comp_rgb)

        def adjust_gamma(img, gamma=0.9):
            inv_gamma = 1.0 / gamma
            table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
            return cv2.LUT(img, table)

        img_np = adjust_gamma(img_np)

        img_pil = Image.fromarray(img_np)
        img_pil = ImageEnhance.Contrast(img_pil).enhance(0.95)
        img_pil = ImageEnhance.Brightness(img_pil).enhance(1.01)
        img_pil = ImageEnhance.Color(img_pil).enhance(1.1)
        img_pil = ImageEnhance.Sharpness(img_pil).enhance(1.1)

        # === Vignette Effect ===
        img_np = np.array(img_pil)
        rows, cols = img_np.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = (255 * kernel / np.max(kernel)) * 0.4

        vignette = np.zeros_like(img_np)
        for i in range(3):
            vignette[..., i] = img_np[..., i] * (mask / 255)
        vignette = np.clip(vignette + img_np * 0.6, 0, 255).astype(np.uint8)

        final_image = Image.fromarray(vignette)
        return final_image

    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None


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

# === Page Title ===
st.title("🎨 AI Photo Composite Editor")
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: #2c3e50;'>Create Professional Photo Composites</h2>
        <p style='color: #7f8c8d; font-size: 1.2em;'>Upload your images below to get started</p>
    </div>
""", unsafe_allow_html=True)

# === Upload Images ===
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📸 Person Image")
    person_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="person")

with col2:
    st.markdown("### 🏞️ Background Image")
    bg_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="background")

st.markdown('</div>', unsafe_allow_html=True)

# === Process and Display Result ===
if person_file and bg_file:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    with st.spinner("🔄 Processing your images..."):
        final_image = composite_with_shadow_and_enhance(person_file, bg_file)

    if final_image:
        st.success("✨ Your composite is ready!")
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.image(final_image, width=1000)
        st.markdown('</div>', unsafe_allow_html=True)

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

# === Footer ===
st.markdown("""
    <div style='text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid #eee;'>
        <p style='color: #7f8c8d;'>Made with ❤️ by Soha-n</p>
    </div>
""", unsafe_allow_html=True)
