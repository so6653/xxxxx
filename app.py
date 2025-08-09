from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # ここは適宜変えてください

DB_PATH = 'data/products.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs('data', exist_ok=True)
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER,
                image TEXT
            )
        ''')
        # サンプル商品
        products = [
            ('ぬいぐるみA', 'ふわふわのぬいぐるみです。', 1200, 'https://via.placeholder.com/300x200?text=ぬいぐるみA'),
            ('ぬいぐるみB', 'かわいいぬいぐるみです。', 1500, 'https://via.placeholder.com/300x200?text=ぬいぐるみB'),
            ('ぬいぐるみC', '人気のぬいぐるみです。', 1800, 'https://via.placeholder.com/300x200?text=ぬいぐるみC'),
            ('ぬいぐるみD', '限定版のぬいぐるみです。', 2500, 'https://via.placeholder.com/300x200?text=ぬいぐるみD'),
            ('ぬいぐるみE', 'かわいい友達のぬいぐるみです。', 1600, 'https://via.placeholder.com/300x200?text=ぬいぐるみE'),
        ]
        conn.executemany('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)', products)
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if product is None:
        return "商品が見つかりません", 404
    return render_template('product.html', product=product)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    conn = get_db_connection()
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if product:
            subtotal = product['price'] * quantity
            items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
            total += subtotal
    conn.close()
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout/select')
def checkout_select():
    return render_template('checkout_select.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    method = request.form['payment_method']
    # ここで決済処理を実装（仮）
    # 実際はPayPayなどAPIと連携します
    session.pop('cart', None)  # カートを空にする
    return render_template('checkout.html', method=method)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
