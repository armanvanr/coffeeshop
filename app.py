from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from dotenv import load_dotenv
from os import environ
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from datetime import datetime
import json

load_dotenv()
db_username = environ["USER_NAME"]
db_password = environ["PASSWORD"]

app = Flask(__name__)
CORS(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{db_username}:{db_password}@localhost:5432/coffeeshop"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth(app)


# Model of Tables and Relationships
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    role = db.Column(db.String, nullable=False)
    cart = db.Column(db.String, nullable=True)

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
    cancelled_date = db.Column(db.DateTime, nullable=True)
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
    member_name = db.Column(db.String, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=True)
    nominal = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}>"


# Authentication
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(email=username).first()

    # user with that email not found, call Error Auth Handler
    if not user:
        return False

    # check password
    is_valid = bcrypt.check_password_hash(user.password, password)

    # password correct, call Authorization
    if is_valid:
        return user

    # password incorrect, call Error Auth Handler
    else:
        return False


# Authorization
@auth.get_user_roles
def get_user_roles(user):
    roles = user.role
    return roles


# Auth Error Handler
@auth.error_handler
def error_handlers(code):
    # handle if user not exists or incorrect password
    if code == 401:
        return {"success": False, "message": "Unauthorized", "data": {}}, code

    # handle if user with specified role has no right to access
    elif code == 403:
        return {"success": False, "message": "Forbidden", "data": {}}, code


# Routes
@app.get("/")
def welcome():
    return {"success": True, "message": "Welcome to Coffee Shop API", "data": {}}


# user login
@app.post("/user/login")
def login():
    username = request.authorization["username"]
    password = request.authorization["password"]

    user = User.query.filter_by(email=username).first()

    # user with that email not found, call Error Auth Handler
    if not user:
        return {"success": False, "message": "User not found", "data": {}}, 404

    # check password
    is_valid = bcrypt.check_password_hash(user.password, password)

    # password correct, call Authorization
    if is_valid:
        cart = json.loads(user.cart)["cartData"]
        return {
            "success": True,
            "message": "User found",
            "data": {
                "name": user.name,
                "email": user.email,
                "balance": user.balance,
                "cart": cart,
                "role": user.role,
            },
        }, 200

    # password incorrect, call Error Auth Handler
    else:
        return {"success": False, "message": "Unauthorized", "data": {}}, 401

# admin login
@app.post("/admin/login")
def admin_login():
    username = request.authorization["username"]
    password = request.authorization["password"]

    user = User.query.filter_by(email=username).first()

    # user with that email not found, call Error Auth Handler
    if not user:
        return {"success": False, "message": "Data not found", "data": {}}, 404

    # check password
    is_valid = bcrypt.check_password_hash(user.password, password)

    # password correct, call Authorization
    if is_valid and user.role == "admin":
        return {
            "success": True,
            "message": "Sign In Successful",
            "data": {
                "name": user.name,
                "email": user.email,
            },
        }, 200

    # password corret, but not admin
    elif is_valid and user.role != "admin":
        return {"success": False, "message": "You have no access", "data": {}}, 403
    
    # password incorrect, call Error Auth Handler
    else:
        return {"success": False, "message": "Incorrect password", "data": {}}, 401


# register a new user
@app.post("/user/register")
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
        cart=json.dumps({"cartData": []}),
    )
    db.session.add(new_user)
    db.session.commit()
    return {"success": True, "message": "Account created successfully", "data": {}}, 201


# log out and save cart data
@app.put("/user/logout")
def logout():
    data = request.get_json()
    email = data["userData"]["email"]
    user = db.session.query(User).filter_by(email=email).first()
    user.cart = json.dumps({"cartData": data["cartData"]})
    db.session.commit()

    return {"success": True, "message": "Logged out", "data": {}}, 200


