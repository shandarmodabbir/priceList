from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load CSV files
daily_products = pd.read_csv('/home/modabbir/Desktop/priceList/Daily_Use_Products_List.csv')
electronics = pd.read_csv('/home/modabbir/Desktop/priceList/Electronic_Products_List.csv')

# Add a 'Category' column to each dataset
daily_products['Category'] = 'Daily Basis Use'
electronics['Category'] = 'Electronics'

# Combine the datasets
df = pd.concat([daily_products, electronics], ignore_index=True)

@app.route('/products')
def get_products():
    """Return the full list of products."""
    return jsonify(df.to_dict(orient='records'))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    min_price = float(request.args.get('min', 0))
    max_price = float(request.args.get('max', float('inf')))
    category = request.args.get('category', '')

    # Filter by search query, price range, and category
    filtered = df[
        (df['Product Name'].str.contains(query, case=False)) &
        (df['Average Price (USD)'] >= min_price) &
        (df['Average Price (USD)'] <= max_price)
    ]

    if category and category.lower() != "all categories":
        filtered = filtered[filtered['Category'].str.contains(category, case=False)]

    # Extract the price range from the 'Price Range (USD)' column and filter by price range
    def in_price_range(row):
        try:
            # Split the range and convert to floats
            low, high = map(float, row['Price Range (USD)'].split(' - '))
            return (low >= min_price and low <= max_price) or (high >= min_price and high <= max_price)
        except ValueError:
            # Skip rows with invalid or missing price ranges
            return False

    filtered = filtered[filtered.apply(in_price_range, axis=1)]

    return jsonify(filtered.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(debug=True)
