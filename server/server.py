import atexit
import threading

from flask import Flask, render_template, jsonify
from flask import request

from busses import Busses

app = Flask(__name__)
stop_event = threading.Event()


@app.route("/")
def dashboard():
    app.busses.update()
    return render_template("dashboard.html", busses=app.busses.busses, show_hidden=False)


@app.route("/hidden")
def dashboard_hidden():
    app.busses.update()
    return render_template("dashboard.html", busses=app.busses.busses, show_hidden=True)



@app.route("/scrape_new")
def reload_data():
    logs = app.busses.reload()
    return "Data reloaded successfully!"




@app.route("/update_bids")
def update_bids():
    logs = app.busses.update_bids()
    return "Bid data updated successfully!"

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


@app.route("/bids")
def show_bids():
    return jsonify(app.busses.bids)


@app.route("/bids/<bus_id>")
def show_bid(bus_id):
    return jsonify(app.busses.bids.get(bus_id, []))


@app.route("/note/<bus_id>", methods=['POST', "GET"])
def notes(bus_id):
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        note = request_data.get("note", "")
        if bus_id in app.busses.bids:
            app.busses.busses[bus_id]['note'] = note
            app.busses.new_data = True
            app.busses.save_data()
            return f"Note added to bus {bus_id}: {note}"
    return jsonify(app.busses.busses.get(bus_id, {}).get("note", ""))


@atexit.register
def teardown():
    stop_event.set()
    app.busses.join()



if __name__ == "__main__":
    busses = Busses(stop_event)
    busses.start()
    app.busses = busses
    app.run(debug=True, host='0.0.0.0', port=5000)
