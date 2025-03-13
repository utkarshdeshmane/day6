from flask import Flask, render_template, request, flash, redirect, url_for
import requests
import logging
import plotly.graph_objects as go
import plotly.utils
import json
from pymongo import MongoClient

app = Flask(__name__)


# Configure logging
logging.basicConfig(
    filename="logger.log",
    filemode="a+",
    format='%(asctime)s %(message)s',
    level=logging.DEBUG
)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://utkarsh:11223344@cluster0.blx1n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ajio_tracker"]  # Database name
collection = db["products"]  # Collection name

@app.route("/", methods=['GET', 'POST'])
def home():
    output = []
    chart_json = None
    print(1)
    if request.method == 'POST':
        try:
            data = request.form['url']
            headers = {"User-Agent": "Mozilla/5.0"}
            product_urls = [url.strip() for url in data.split(',')]
            logging.debug("URL(s) loaded successfully")
            
            for url in product_urls:
                existing_product = collection.find_one({"url": url})
                if existing_product:
                    logging.info(f"Product data retrieved from MongoDB for URL: {url}")
                    output.append(existing_product)
                    continue
                
                product_code = url.split("/")[-1]
                API_URL = f"https://www.ajio.com/api/p/{product_code}"
                res = requests.get(API_URL, headers=headers)
                res.raise_for_status()
                
                try:
                    product_details = res.json()
                    product_info = {
                        'url': url,
                        'Product Name': product_details['baseOptions'][0]['options'][0]['modelImage']['altText'],
                        'Product Stock': 'Available' if product_details['baseOptions'][0]['options'][0]['stock']['stockLevelStatus'] == 'inStock' else 'Out of Stock',
                        'Quantity in stock': product_details['baseOptions'][0]['options'][0]['stock']['stockLevel'],
                        'Current Price': product_details['baseOptions'][0]['options'][0]['priceData']['value'],
                        'Best Promos': [x['maxSavingPrice'] for x in product_details.get('potentialPromotions', [])[:3]]
                    }
                    collection.insert_one(product_info)  # Save to MongoDB
                    output.append(product_info)
                except (KeyError, ValueError) as e:
                    logging.error(f"Error processing product data: {e}")
                    flash("Error processing product data. Please check the URL or try again.")
                    return redirect(url_for('home'))
        
        except requests.exceptions.ConnectionError:
            logging.error("Connection error. Please check your internet connection.")
            flash("Connection error. Please check your internet connection.")
            return redirect(url_for('home'))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            flash("An unexpected error occurred. Please try again.")
            return redirect(url_for('home'))
        
        if output:
            product_names = [item['Product Name'] for item in output]
            product_prices = [item['Current Price'] for item in output]
            best_promos = [
                max(item.get("Best Promos", [0]))  # Get max discount or 0 if no promotions
                for item in output
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=product_names, y=product_prices, name='Price', marker_color='blue'))
            fig.add_trace(go.Bar(x=product_names, y=best_promos, name='Price After-Discount', marker_color='red'))
            
            fig.update_layout(
                title='Product Prices and Discount Amounts',
                xaxis_title='Products',
                yaxis_title='Value (₹)',
                barmode='group'
            )
            
            chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) 
    
    return render_template("ajio_price_tracker.html", output=output, chart_json=chart_json)

if __name__ == "__main__":
    app.run(debug=True)
