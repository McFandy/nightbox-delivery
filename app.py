from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "delivery.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-real-project"  # для учебного можно оставить так
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", backref="cart_items")
    product = db.relationship("Product")


@app.before_request
def load_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.current_user = None
    else:
        g.current_user = User.query.get(user_id)


def login_required(view_func):
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


@app.route("/")
def index():
    products = Product.query.limit(3).all()
    return render_template("index.html", products=products)


@app.route("/catalog")
def catalog():
    products = Product.query.all()
    return render_template("catalog.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not email or not name or not password:
            error = "Заполните все поля."
        elif password != confirm:
            error = "Пароли не совпадают."
        elif User.query.filter_by(email=email).first():
            error = "Пользователь с таким email уже существует."
        else:
            user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return redirect(url_for("profile"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            error = "Неверный email или пароль."
        else:
            session["user_id"] = user.id
            next_url = request.args.get("next")
            return redirect(next_url or url_for("profile"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=g.current_user)


@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=g.current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    item = CartItem.query.filter_by(user_id=g.current_user.id, product_id=product.id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=g.current_user.id, product_id=product.id, quantity=1)
        db.session.add(item)
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=g.current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart"))


def init_db():
    """Простая инициализация БД с несколькими товарами."""
    db.create_all()
    if not Product.query.first():
        sample_products = [
            Product(
                name="Пицца Маргарита",
                description="Классическая пицца с томатами и сыром.",
                price=499.0,
            ),
            Product(
                name="Бургер NightBox",
                description="Сочный бургер с говядиной и соусом.",
                price=389.0,
            ),
            Product(
                name="Сет роллов",
                description="Набор из 24 роллов на компанию.",
                price=899.0,
            ),
            Product(
                name="Лимонад домашний",
                description="Освежающий лимонад 1л.",
                price=199.0,
            ),
        ]
        db.session.add_all(sample_products)
        db.session.commit()


if __name__ == "__main__":
    # Локальный запуск
    with app.app_context():
        init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



