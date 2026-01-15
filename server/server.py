import jinja2
from flask import Flask, render_template, jsonify

from busses import Busses

app = Flask(__name__)


@app.route("/")
def dashboard():
    app.busses.update()
    return render_template("dashboard.html", busses=app.busses.busses)


@app.route("/scrape_new")
def reload_data():
    logs = app.busses.reload()
    return "Data reloaded successfully!"


@app.route("/bus/<bus_id>")
def bus_data(bus_id):
    return jsonify(app.busses.busses.get(bus_id, {}))


@app.route("/hide/<bus_id>")
def hide_bus(bus_id):
    app.busses.hide_bus(bus_id)
    return f"Bus {bus_id} hidden"


@app.route("/details/<bus_id>")
def bus_details(bus_id):
    details = app.busses.get_bus_details(bus_id)
    return jsonify(details)


if __name__ == "__main__":
    busses = Busses()
    app.busses = busses
    app.run(debug=True)
