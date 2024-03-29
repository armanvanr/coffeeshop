# Coffeeverse API Documentation
> *Coffeeverse, explore the flavor across the multiverse*
<br/>
Coffeeverse is a RESTful API server built with Flask. Coffeeverse was designed as a mini project to complete the backend course held by Makers Institute.

## Entity Relationship Diagram (ERD)
![ERD of Coffeeverse API Server](./sql/coffeeshop-erd.png)

## Main Module and Extensions
- [Flask](https://flask.palletsprojects.com/en/2.3.x/): a web application framework written in Python
- [psycopg2](https://pypi.org/project/psycopg2/): PostgreSQL database adpater for Python
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/): Extension to simplify using SQLAlchemy with Flask
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/): Extension to handle SQLAlchemy migration for Flask App using Alembic
- [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/en/1.0.1/): Extension that provides bcrypt hashing utilities
- [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/): Extension that simplifies the use of HTTP authentication with Flask routes

## Running Application
1. Clone repository
```bash
$ git clone https://github.com/armanvanr/coffeeshop.git
```
2. Install the required modules
 - Create virtual environment (if using VSCode)
```bash
python.exe -m venv yourvenvname
```
 - Activate venv
```bash
yourvenvname\Scripts\activate
```
 - Install the requirement
```bash
$ pip install -r requirements.txt
```
3. Setup Database Configurations
 - Environment variables <br/>
    In the root directory, create a `.env` file containing `USER_NAME` and `PASSWORD` of database engine
```dosini
# .env
USER_NAME = postgres #bydefault
PASSWORD = password123
```
```python
# app.py
from dotenv import load_dotenv
from os import environ

load_dotenv()
db_username = environ["USER_NAME"]
db_password = environ["PASSWORD"]
db_name = coffeeshop
...
```
 - Database URI <br/>
    Create a new database in the PGAdmin and put the database name at the end of URI `app.config["SQLALCHEMY_DATABASE_URI"]`
```python
# app.py
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_username}:{db_password}@localhost:5432/{db_name}"
...
```
4. Migrate your application by running command
 - Initiate migration
```bash
$ flask db init
```
 - Add a new migration
```bash
$ flask db migrate
```
 - Upgrade the migration
```bash
$ flask db upgrade
```
5. Start Flask App by running command
```bash
$ flask run
```

## API Endpoints

| Number | Access                    | Feature                    | Description                                                                                                                                                                          | Method | URL                  | Request Body                                      | Query      | Response                                                                                                                                                                                                                                                              |
| ------ | ------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ | -------------------- | ------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1      | non-registered users      | Register new user          | register a new member/admin                                                                                                                                                          | POST   | /user                | name, email, password, role                       |            | Error (400):<br>"message": "Email already exists"<br>Success (201):<br>"message": "Account successfully created"                                                                                                                                                      |
| 2      | member, admin             | Update user data           | update user name or password                                                                                                                                                         | PUT    | /user/<id>           | name, email, password                             |            | success: updated                                                                                                                                                                                                                                                      |
| 3      | admin                     | Show all users             | show user details (name, email, balance)                                                                                                                                             | GET    | /users/all           |                                                   |            | Success (200):<br>"message": "Data found",<br>"data": {<br>  "users": [{<br>    "name": user.name,<br>     "id": user.id,<br>     "balance": user.balance,<br>     "email": user.email,<br>     "role": user.role,<br>     "password": user.password,<br>     }]<br>} |
| 4      | admin                     | Show top 5 customers order | get 5 users who create orders the most, sort descending                                                                                                                              | GET    | /users/top5/order    |                                                   |            | Error (400):<br>"message": "Incorrect old password"<br>Success (200):<br>"message": "Account data updated"                                                                                                                                                            |
| 5      | admin                     | Show top 5 customers spend | Users who spend money the most, sort descending                                                                                                                                      | GET    | /users/top5/spend    |                                                   |            |                                                                                                                                                                                                                                                                       |
| 6      | admin                     | Add new menu               | name, description, price                                                                                                                                                             | POST   | /menu                | name, description, price                          |            |                                                                                                                                                                                                                                                                       |
| 7      | all, including non member | Get all menu               | Only display menu that is in-stock by default                                                                                                                                        | GET    | /menu/all            |                                                   | name       |                                                                                                                                                                                                                                                                       |
| 8      | all, including non member | Show top 5 menu            | Ordered most ordered                                                                                                                                                                 | GET    | /menu/top5           |                                                   |            |                                                                                                                                                                                                                                                                       |
| 9      | all, including non member | Search menu                | Only display menu that is in-stock by default                                                                                                                                        | GET    | /menu/search         |                                                   | name, desc |                                                                                                                                                                                                                                                                       |
| 10     | all, including non member | Show menu details          | Show details of specific menu                                                                                                                                                        | GET    | /menu/<id>           |                                                   |            | Details: name, description, price, stock, img_url                                                                                                                                                                                                                     |
| 11     | admin                     | Show lowstock menu         | get all menu items whose stock is 10 or less                                                                                                                                         | GET    | /menu/lowstock       |                                                   |            |                                                                                                                                                                                                                                                                       |
| 12     | admin                     | Update menu stock          | update menu stock                                                                                                                                                                    | PUT    | /menu/<id>           | stock                                             |            |                                                                                                                                                                                                                                                                       |
| 13     | admin                     | Update menu data           | update menu (name, description, image, price)                                                                                                                                        | PUT    | /menu/<id>           | name, description, price                          |            |                                                                                                                                                                                                                                                                       |
| 14     | member                    | Create order               | Check if balance exceeds total bill.<br>Before create, re-check if stock is still available.<br>Max only 10 active orders can be served by shop, otherwise order is in waiting list. | POST   | /order/create        | menu: {menu_item:quantity}, user_id,              |            | Order details (menu, quantity, bill, total bill, status)                                                                                                                                                                                                              |
| 15     | admin                     | Show all created orders    | Show created orders (waiting-list or in-process) ordered by created date                                                                                                             | GET    | /orders              | ?status=in-process,<br>OR<br>?status=waiting-list |            |                                                                                                                                                                                                                                                                       |
| 16     | member                    | Show order details         | Show total bills, ordered items                                                                                                                                                      | GET    | /order/details/<id>  |                                                   |            | order_id, ordered items (name) and its quantity, created date                                                                                                                                                                                                         |
| 17     | admin                     | Complete order             | Stock is decreased, change the oldest waiting-list to in-process                                                                                                                     | PUT    | /order/complete/<id> | status: completed,<br>reduce stock                |            | completed, order invoice                                                                                                                                                                                                                                              |
| 18     | member                    | Cancel order               | delete order, autorefund                                                                                                                                                             | PUT    | /order/cancel/<id>   | status: cancelled, auto refund                    |            | cancelled                                                                                                                                                                                                                                                             |
| 19     | member                    | Create balance top up      | send money to be kept by shop. Minimum nominal 10000                                                                                                                                 | POST   | /balance/topup       | nominal: integer value                            |            |                                                                                                                                                                                                                                                                       |
| 20     | admin                     | Get all top up requests    | See all top up request (status created)                                                                                                                                              | GET    | /balance/topup       |                                                   |            |                                                                                                                                                                                                                                                                       |
| 21     | admin                     | Completed balance top up   | approved by admin                                                                                                                                                                    | PUT    | /balance/topup/<id>  |                                                   |            |                                                                                                                                                                                                                                                                       |