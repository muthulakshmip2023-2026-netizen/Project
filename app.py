from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json, os
from datetime import datetime

# ---------------- APP ----------------
app = Flask(__name__)
app.secret_key = "super-secret-key-change-this-later-xyz123"
CORS(app)

# ---------------- CONFIGURATION ----------------
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static/images')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "novashop.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cat = db.Column(db.String(50))
    rating = db.Column(db.Float)
    sizes = db.Column(db.Text)
    img = db.Column(db.String(500)) 
    stock = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    items = db.Column(db.Text) 
    total = db.Column(db.Integer)
    address = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- DEFAULT PRODUCTS ----------------
default_products = [
    {"id": 1, "name": "Casual Cotton T-Shirt", "price": 799, "cat": "men", "rating": 4.2, "sizes": ["S","M","L","XL"], "img": "men1.jpeg", "stock": 28},
    {"id": 102, "name": "Graphic Print Hoodie", "price": 1899, "cat": "men", "rating": 4.7, "sizes": ["M","L"], "img": "men2.jpeg", "stock": 11},
    {"id": 103, "name": "Denim Jacket Classic", "price": 2599, "cat": "men", "rating": 4.6, "sizes": ["M","L","XL"], "img": "men3.jpeg", "stock": 8},
    {"id": 2, "name": "Floral Midi Dress", "price": 1499, "cat": "women", "rating": 4.8, "sizes": ["S","M","L"], "img": "wom1.jpeg", "stock": 16},
    {"id": 201, "name": "Boho Maxi Dress", "price": 2199, "cat": "women", "rating": 4.9, "sizes": ["S","M"], "img": "wom2.jpeg", "stock": 9},
    {"id": 203, "name": "Party Red Gown", "price": 2899, "cat": "women", "rating": 4.7, "sizes": ["M","L"], "img": "wom3.jpeg", "stock": 6},
    {"id": 3, "name": "Smartwatch Series 7", "price": 3999, "cat": "electronics", "rating": 4.9, "sizes": None, "img": "elc1.jpeg", "stock": 13},
    {"id": 301, "name": "Wireless Earbuds Pro", "price": 2499, "cat": "electronics", "rating": 4.7, "sizes": None, "img": "elc2.jpeg", "stock": 24},
    {"id": 302, "name": "Portable Bluetooth Speaker", "price": 2799, "cat": "electronics", "rating": 4.8, "sizes": None, "img": "elc3.jpeg", "stock": 8},
    {"id": 4, "name": "Interactive Laser Cat Toy", "price": 499, "cat": "cat", "rating": 4.9, "sizes": None, "img": "cat1.jpeg", "stock": 5},
    {"id": 401, "name": "Cat Scratching Tower", "price": 1499, "cat": "cat", "rating": 4.6, "sizes": None, "img": "cat2.jpeg", "stock": 12},
    {"id": 402, "name": "Catnip Toy Set (6 pcs)", "price": 349, "cat": "cat", "rating": 5.0, "sizes": None, "img": "cat3.jpeg", "stock": 40},
    {"id": 5, "name": "Heavy Duty Dog Leash", "price": 699, "cat": "dog", "rating": 4.7, "sizes": None, "img": "dog1.jpeg", "stock": 19},
    {"id": 501, "name": "Orthopedic Pet Bed Medium", "price": 1999, "cat": "dog", "rating": 4.8, "sizes": None, "img": "dog2.jpeg", "stock": 10},
    {"id": 502, "name": "Indestructible Chew Toy", "price": 399, "cat": "dog", "rating": 4.9, "sizes": None, "img": "dog3.jpeg", "stock": 32},
    {"id": 601, "name": "Scented Candle Gift Set", "price": 999, "cat": "home", "rating": 4.8, "sizes": None, "img": "home1.jpeg", "stock": 17},
    {"id": 602, "name": "Modern LED Table Lamp", "price": 1599, "cat": "home", "rating": 4.6, "sizes": None, "img": "home2.jpeg", "stock": 13},
    {"id": 702, "name": "Lip Care Trio Pack", "price": 449, "cat": "beauty", "rating": 4.9, "sizes": None, "img": "beauty.jpeg", "stock": 35},
    {"id": 802, "name": "Resistance Bands Set (5 pcs)", "price": 799, "cat": "sports", "rating": 4.6, "sizes": None, "img": "fit.jpeg", "stock": 26},
    {"id": 901, "name": "Building Blocks Set 500 pcs", "price": 1799, "cat": "toys", "rating": 5.0, "sizes": None, "img": "toy1.jpeg", "stock": 12},
    {"id": 902, "name": "Remote Control Racing Car", "price": 1399, "cat": "toys", "rating": 4.7, "sizes": None, "img": "toy2.jpeg", "stock": 9},
    {"id": 903, "name": "Puzzle 1000 Pieces Landscape", "price": 599, "cat": "toys", "rating": 4.6, "sizes": None, "img": "toy3.jpeg", "stock": 15},
    {"id": 1001, "name": "Polarized Sunglasses UV400", "price": 999, "cat": "accessories", "rating": 4.6, "sizes": None, "img": "uv1.jpeg", "stock": 20},
    {"id": 1002, "name": "Genuine Leather Wallet", "price": 1499, "cat": "accessories", "rating": 4.8, "sizes": None, "img": "uv2.jpeg", "stock": 15},
    {"id": 1003, "name": "Bluetooth Smart Watch Band", "price": 799, "cat": "accessories", "rating": 4.5, "sizes": None, "img": "uv3.jpeg", "stock": 18},
    {"id": 1101, "name": "Motivational Notebook Set (3 pcs)", "price": 499, "cat": "books", "rating": 4.5, "sizes": None, "img": "book1.jpeg", "stock": 30},
    {"id": 1102, "name": "Best Seller Fiction Novel", "price": 399, "cat": "books", "rating": 4.9, "sizes": None, "img": "book2.jpeg", "stock": 25},
    {"id": 1103, "name": "Academic Planner 2026", "price": 599, "cat": "books", "rating": 4.7, "sizes": None, "img": "book3.jpeg", "stock": 22}
]

