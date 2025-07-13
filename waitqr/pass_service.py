from flask import Flask, jsonify, request
from skyfield.api import Topos, load, EarthSatellite, wgs84
from datetime import timedelta
from zoneinfo import ZoneInfo
import requests
import numpy as np

app = Flask(__name__)

# --- Konstanten und Initialisierung ---
latitude = 48.262839
longitude = 11.666853
elevation_m = 0
berlin_tz = ZoneInfo("Europe/Berlin")

# Skyfield Setup
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']

observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation_m)

def load_satellite():
    TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"
    tle_text = requests.get(TLE_URL).text.splitlines()
    for i, line in enumerate(tle_text):
        if "ISS" in line.upper():
            name = line.strip()
            tle_line1 = tle_text[i + 1].strip()
            tle_line2 = tle_text[i + 2].strip()
            return EarthSatellite(tle_line1, tle_line2, name, ts)
    raise ValueError("ISS nicht gefunden in TLE-Daten.")

satellite = load_satellite()


def find_passes(days=7):
    now = ts.now()
    t0 = now
    t1 = ts.utc(now.utc_datetime() + timedelta(days=days))

    times, events = satellite.find_events(observer, t0, t1, altitude_degrees=10.0)
    passes = []

    for i in range(0, len(events), 3):
        if i + 2 >= len(events):
            break  # unvollständiger Pass

        rise_time = times[i]
        max_time = times[i + 1]
        set_time = times[i + 2]

        alt, az, _ = (satellite - observer).at(max_time).altaz()
        max_elev = alt.degrees

        duration_seconds = int((set_time.utc_datetime() - rise_time.utc_datetime()).total_seconds())
        steps = max(1, duration_seconds // 10)
        sample_times = ts.utc([
            (rise_time.utc_datetime() + timedelta(seconds=sec)) for sec in np.linspace(0, duration_seconds, steps)
        ])

        visible = False
        for t in sample_times:
            iss_position = satellite.at(t)
            subpoint = wgs84.subpoint(iss_position)
            iss_observer = wgs84.latlon(latitude_degrees=subpoint.latitude.degrees,
                                        longitude_degrees=subpoint.longitude.degrees,
                                        elevation_m=subpoint.elevation.m)
            iss_location = earth + iss_observer
            sun_alt_at_iss = iss_location.at(t).observe(sun).apparent().altaz()[0].degrees
            iss_lit = sun_alt_at_iss > -20.0

            obs_pos = earth + observer
            sun_alt = obs_pos.at(t).observe(sun).apparent().altaz()[0].degrees
            observer_in_darkness = sun_alt < -4.0

            if iss_lit and observer_in_darkness:
                visible = True
                break

            rise_local = rise_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
            max_local = max_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
            set_local = set_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)

            passes.append({
                "start": rise_local.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "max": max_local.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "end": set_local.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "max_elevation_deg": round(max_elev, 1),
                "duration_sec": duration_seconds,
                "visible": visible
            })

    return passes

@app.route('/passes')
def passes_endpoint():
    days_str = request.args.get('days', '7')
    try:
        days = int(days_str)
        if days < 1 or days > 7:
            return jsonify({"error": "days must be between 1 and 7"}), 400
    except ValueError:
        return jsonify({"error": "Invalid days parameter"}), 400

    passes = find_passes(days=days)
    return jsonify(passes)

@app.route('/next_pass')
def next_pass_endpoint():
    passes = find_passes(days=7)
    if passes:
        return jsonify(passes[0])
    else:
        return jsonify({"error": "No passes found"}), 404


if __name__ == "__main__":
    # Server starten, von außen erreichbar auf Port 5000
    app.run(host='0.0.0.0', port=5000)
