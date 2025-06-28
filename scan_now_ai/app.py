import os
import time
import json
import requests
import numpy as np
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the debug file

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load AI model
model = MobileNetV2(weights='imagenet')

# HTML Template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Scan Now AI</title>
</head>
<body>
    <h2>📷 Upload an image</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <input type="submit" value="Scan">
    </form>

    {% if labels %}
        <h3>✅ I think this is:</h3>
        <ul>
        {% for item in labels %}
            <li>{{ item.label }} ({{ item.confidence }}%)</li>
        {% endfor %}
        </ul>

        <h3>🖼️ Similar Images from Bing:</h3>
        {% for img_url in image_urls %}
            <img src="{{ img_url }}" alt="Similar image" style="max-height:150px; margin:10px;">
        {% endfor %}

        <h3>🛍️ Similar Products (from Bing Shopping):</h3>
        {% if products %}
            {% for item in products %}
                <p>
                    <b>{{ loop.index }}. {{ item.title }}</b><br>
                    Price: {{ item.price }}<br>
                    <img src="{{ item.img_url }}" style="max-height:100px;"><br>
                    <a href="{{ item.link }}" target="_blank">Buy here</a>
                </p>
            {% endfor %}
        {% else %}
            <p>No products found.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

# Recognize image labels
def recognize(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    prediction = model.predict(img_array)
    decoded = decode_predictions(prediction, top=5)[0]
    labels = [{'label': item[1], 'confidence': f"{item[2]*100:.2f}"} for item in decoded]
    return labels

# Bing image URLs (static scraping, works fine)
def bing_image_urls(keyword, max_results=3):
    query = keyword.replace(' ', '+')
    url = f"https://www.bing.com/images/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    print(resp.text)
    image_urls = []
    for a in soup.find_all('a', class_='iusc', limit=max_results):
        m_json = a.get('m')
        if m_json:
            m_data = json.loads(m_json)
            murl = m_data.get('murl')
            if murl:
                image_urls.append(murl)
    return image_urls

# Selenium-based Bing Shopping scraping with WebDriverWait
def search_bing_shopping(keyword, max_results=8):
    query = keyword.replace(' ', '+')
    url = f"https://www.bing.com/shop?q={query}"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # Wait until product cards appear
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.br-pdMain"))
        # )
        driver.implicitly_wait(10)
        time.sleep(2)  # extra wait for full render
        page_text = driver.page_source
        
        cards = driver.find_elements(By.CSS_SELECTOR, "li.br-item.br-allowCrdovrflw")  # fallback options

        # , encoding="utf-8"

        with open("C:/Users/hao07/Downloads/tester.txt", "a") as file:
            file.write(str(len(cards)) + "\n\n")
        
        results = []

        for card in cards[:max_results]:
            try:
                for idx, card in enumerate(cards[:max_results]):
                    print(card.get_attribute("outerHTML"))
                    try:
                        # Get title (deep nested search)
                        title = ""
                        try:
                            title = card.find_element(By.CSS_SELECTOR, "div.br-title.br-freeGridFontChange").text.strip()
                        except:
                            title = card.text.strip().split('\n')[0]  # fallback

                        # Get price
                        price = ""
                        try:
                            price = card.find_element(By.CSS_SELECTOR, "div.br-price.br-unit-price").text.strip()
                        except:
                            price = "N/A"

                        # Get link
                        try:
                            link = card.find_element(By.CSS_SELECTOR, "a.br-titlelink.sj_spcls").get_attribute("href")
                        except:
                            link = "No link"

                        # Get image
                        try:
                            img = card.find_element(By.TAG_NAME, "img").get_attribute("src")
                        except:
                            img = ""

                        # Log/save
                        print(f"[{idx}] {title} | {price}")
                        with open("C:/Users/hao07/Downloads/tester.txt", "a", encoding="utf-8") as file:
                            file.write(f"{title} | {price} | {link}\n\n")

                        results.append({
                            'title': title,
                            'price': price,
                            'link': link,
                            'img_url': img
                        })

                    except Exception as e:
                        print(f"⚠️ Skipping card due to error: {e}")
                results.append({
                    'title': title,
                    'price': price,
                    'link': link,
                    'img_url': img
                })
            except Exception as e:
                print(f"⚠️ Skipping product due to error: {e}")
                continue

    except Exception as e:
        print(f"❌ Error loading Bing Shopping results: {e}")
        driver.save_screenshot("debug_bing.png")
        results = []

    driver.quit()
    
    title_list = []
    for i in range(len(title_list)):
        if results[i]['title'] in title_list:
            del results[i]
            i -= 1
        else:
            title_list.append(title_list[i]['title'])
            
    return results

# Flask route
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    labels = []
    products = []
    image_urls = []
    if request.method == 'POST':
        file = request.files['file']
        if file:
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)

            labels = recognize(img_path)
            top_label = labels[0]['label'] if labels else 'unknown'
            image_urls = bing_image_urls(top_label)
            products = search_bing_shopping(top_label)

    return render_template_string(HTML, labels=labels, products=products, image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)
