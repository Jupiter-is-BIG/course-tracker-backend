# UBC Course Tracker
This is a course tracking server side application for UBC courses. Suppose you want to register in a course COSC 111 001 for instance, but all the seats are full. Instead of checking SSC every other hour for a seat availablity, simply subscribe to the course on our server and get a discord bot notification as soon as a seat is available. We scrape and look for course availablilty every 20 minutes respecting UBC's Terms of Use Section F [TOS](https://www.ubc.ca/site/legal.html)

Discord Server: [https://discord.gg/ZbD4hjnc](https://discord.gg/ZbD4hjnc)

## Tech Stack
In this open source project, we use FastAPI for the backend with PostgresSQL for the database with SQLAlcemy ORM to interact with the database in addition to Alembic for database migration.

### Build Command
```sh
pip install -r requirements.txt && alembic upgrade head
```

### Deploy Command
```sh
uvicorn app.main:app --host 0.0.0.0 --reload
```

## API v0.0.1 Documentation
The documentation for the API can be found at [https://course-tracker-backend.onrender.com/docs](https://course-tracker-backend.onrender.com/docs)