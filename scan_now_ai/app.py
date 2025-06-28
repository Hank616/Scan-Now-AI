import os
import re
import requests
import numpy as np
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import json

# Set up Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load AI model
model = MobileNetV2(weights='imagenet')

# HTML Template (added images display)
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

    {% if label %}
        <h3>✅ I think this is a: {{ label }}</h3>

        <h3>🖼️ Similar Images from Bing:</h3>
        {% for img_url in image_urls %}
            <img src="{{ img_url }}" alt="Similar image" style="max-height:150px; margin:10px;">
        {% endfor %}

        <h3>🛍️ Similar Products:</h3>
        {% for item in products %}
            <p>
                <b>{{ loop.index }}. {{ item.title }}</b><br>
                Price: {{ item.price }}<br>
                <a href="{{ item.link }}" target="_blank">Buy here</a>
            </p>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

# Function: recognize object
def recognize(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    prediction = model.predict(img_array)
    label = decode_predictions(prediction, top=1)[0][0][1]
    return label

# Function: search Bing shopping
def search_bing_products(keyword):
    query = keyword.replace(' ', '+')
    url = f"https://www.bing.com/shop?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for item in soup.find_all('li', class_='b_shp_itm'):
        title_tag = item.find('div', class_='b_shp_itm_title')
        price_tag = item.find('div', class_='b_shp_price')
        link_tag = item.find('a', href=True)

        if title_tag and price_tag and link_tag:
            title = title_tag.get_text(strip=True)
            price_match = re.search(r'\$[\d.,]+', price_tag.get_text())
            if price_match:
                price = price_match.group(0)
                link = 'https://www.bing.com' + link_tag['href']
                results.append({'title': title, 'price': price, 'link': link})

        if len(results) >= 3:
            break
    return results

# NEW Function: get top 3 Bing Images URLs for the keyword
def bing_image_urls(keyword, max_results=3):
    query = keyword.replace(' ', '+')
    url = f"https://www.bing.com/images/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    image_urls = []
    for a in soup.find_all('a', class_='iusc', limit=max_results):
        m_json = a.get('m')
        if m_json:
            m_data = json.loads(m_json)
            murl = m_data.get('murl')
            if murl:
                image_urls.append(murl)
    return image_urls

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    label = None
    products = []
    image_urls = []

    if request.method == 'POST':
        file = request.files['file']
        if file:
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)

            label = recognize(img_path)
            products = search_bing_products(label)
            image_urls = bing_image_urls(label)

    return render_template_string(HTML, label=label, products=products, image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)
