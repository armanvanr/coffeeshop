# Coffeeverse API Documentation

Coffeeverse is a RESTful API server built with Flask. Coffeeverse was designed as a mini project to complete the backend course held by Makers Institute.

## Entity Relationship Diagram (ERD)
![ERD of Coffeeverse API Server](./sql/coffeeshop-erd.png)

### Main Module and Extensions
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [psycopg2](https://pypi.org/project/psycopg2/): PostgreSQL database adpater for Python
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/): Extension to handle SQLAlchemy migration for Flask App using Alembic
- [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/en/1.0.1/): Extension that provides bcrypt hashing utilities
- [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/): Extension that simplifies the use of HTTP authentication with Flask routes

## Running Application
1. Clone repository
```
$ git clone https://github.com/armanvanr/coffeeshop.git
```
2. Install the required modules
    1. Create virtual environment (if using VSCode)
    ```
    python.exe -m venv yourvenvname
    ```
    2. Activate venv
    ```
    yourvenvname\Scripts\activate
    ```
    3. Install the requirement
    ```
    $ pip install -r requirements.txt
    ```
3. Setup Database Configurations
    1. Environment variables
    In the root directory, create a `.env` file containing `USER_NAME` and `PASSWORD` of database engine
    ```
    # .env
    USER_NAME = postgres #bydefault
    PASSWORD = password123
    ```
    ```
    # app.py
    from dotenv import load_dotenv
    from os import environ

    load_dotenv()
    db_username = environ["USER_NAME"]
    db_password = environ["PASSWORD"]
    db_name = coffeeshop
    ....
    ```
    2. Setup Database URI
    Create a new database in the PGAdmin and put the database name at the end of URI `app.config["SQLALCHEMY_DATABASE_URI"]`
    ```
    # app.py
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_username}:{db_password}@localhost:5432/{db_name}"
    ....
    ```
4. Migrate your application by running command
    1. Initiate Migration
    ```
    $ flask db init
    ```
    2. Add a new migration
    ```
    $ flask db migrate
    ```
    3. Upgrade the migration
    ```
    $ flask db upgrade
    ```
5. Start Flask App by running command
```
$ flask run
```

## API Endpoints