# ---------------- INIT DB ----------------
def init_db():
    with app.app_context():
        db.create_all()
        if Product.query.first() is None:
            for p in default_products:
                db.session.add(Product(
                    id=p["id"], name=p["name"], price=p["price"], cat=p["cat"],
                    rating=p["rating"],
                    sizes=json.dumps(p["sizes"]) if p["sizes"] else None,
                    img=p["img"], stock=p["stock"]
                ))
            db.session.commit()
            print("✅ Default products inserted")

# ---------------- ROUTES (PAGES) ----------------
@app.route('/')
def index(): return render_template('register.html')

@app.route('/register')
def show_register(): return render_template('register.html')

@app.route('/login')
def show_login(): return render_template('login.html')

@app.route('/home')
def home(): return render_template('home.html')

@app.route('/wishlist')
def wishlist(): return render_template('wishlist.html')

@app.route('/cart')
def cart(): return render_template('cart.html')

@app.route('/orders')   
def orders(): return render_template('orders.html')

@app.route('/checkout')
def checkout(): return render_template('checkout.html')

@app.route('/confirmation')
def confirmation(): return render_template('confirmation.html')

@app.route('/admin_login')
def admin_login(): return render_template('admin_login.html')

@app.route('/admin_orders')
def admin_orders(): return render_template('admin_orders.html')

@app.route('/admin_products_dashboard')
def admin_products_dashboard(): return render_template('admin_products_dashboard.html')

@app.route('/favicon.ico')
def favicon(): return '', 204

# ---------------- API: USER AUTH ----------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email"): return jsonify({"error":"Invalid data"}), 400
    if User.query.filter_by(email=data["email"]).first(): return jsonify({"error":"Email already exists"}), 409
    user = User(name=data["name"], email=data["email"], password=generate_password_hash(data["password"]))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User registered successfully"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error":"Invalid email or password"}), 401
    return jsonify({"message":"Login successful", "user":{"id":user.id, "name":user.name, "email":user.email}}), 200

