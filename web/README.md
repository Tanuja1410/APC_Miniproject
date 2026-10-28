# TripSplit Web App

From this folder, install the project dependencies and start Django:

```powershell
python -m pip install -r ..\requirements.txt
python manage.py migrate --fake-initial
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, create an account with a username and password, then log in.

Run the web workflow tests from this folder:

```powershell
python manage.py test trips
```

The web app saves data to `db.sqlite3` in this folder. Desktop app data is stored separately under the project-level `data/` folder.
