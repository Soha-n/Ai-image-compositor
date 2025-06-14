# Ai-image-compositor
 Streamlit web app that removes background, adds shadows, blends subjects into a new background, and enhances images with filters — all using AI.
Absolutely! Here's a complete **GitHub repo structure**, including a good **repo name**, **description**, and a full **README.md** file for your Streamlit-based AI Image Compositor.

# 🖼️ AI Image Compositor

This project is a Streamlit-based web app that lets you:

- Automatically remove the background from a person image using `rembg`.
- Add a realistic shadow and composite the person onto a new background.
- Enhance the final output with brightness, contrast, saturation, sharpness, and a soft vignette.
- Download the resulting photorealistic image.

---

## 🚀 Demo

Upload your background and foreground images and get a professional-looking composite in seconds.

![App Screenshot](https://your-screenshot-link-or-gif.gif)

---

## 🧠 Features

✅ Background removal using `rembg`  
✅ Shadow generation from the person's alpha mask  
✅ Auto scaling and positioning  
✅ Realistic enhancement (exposure, contrast, saturation)  
✅ Vignette for cinematic effect  
✅ Clean, responsive Streamlit front-end  
✅ Downloadable output  

---

## 🛠️ Tech Stack

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [rembg](https://github.com/danielgatis/rembg)
- [Pillow](https://python-pillow.org/)
- [OpenCV](https://opencv.org/)
- [Matplotlib](https://matplotlib.org/)

---

## 🖥️ Run Locally

1. **Clone the repo**  
```bash
git clone https://github.com/yourusername/ai-image-compositor.git
cd ai-image-compositor
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Start the app**

```bash
streamlit run app.py
```

---
---

## ✅ Requirements

Place these in `requirements.txt`:

```
streamlit==1.31.1
Pillow==10.1.0
numpy==1.24.3
opencv-python-headless==4.7.0.72
rembg==2.0.50
pooch==1.7.0
pymatting==1.1.11
scikit-image==0.21.0
onnxruntime==1.15.1 
```

---
