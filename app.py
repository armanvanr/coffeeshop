from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import environ
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

load_dotenv()
db_username = environ["USER_NAME"]
db_password = environ["PASSWORD"]

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{db_username}:{db_password}@localhost:5432/coffeeshop"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    role = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User {self.id}>"


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_bill = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Order {self.id}>"


class Order_Items(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    quantity = db.Column(db.SmallInteger, nullable=False)

    def __repr__(self):
        return f"<Order-Item {self.order_id}-{self.menu_id}>"


class Menu(db.Model):
    __tablename__ = "menu"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.SmallInteger, nullable=False)
    img_url = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Menu {self.id}>"


class Balance_Record(db.Model):
    __tablename__ = "balance_record"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    nominal = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}>"


@app.get("/")
def welcome():
    return {"success": True, "message": "Welcome to Coffee Shop API", "data": {}}


@app.get("/users")
def get_users():
    users = [
        {
            "name": user.name,
            "id": user.id,
            "balance": user.balance,
            "email": user.email,
            "role": user.role,
            "password": user.password,
        }
        for user in User.query.all()
    ]
    return {"success": True, "message": "Data found", "data": {"users": users}}, 200


# register a new user
@app.post("/user")
def add_user():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return {"success": False, "message": "Email already exists", "data": {}}, 400
    hash_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hash_pw,
        role=data["role"],
    )
    db.session.add(new_user)
    db.session.commit()
    return {"success": True, "message": "Account successfully created", "data": {}}, 201


# change name or password
@app.put("/user/<int:id>")
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if not user:
        return {"success": False, "message": "Data not found", "data": {}}, 404
    user.name = data.get("name", user.name)
    if "new_password" in data.keys():
        is_valid = bcrypt.check_password_hash(user.password, data["old_password"])
        if is_valid:
            hash_pw = bcrypt.generate_password_hash(data["new_password"]).decode(
                "utf-8"
            )
            user.password = hash_pw
    db.session.commit()
    return {"success": True, "message": "Account data updated", "data": {}}, 200


# show all in-stock menus
@app.get("/menus")
def get_menus():
    drinks = [
        {
            "name": menu.name,
            "id": menu.id,
            "img_url": menu.img_url,
        }
        for menu in Menu.query.filter_by(category="drinks")
        if menu.stock > 0
    ]
    foods = [
        {
            "name": menu.name,
            "id": menu.id,
            "img_url": menu.img_url,
        }
        for menu in Menu.query.filter_by(category="foods")
        if menu.stock > 0
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"drinks": drinks, "foods": foods},
    }, 200


# show a menu details
@app.get("/menu/<int:id>")
def get_menu(id):
    menu = Menu.query.get(id)
    details = {
        "name": menu.name,
        "id": menu.id,
        "img_url": menu.img_url,
        "price": menu.price,
        "description": menu.desc,
        "stock": menu.stock,
    }

    return {
        "success": True,
        "message": "Data found",
        "data": {"details": details},
    }, 200


# add a new menu
@app.post("/menu")
def add_menu():
    data = request.get_json()

    new_menu = Menu(
        name=data["name"],
        desc=data["desc"],
        price=data["price"],
        stock=data["stock"],
        img_url=data["img_url"],
        category=data["category"],
    )
    db.session.add(new_menu)
    db.session.commit()
    return {"success": True, "message": "menu added", "data": {}}, 201


# update menu data
@app.put("/menu/<int:id>")
def update_menu(id):
    data = request.get_json()
    menu = Menu.query.get(id)
    menu.name = data.get("name", menu.name)
    menu.desc = data.get("desc", menu.desc)
    menu.price = data.get("price", menu.price)
    menu.img_url = data.get("img_url", menu.img_url)
    db.session.commit()
    return {"success": True, "message": "menu updated", "data": {}}, 200


# update menu stock
@app.put("/menu/stock/<int:id>")
def update_menu_stock(id):
    data = request.get_json()
    menu = Menu.query.get(id)
    menu.stock = data.get("stock", menu.stock)
    db.session.commit()
    return {"success": True, "message": "menu stock updated", "data": {}}, 200


# search menu
@app.get("/menusearch")
def menu_search():
    args = request.args
    q = Menu.query
    if "name" in args.keys():
        q = q.filter(Menu.name.ilike(f"%{args['name']}%"))
    menus = q.all()
    results = [
        {
            "name": menu.name,
            "id": menu.id,
            "img_url": menu.img_url,
        }
        for menu in menus
        if menu.stock > 0
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"results": results},
    }, 200


if __name__ == "__main__":
    app.run(debug=True)