# change name or password of member or admin
@app.put("/user/update")
# @auth.login_required(role=["member", "admin"])
def update_user():
    data = request.get_json()
    # user = auth.current_user()
    user = db.session.query(User).filter_by(email=data["email"]).first()
    user.name = data.get("name", user.name)

    # handle to change password
    if "new_password" in data.keys():
        is_valid = bcrypt.check_password_hash(user.password, data["old_password"])
        if is_valid:
            hash_pw = bcrypt.generate_password_hash(data["new_password"]).decode(
                "utf-8"
            )
            user.password = hash_pw
        else:
            return {
                "success": False,
                "message": "Incorrect old password",
                "data": {},
            }, 400
    db.session.commit()
    return {"success": True, "message": "Account data updated", "data": {}}, 200


# show all users
@app.get("/users/all")
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


# show top 5 users most frequently create orders
@app.get("/users/top5/order")
# @auth.login_required(role="admin")
def show_top_user_order():
    users = (
        db.session.query(
            Order.customer_name, User.email, func.count(Order.customer_name).label("times")
        )
        .join(
            Order,
            Order.user_id == User.id,
        )
        .filter(Order.status == "completed")
        .group_by(Order.customer_name, User.email)
        .order_by(func.count(Order.customer_name).desc())
        .limit(5)
    )
    return {
        "success": True,
        "message": "Data found",
        "data": {
            "members": [
                {
                    # "id": user.id,
                    "name": user.customer_name,
                    "email": user.email,
                    "order_times": user.times,
                }
                for user in users
            ]
        },
    }, 200


# show top 5 users highest spend
@app.get("/users/top5/spend")
# @auth.login_required(role="admin")
def show_top_user_spend():
    users = (
        db.session.query(Order.customer_name, User.email, func.sum(Order.total_bill).label("bill"))
        .join(
            Order,
            Order.user_id == User.id,
        )
        .filter(Order.status == "completed")
        .group_by(Order.customer_name, User.email)
        .order_by(func.sum(Order.total_bill).desc())
        .limit(5)
    )
    return {
        "success": True,
        "message": "Data found",
        "data": {
            "members": [
                {
                    # "id": user.id,
                    "name": user.customer_name,
                    "email": user.email,
                    "bill_sum": user.bill,
                }
                for user in users
            ]
        },
    }, 200


# add a new menu
@app.post("/menu")
# @auth.login_required(role="admin")
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
    return {"success": True, "message": "Menu successfully added", "data": {}}, 201


# show all in-stock menu
@app.get("/menu/available")
def get_available_menu():
    drinks = [
        {
            "id": menu.id,
            "img_url": menu.img_url,
            "name": menu.name,
            "desc": menu.desc,
            "price": menu.price,
            "stock": menu.stock
        }
        for menu in Menu.query.filter(Menu.category == "drinks", Menu.stock > 0)
    ]
    foods = [
        {
            "id": menu.id,
            "img_url": menu.img_url,
            "name": menu.name,
            "desc": menu.desc,
            "price": menu.price,
            "stock": menu.stock
        }
        for menu in Menu.query.filter(Menu.category == "foods", Menu.stock > 0)
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"drinks": drinks, "foods": foods},
    }, 200


@app.get("/menu/all")
def get_all_menu():
    menu_list = [
        {
            "id": menu.id,
            "name": menu.name,
            "price": menu.price,
            "stock": menu.stock,
            "category": menu.category
        }
        for menu in db.session.query(Menu).order_by(Menu.name).all()
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"menu_list": menu_list},
    }, 200


