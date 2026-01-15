from flask import Flask, render_template

from busses import Busses

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("dashboard.html", busses=app.busses.busses)


@app.route("/scrape_new")
def reload_data():
    logs = app.busses.reload()
    return "Data reloaded successfully!"


if __name__ == "__main__":
    busses = Busses()
    app.busses = busses
    app.run(debug=True)
