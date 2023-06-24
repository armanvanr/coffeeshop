# Coffeeverse API Documentation

Coffeeverse is a RESTful API server built with Flask. Coffeeverse was designed as a mini project to complete the backend course held by Makers Institute.

## Entity Relationship Diagram (ERD)
![ERD of Coffeeverse API Server](./sql/coffeeshop-erd.png)

### Main Module and Extensions
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
 - Environment variables
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
 - Setup Database URI
    Create a new database in the PGAdmin and put the database name at the end of URI `app.config["SQLALCHEMY_DATABASE_URI"]`
```python
# app.py
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_username}:{db_password}@localhost:5432/{db_name}"
...
```
4. Migrate your application by running command
 - Initiate Migration
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

### GET
`GET`[/users]
`GET`[/users/top5/spend]
`GET`[/users/top5/order]
`GET`[/menu]
`GET`[/menu/id]
`GET`[/menu/search]
`GET`[/menu/lowstock]
`GET`[/menu/top5]
`GET`[/orders]
`GET`[/order/details/id]

### POST
`POST` [/user]
`POST [/menu]`
`POST /order/create`
`POST/balance/topup`

### PUT
`PUT`[/user/update]
`PUT`[/menu/id]
`PUT`[/menu/stock/id]
`PUT`[/order/complete/id]
`PUT`[/order/cancel/id]
`PUT`[/balance/topup/id]