# show top 5 menu items ordered the most
@app.get("/menu/top5")
def show_top_menu():
    base_query = (
        db.session.query(
            func.sum(Order_Items.quantity).label("qty"),
            Menu.name,
            Menu.desc,
            Menu.price,
            Menu.img_url,
            Menu.id,
            Menu.stock
        )
        .join(
            Order,
            Order.id == Order_Items.order_id,
        )
        .join(Menu, Order_Items.menu_id == Menu.id)
    )
    drink_items = (
        base_query.filter(Order.status == "completed", Menu.category == "drinks")
        .group_by(Menu.name, Menu.desc, Menu.price, Menu.img_url, Menu.id, Menu.stock)
        .order_by(func.sum(Order_Items.quantity).desc())
        .limit(5)
    )
    food_items = (
        base_query.filter(Order.status == "completed", Menu.category == "foods")
        .group_by(Menu.name, Menu.desc, Menu.price, Menu.img_url, Menu.id)
        .order_by(func.sum(Order_Items.quantity).desc())
        .limit(5)
    )
    return {
        "success": True,
        "message": "Data found",
        "data": {
            "drinks": [
                {
                    "id": item.id,
                    "name": item.name,
                    "desc": item.desc,
                    "price": item.price,
                    "img_url": item.img_url,
                    "qty": item.qty,
                    "stock": item.stock
                }
                for item in drink_items
            ],
            "foods": [
                {
                    "id": item.id,
                    "name": item.name,
                    "desc": item.desc,
                    "price": item.price,
                    "img_url": item.img_url,
                    "qty": item.qty,
                    "stock": item.stock
                }
                for item in food_items
            ],
        },
    }, 200

@app.get("/menu/top5/order")
def show_top_menu_order():
    menu_list = (
        db.session.query(
            Menu.name, Menu.price, func.sum(Order_Items.quantity).label("times")
        )
        .join(
            Order,
            Order.id == Order_Items.order_id,
        )
        .join(Menu, Order_Items.menu_id == Menu.id)
        .filter(Order.status == "completed")
        .group_by(Menu.name, Menu.price,)
        .order_by(func.sum(Order_Items.quantity).desc())
        .limit(5)
    )
    return {
        "success": True,
        "message": "Data found",
        "data": {
            "menu_list": [
                {
                    "name": item.name,
                    "price": item.price,
                    "times": item.times,
                }
                for item in menu_list
            ],
        },
    }, 200

# search menu
@app.get("/menu/search")
def menu_search():
    keyword = request.args["keyword"]
    menu_list = (
        Menu.query.filter(
            or_(Menu.name.ilike(f"%{keyword}%"), Menu.desc.ilike(f"%{keyword}%"))
        )
        .order_by(Menu.category)
        .all()
    )
    results = [
        {
            "id": menu.id,
            "name": menu.name,
            "desc": menu.desc,
            "price": menu.price,
            "img_url": menu.img_url,
            "category": menu.category,
            "stock": menu.stock
        }
        for menu in menu_list
        if menu.stock > 0
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"results": results},
    }, 200


# show a menu details
@app.get("/menu/<int:m_id>")
def get_menu(m_id):
    menu = db.session.query(Menu).get(m_id)
    details = {
        "name": menu.name,
        "id": menu.id,
        "img_url": menu.img_url,
        "price": menu.price,
        "desc": menu.desc,
        "stock": menu.stock,
        "category": menu.category
    }

    return {
        "success": True,
        "message": "Data found",
        "data": {"details": details},
    }, 200

# show a menu details
@app.get("/menu/stock/<int:m_id>")
def get_menu_stock(m_id):
    menu = db.session.query(Menu).get(m_id)
    return {
        "success": True,
        "message": "Data found",
        "data": {"stock": menu.stock},
    }, 200


# show menu items order by lowest stock
@app.get("/menu/lowstock")
# @auth.login_required(role="admin")
def get_low_stock():
    menu_list = [
        {
            "name": item.name,
            "price": item.price,
            "stock": item.stock,
        }
        for item in Menu.query.order_by(Menu.stock).limit(5)
    ]
    return {
        "success": True,
        "message": "Data retrieved",
        "data": {"menu_list": menu_list},
    }, 200


# update menu stock
@app.put("/menu/stock/<int:m_id>")
@auth.login_required(role="admin")
def update_menu_stock(m_id):
    data = request.get_json()
    menu = Menu.query.get(m_id)
    menu.stock = data.get("stock", menu.stock)
    # db.session.commit()
    return {"success": True, "message": "menu stock updated", "data": {}}, 200


