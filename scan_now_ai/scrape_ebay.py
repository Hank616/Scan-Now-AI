import requests
from bs4 import BeautifulSoup
import re

def search_bing_products(product_name):
    query = product_name.replace(' ', '+')
    url = f"https://www.bing.com/shop?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch Bing results.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    items = []
    for item_block in soup.find_all('li', class_='b_shp_itm'):
        title_tag = item_block.find('div', class_='b_shp_itm_title')
        price_tag = item_block.find('div', class_='b_shp_price')
        if title_tag and price_tag:
            title = title_tag.get_text(strip=True)
            price_text = price_tag.get_text(strip=True)
            match = re.search(r'\$(\d+(\.\d+)?)', price_text)
            if match:
                price = float(match.group(1))
                if price >= 2:  # Filter out suspiciously cheap prices
                    items.append((title, price))

    return items

# Try it
if __name__ == "__main__":
    query = input("Search for: ")
    results = search_bing_products(query)

    if not results:
        print("No real products found.")
    else:
        print("\nTop matching products:")
        for title, price in results[:5]:
            print(f"- {title}: ${price:.2f}")