# ---------------- API: ADMIN LOGIN ----------------
@app.route("/api/admin/login", methods=["POST"])
def admin_login_api():
    data = request.get_json()
    if data.get("email") == "admin@novashop.com" and data.get("password") == "admin123":
        return jsonify({"message": "Admin login successful"}), 200
    return jsonify({"error": "Invalid admin credentials"}), 401

# ---------------- API: GET PRODUCTS ----------------
@app.route("/api/products")
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id":p.id, "name":p.name, "price":p.price, "cat":p.cat,
            "rating":p.rating, "sizes":json.loads(p.sizes) if p.sizes else None,
            "img":p.img, "stock":p.stock
        } for p in products
    ])

# ---------------- API: ADD PRODUCT (ADMIN) ----------------
@app.route("/api/products", methods=["POST"])
def add_product():
    try:
        name = request.form.get('name')
        price_str = request.form.get('price')
        cat = request.form.get('cat')
        stock_str = request.form.get('stock')
        rating_str = request.form.get('rating', '4.5')
        sizes_str = request.form.get('sizes')
        
        if not name or not price_str or not cat or not stock_str:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            price = int(float(price_str))
            stock = int(float(stock_str))
            rating = float(rating_str)
        except ValueError:
            return jsonify({"error": "Invalid number format"}), 400

        img_value = ""
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_value = filename
        
        if not img_value:
            img_url = request.form.get('img_url')
            if img_url: img_value = img_url

        sizes_json = None
        if sizes_str:
            s_list = [s.strip() for s in sizes_str.split(',') if s.strip()]
            if s_list: sizes_json = json.dumps(s_list)

        new_product = Product(name=name, price=price, cat=cat, stock=stock, rating=rating, sizes=sizes_json, img=img_value)
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({"message": "Product added successfully", "id": new_product.id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- API: UPDATE PRODUCT (ADMIN) - FIXED ----------------
@app.route("/api/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        # Handle Form Data (with image) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            product.name = request.form.get("name", product.name)
            product.price = int(float(request.form.get("price", product.price)))
            product.stock = int(float(request.form.get("stock", product.stock)))
            product.cat = request.form.get("cat", product.cat)
            
            # FIXED: Handle Sizes Update
            sizes_str = request.form.get("sizes")
            if sizes_str is not None:
                s_list = [s.strip() for s in sizes_str.split(',') if s.strip()]
                product.sizes = json.dumps(s_list) if s_list else None
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    product.img = filename
        else:
            # Handle JSON (fallback)
            data = request.get_json()
            product.name = data.get("name", product.name)
            product.price = int(float(data.get("price", product.price)))
            product.stock = int(float(data.get("stock", product.stock)))
            product.cat = data.get("cat", product.cat)
            
            # FIXED: Handle Sizes in JSON
            if "sizes" in data:
                product.sizes = json.dumps(data["sizes"]) if data["sizes"] else None
                
            if data.get("img"):
                 product.img = data.get("img")

        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        print(f"Error updating: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------- API: DELETE PRODUCT (ADMIN) ----------------
@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    product = Product.query.get(pid)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Not found"}), 404

# ---------------- API: ORDERS ----------------
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    new_order = Order(
        user_email=data.get("email"),
        items=json.dumps(data.get("items")),
        total=data.get("total"),
        address=data.get("address")
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Order placed", "id": new_order.id}), 201

@app.route("/api/orders", methods=["GET"])
def get_orders():
    orders = Order.query.order_by(Order.date.desc()).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id, "user_email": o.user_email, "items": json.loads(o.items),
            "total": o.total, "address": o.address, "status": o.status,
            "date": o.date.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(result)

@app.route("/api/orders/<int:oid>", methods=["PUT"])
def update_order(oid):
    order = Order.query.get(oid)
    if order:
        data = request.get_json()
        order.status = data.get("status", order.status)
        db.session.commit()
        return jsonify({"message": "Status updated"}), 200
    return jsonify({"error": "Not found"}), 404

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/") 
    
    app.run(debug=True)
