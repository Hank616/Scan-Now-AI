# 📷 Scan Now AI

**Scan Now AI** is a web-based AI app that lets users upload an image and instantly:

- ✅ Recognize what’s in the image using AI
- 🖼️ See visually similar images from Bing
- 🛍️ Discover related products via Bing Shopping

It combines TensorFlow image classification with real-time scraping of Bing results to create an intelligent visual search experience.

---

## 🚀 Features

- Upload any image (product, animal, object, etc.)
- Classify image content using MobileNetV2 (TensorFlow)
- Scrape similar image results from Bing Images
- Automatically list relevant products from Bing Shopping

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask** – Web server
- **TensorFlow / Keras** – MobileNetV2 AI model
- **Selenium** – Bing Shopping automation
- **BeautifulSoup** – HTML parsing for Bing Images

---

## ▶️ How to Run

> 🔧 **Quick steps to start the app and use it:**

1. **Clone the project:**
   ```bash
   git clone https://github.com/Hank616/scan-now-ai.git
   cd scan-now-ai
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
3. **Make sure ChromeDriver is installed and added to your system PATH**
4. **Run the app:**
   ```bash
   python app.py
5. **Open the web interface:**
   Go to the output URL (usually):
   ```bash
   http://127.0.0.1:5000
6. **Upload an image on the website and you will see:**  
   AI-predicted labels  
  Similar images from Bing  
  Related product listings from Bing Shopping  