# update menu data
@app.put("/menu/<int:m_id>")
# @auth.login_required(role="admin")
def update_menu(m_id):
    data = request.get_json()
    menu = Menu.query.get(m_id)
    menu.name = data.get("name", menu.name)
    menu.desc = data.get("desc", menu.desc)
    menu.price = data.get("price", menu.price)
    menu.img_url = data.get("img_url", menu.img_url)
    menu.stock = data.get("stock", menu.stock)
    menu.category = data.get("category", menu.category)
    db.session.commit()
    return {"success": True, "message": "menu updated", "data": {}}, 200

# get all order records
@app.get("/orders/all")
def get_all_orders():
    order_list = [
        {
            "id": order.id,
            "customer_name": order.customer_name,
            "total_bill": order.total_bill,
            "status": order.status,
            "created_date": order.created_date
        }
        for order in db.session.query(Order).order_by((Order.created_date).desc()).all()
    ]
    return {
        "success": True,
        "message": "Data found",
        "data": {"order_list": order_list},
    }, 200

# create order
@app.post("/order/create")
# @auth.login_required(role="member")
def create_order():
    items = request.get_json()["order_items"]
    # member = auth.current_user()
    member_email = request.get_json()["user_data"]["email"]
    member = db.session.query(User).filter_by(email=member_email).first()
    new_order = Order(
        user_id=member.id,
        customer_name=member.name,
        created_date=datetime.now(),
    )
    total_bill = 0
    for item in items:
        menu = Menu.query.get(item["menu_id"])
        if item["quantity"] > menu.stock:
            return {
                "success": False,
                "message": "Quantity of item(s) exceeds available stock",
                "data": {"order_item": menu.name, "stock": menu.stock},
            }, 400
        new_item = Order_Items(
            order_id=new_order.id,
            menu_id=item["menu_id"],
            menu_name=menu.name,
            quantity=item["quantity"],
        )
        menu.stock -= item["quantity"]
        total_bill += menu.price * item["quantity"]
        new_order.order_items.append(new_item)
    new_order.total_bill = total_bill
    active_orders = Order.query.filter_by(status="in-process").count()
    if active_orders >= 10:
        waiting_number = Order.query.filter_by(status="waiting-list").count() + 1
        new_order.status = "waiting-list"
        response_message = (
            f"We apologize, your order is in waiting list number: {waiting_number}"
        )
    else:
        new_order.status = "in-process"
        response_message = "Your order is being processed"
    db.session.add(new_order)
    # db.session.commit()
    if member.balance < total_bill:
        return {
            "success": False,
            "message": "Unsufficient balance",
            "data": {},
        }, 400
    # balance is reduced
    member.balance -= total_bill

    # insert balance transaction
    new_record = Balance_Record(
        user_id=member.id,
        member_name=member.name,
        order_id=new_order.id,
        nominal=total_bill,
        completed_date=datetime.now(),
        status="completed",
        type="payment",
    )
    db.session.add(new_record)
    # db.session.commit()
    return {
        "success": True,
        "message": response_message,
        "data": {
            "total_bill": total_bill,
            "order_id": new_order.id,
            "status": new_order.status,
        },
    }, 201


# see all waiting-list or in-process orders
@app.get("/orders/created")
@auth.login_required(role="admin")
def get_orders():
    args = request.args
    # add row number in query
    row_number = func.row_number().over(
        partition_by=Order.status, order_by=Order.created_date
    )
    q = db.session.query(Order).add_columns(row_number)

    # can only filter by either "in-progress" or "waiting-list" status
    # if filter status is omitted, it will result all orders including cancelled ones
    if "status" in args.keys():
        q = q.filter_by(status=args["status"])

    # queries in the form of list of tuples => [(order1, numb1), (order2, numb2)]
    queries = q.all()
    result = [
        {
            "order_id": order.id,
            "created_at": order.created_date,
            "order_number": number,
            "items": [
                {"name": item.menu_name, "qty": item.quantity}
                for item in order.order_items
            ],
            "total_bill": order.total_bill,
            "member_name": order.customer_name,
            "status": order.status,
        }
        for (order, number) in queries
    ]
    return {
        "success": True,
        "message": "Data retrieved",
        "data": {"orders": result},
    }, 200


