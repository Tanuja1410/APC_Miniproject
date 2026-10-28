# TripSplit

TripSplit is a beginner-friendly group trip expense manager. It has a command-line app, a Tkinter desktop GUI, and a Django website. The desktop app stores its trip in `data/trip.json`; the website stores trips in `web/db.sqlite3`.

## Install

Run from the project folder:

```powershell
python -m pip install -r requirements.txt
```

## Django website

```powershell
cd web
python manage.py migrate --fake-initial
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, create an account with a username and password, then log in. The `--fake-initial` option safely recognizes the original website tables if you already created them before migrations were added.

The dashboard lets you select or create a trip, add members and expenses, choose who shares each expense, view balances and settlements, and refresh saved data. A report can be viewed, printed, or downloaded. If an old expense has no saved participant list, the report splits it across the trip's members.

Run the website tests from the `web` folder:

```powershell
python manage.py test trips
```

## Desktop GUI

Run this from the project folder:

```powershell
python launch_gui.py
```

Use **Save** to save trip name and budget changes. **Refresh** reloads the saved trip and shows its totals. Members and expenses are saved when they are added. Desktop reports remain available from the command-line app.

## Other demos

```powershell
python main.py
python concepts_demo.py
python pygame_demo.py
```

Charts and desktop reports are saved under `reports/`. The desktop data and Django database are separate.
