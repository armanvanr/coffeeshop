from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import environ
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from datetime import datetime

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
auth = HTTPBasicAuth(app)


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
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    customer_name = db.Column(db.String, nullable=False)
    total_bill = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    order_items = db.relationship("Order_Items", backref="order")

    def __repr__(self):
        return f"<Order {self.id}>"


class Order_Items(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False)
    menu_name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.SmallInteger, nullable=False)

    def __repr__(self):
        return f"<Item(Qty) {self.menu_name}({self.quantity})>"


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
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=True)
    nominal = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}>"


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(email=username).first()
    # if not user:
    #     return {"message": "Unauthorized"}, 401
    # raise Exception({"message": "Unauthorized"}, 401)
    is_valid = bcrypt.check_password_hash(user.password, password)
    if user and is_valid:
        return user
    # else:
    #     return {"message": "Forbidden"}, 403


@auth.get_user_roles
def get_user_roles(user):
    roles = user.role
    return roles


@app.get("/")
def welcome():
    return {"success": True, "message": "Welcome to Coffee Shop API", "data": {}}


@app.get("/users")
@auth.login_required(role="admin")
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
@app.put("/user/update")
@auth.login_required()
def update_user():
    data = request.get_json()
    user = auth.current_user()

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


# show all in-stock menu
@app.get("/menu")
def get_all_menu():
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
@app.get("/menu/<int:m_id>")
@auth.login_required(role=["cashier", "admin"], optional=True)
def get_menu(m_id):
    menu = Menu.query.get(m_id)
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
@auth.login_required(role="admin")
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
@auth.login_required(role="admin")
def update_menu(m_id):
    data = request.get_json()
    menu = Menu.query.get(m_id)
    menu.name = data.get("name", menu.name)
    menu.desc = data.get("desc", menu.desc)
    menu.price = data.get("price", menu.price)
    menu.img_url = data.get("img_url", menu.img_url)
    db.session.commit()
    return {"success": True, "message": "menu updated", "data": {}}, 200


# update menu stock
@app.put("/menu/stock/<int:m_id>")
@auth.login_required(role=["admin", "cashier"])
def update_menu_stock(m_id):
    data = request.get_json()
    menu = Menu.query.get(m_id)
    menu.stock = data.get("stock", menu.stock)
    db.session.commit()
    return {"success": True, "message": "menu stock updated", "data": {}}, 200


# search menu
@app.get("/menusearch")
@auth.login_required(role=["cashier", "member"], optional=True)
def menu_search():
    args = request.args
    q = Menu.query
    if "name" in args.keys():
        q = q.filter(Menu.name.ilike(f"%{args['name']}%"))
    menu_list = q.all()
    results = [
        {
            "name": menu.name,
            "id": menu.id,
            "img_url": menu.img_url,
        }
        for menu in menu_list
        if menu.stock > 0
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"results": results},
    }, 200


# create order
@app.post("/order/member")
@auth.login_required(role=["cashier", "member"])
def create_order_member():
    active_orders = Order.query.filter_by(status="created").count()
    if active_orders > 10:
        return {
            "success": False,
            "message": "We apologize, our service is busy at the moment 🙏🏻 Please kindly wait 😊",
            "data": {},
        }, 400
    items = request.get_json()["order_items"]
    member = auth.current_user()
    new_order = Order(
        user_id=member.id,
        customer_name=member.name,
        status="created",
        created_date=datetime.now(),
    )
    db.session.add(new_order)
    db.session.commit()
    total_bill = 0
    for item in items:
        menu = Menu.query.get(item["menu_id"])
        new_item = Order_Items(
            order_id=new_order.id,
            menu_id=item["menu_id"],
            menu_name=menu.name,
            quantity=item["quantity"],
        )
        total_bill += menu.price * item["quantity"]
        new_order.order_items.append(new_item)
    new_order.total_bill = total_bill
    db.session.commit()
    return {
        "success": True,
        "message": "Order created",
        "data": {"total_bill": total_bill, "order_id": new_order.id},
    }, 201


# order details
@app.get("/order/<int:o_id>")
@auth.login_required(role=["member", "cashier"])
def get_order(o_id):
    # order = Order.query.get(o_id)
    order = db.session.get(Order, o_id)
    details = {
        "order_id": order.id,
        "created_at": order.created_date,
        "items": [
            {"name": item.menu_name, "qty": item.quantity} for item in order.order_items
        ],
        "total_bill": order.total_bill,
        "status": order.status
    }
    return {
        "success": True,
        "message": "Data found",
        "data": {"details": details},
    }, 200


# complete order
@app.put("/order/member/<int:o_id>")
@auth.login_required(role="member")
def complete_order_member(o_id):
    user = auth.current_user()
    order = Order.query.get(o_id)
    if user.balance < order.total_bill:
        return {
            "success": False,
            "message": "Unsufficient balance",
            "data": {},
        }, 400
    order.status = "completed"
    order.completed_date = datetime.now()

    # reduce stock
    for item in order.order_items:
        menu = Menu.query.get(item.menu_id)
        menu.stock -= item.quantity

    # reduce balance
    user.balance -= order.total_bill
    
    # insert balance transaction
    new_record = Balance_Record(
        user_id=user.id,
        order_id=order.id,
        nominal=order.total_bill,
        completed_date=datetime.now(),
        status="completed",
        type="payment",
    )
    db.session.add(new_record)
    db.session.commit()
    return {
        "success": True,
        "message": "Order completed",
        "data": {},
    }, 200


# balance top-up
@app.post("/balance/topup")
@auth.login_required(role="member")
def create_top_up():
    data = request.get_json()
    if data["nominal"] < 10000:
        return {
            "success": False,
            "message": "Minimum top-up is 10000",
            "data": {},
        }, 400
    user = auth.current_user()
    new_record = Balance_Record(
        user_id=user.id,
        nominal=data["nominal"],
        created_date=datetime.now(),
        status="created",
        type="topup",
    )
    db.session.add(new_record)
    db.session.commit()
    return {
        "success": True,
        "message": "Top-up created",
        "data": {},
    }, 200


# balance top-up
@app.put("/balance/topup/<int:b_id>")
@auth.login_required(role="admin")
def complete_top_up(b_id):
    record = Balance_Record.query.get(b_id)
    user = User.query.get(record.user_id)
    user.balance = record.nominal
    record.completed_date = datetime.now()
    record.status = "completed"
    db.session.commit()
    return {
        "success": True,
        "message": "Top-up completed",
        "data": {},
    }, 200


if __name__ == "__main__":
    app.run(debug=True)