# order details
@app.get("/order/details/<int:o_id>")
@auth.login_required(role="member")
def get_order(o_id):
    row_number = func.row_number().over(
        partition_by=Order.status, order_by=Order.created_date
    )
    query = db.session.query(Order).add_columns(row_number).filter_by(id=o_id).first()
    order = query[0]
    number = query[1]
    details = {
        "order_id": order.id,
        "order_number": number,
        "created_at": order.created_date,
        "items": [
            {"name": item.menu_name, "qty": item.quantity} for item in order.order_items
        ],
        "total_bill": order.total_bill,
        "status": order.status,
    }
    return {
        "success": True,
        "message": "Data found",
        "data": {"details": details},
    }, 200


# complete order
@app.put("/order/complete/<int:o_id>")
# @auth.login_required(role="admin")
def complete_order(o_id):
    order = Order.query.get(o_id)
    if order.status == "waiting-list":
        return {
            "success": False,
            "message": "Order is still in waiting-list",
            "data": {},
        }, 400
    order.status = "completed"
    order.completed_date = datetime.now()

    # reduce stock
    for item in order.order_items:
        menu = Menu.query.get(item.menu_id)
        menu.stock -= item.quantity

    # change the waiting-list into in-process
    query_waiting_list = (
        Order.query.filter_by(status="waiting-list")
        .order_by(Order.created_date)
        .limit(1)
        .all()
    )
    if query_waiting_list:
        new_active_order = query_waiting_list[0]
        new_active_order.status = "in-process"
    # db.session.commit()
    return {
        "success": True,
        "message": "Order completed",
        "data": {},
    }, 200


# cancel order and refund
@app.put("/order/cancel/<int:o_id>")
# @auth.login_required(role="member")
def cancel_order(o_id):
    order = Order.query.get(o_id)
    if order.status != "waiting-list":
        return {
            "success": False,
            "message": "Order cannot be cancelled",
            "data": {},
        }, 400
    # user = auth.current_user()
    data = request.get_json()
    user = db.session.query(User).filter_by(email=data["userData"]["email"]).first()
    order.status = "cancelled"
    order.cancelled_date = datetime.now()

    # refund
    user.balance += order.total_bill

    # insert balance transaction
    new_record = Balance_Record(
        user_id=user.id,
        member_name=user.name,
        order_id=order.id,
        nominal=0.8 * order.total_bill,
        completed_date=datetime.now(),
        status="completed",
        type="refund",
    )
    db.session.add(new_record)
    db.session.commit()
    return {
        "success": True,
        "message": "Order cancelled",
        "data": {},
    }, 200


# top-up balance
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
        member_name=user.name,
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


# get all uncomplete top-up
@app.get("/balance/topup")
@auth.login_required(role="admin")
def get_uncomplete_top_up():
    records = Balance_Record.query.filter_by(type="topup", status="created").all()
    requests = [
        {
            "record_id": record.id,
            "member_name": record.member_name,
            "nominal": record.nominal,
        }
        for record in records
    ]
    return {
        "success": True,
        "message": "Data retrieved",
        "data": {"requests": requests},
    }, 200


# approve top-up balance
@app.put("/balance/topup/<int:r_id>")
@auth.login_required(role="admin")
def complete_top_up(r_id):
    record = Balance_Record.query.get(r_id)
    user = User.query.get(record.user_id)
    if record.status == "completed":
        return {
            "success": False,
            "message": "Top-up already completed",
            "data": {},
        }, 400
    user.balance += record.nominal
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
