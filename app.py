from flask import Flask, render_template, request
from collections import defaultdict
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def search_flipkart(product, total_products_count):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }
        word_list = product.split(' ')
        url_list = []
        for word in word_list:
            url_list.append(word)
            url_list.append('+')
        url_list = url_list[:-1]
        url = 'https://www.flipkart.com/search?q=' + "".join(url_list)

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        all_divs = soup.find_all('div', {'class': '_1AtVbE'})

        flipkart_products_data = defaultdict(dict)
        count = 0

        for div in all_divs:
            item_divs = div.find_all("div", {"data-id": re.compile("^[a-zA-Z]*")})

            for item_div in item_divs:
                # Get the name
                item_name = item_div.find('img')['alt'].strip()
                if item_name == "":
                    # Try to find item name in anchor tags
                    anchor_tags = item_div.find_all('a')
                    for tag in anchor_tags:
                        text = tag.get('title')
                        if text is not None:
                            item_name = text
                if item_name[-3:] == '...':
                    item_name = item_name[:-3]

                if item_name == "":
                    flipkart_products_data[count]['item_name'] = "Unavailable"
                else:
                    flipkart_products_data[count]['item_name'] = item_name

                # Get the rating
                item_rating = item_div.find('span', {'class': '_1lRcqv'})
                if item_rating is not None:
                    flipkart_products_data[count]['item_rating'] = item_rating.get_text().strip()
                else:
                    flipkart_products_data[count]['item_rating'] = 'Unavailable'

                # Get the price
                item_price = item_div.find('div', {'class': '_30jeq3 _1_WHN1'})
                if item_price is not None:
                    flipkart_products_data[count]['item_price'] = item_price.get_text().strip()[1:]
                else:
                    flipkart_products_data[count]['item_price'] = 'Unavailable'

                # Get the link
                item_link = item_div.find("a", {'class': '_1fQZEK'})
                if item_link is not None:
                    flipkart_products_data[count]['item_link'] = 'https://www.flipkart.com' + item_link['href']
                else:
                    flipkart_products_data[count]['item_link'] = 'Unavailable'

                count += 1
                if count == total_products_count:
                    return flipkart_products_data

        return flipkart_products_data

    except Exception as e:
        # Could not fetch data from Flipkart
        return {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product = request.form['product']
        total_products_count = int(request.form['total_products_count'])
        results = search_flipkart(product, total_products_count)
        return render_template('index.html', results=results, product=product, total_products_count=total_products_count)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
