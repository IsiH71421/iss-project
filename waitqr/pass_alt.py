from skyfield.api import Topos, load, EarthSatellite, wgs84
from datetime import timedelta
from zoneinfo import ZoneInfo
import requests
import numpy as np

# Standort Garching
latitude = 48.262839
longitude = 11.666853
elevation_m = 0

# TLE-Daten von Celestrak (Stations)
TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"
tle_text = requests.get(TLE_URL).text.splitlines()

# ISS TLE auslesen
for i, line in enumerate(tle_text):
    if "ISS" in line.upper():
        name = line.strip()
        tle_line1 = tle_text[i + 1].strip()
        tle_line2 = tle_text[i + 2].strip()
        break
else:
    raise ValueError("ISS nicht gefunden in TLE-Daten.")

# Skyfield Setup
ts = load.timescale()
satellite = EarthSatellite(tle_line1, tle_line2, name, ts)
observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation_m)
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']

# Zeitraum: Jetzt bis 7 Tage in die Zukunft
now = ts.now()
t0 = now
t1 = ts.utc(now.utc_datetime() + timedelta(days=7))

# Zeitzone Europa/Berlin
berlin_tz = ZoneInfo("Europe/Berlin")

# Finde Überflüge (Events: Aufgang, Maximum, Untergang)
times, events = satellite.find_events(observer, t0, t1, altitude_degrees=10.0)

for i in range(0, len(events), 3):
    if i + 2 >= len(events):
        break  # unvollständiger Pass, abbrechen

    rise_time = times[i]
    max_time = times[i + 1]
    set_time = times[i + 2]

    # Maximale Elevation
    alt, az, _ = (satellite - observer).at(max_time).altaz()
    max_elev = alt.degrees

    # Zeitpunkte im Überflugfenster alle 30 Sekunden
    duration_seconds = int((set_time.utc_datetime() - rise_time.utc_datetime()).total_seconds())
    steps = max(1, duration_seconds // 10)
    sample_times = ts.utc([
        (rise_time.utc_datetime() + timedelta(seconds=sec)) for sec in np.linspace(0, duration_seconds, steps)
    ])

    visible = False
    for t in sample_times:
        # ISS Position und Sonnenhöhe an diesem Zeitpunkt
        iss_position = satellite.at(t)
        subpoint = wgs84.subpoint(iss_position)
        iss_observer = wgs84.latlon(latitude_degrees=subpoint.latitude.degrees,
                                    longitude_degrees=subpoint.longitude.degrees,
                                    elevation_m=subpoint.elevation.m)
        iss_location = earth + iss_observer
        sun_alt_at_iss = iss_location.at(t).observe(sun).apparent().altaz()[0].degrees
        iss_lit = sun_alt_at_iss > -20.0

        # Sonnenhöhe am Boden
        obs_pos = earth + observer
        sun_alt = obs_pos.at(t).observe(sun).apparent().altaz()[0].degrees
        observer_in_darkness = sun_alt < -4.0

        if iss_lit and observer_in_darkness:
            visible = True
            break

    # Ausgabezeiten in CEST
    rise_local = rise_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
    max_local = max_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
    set_local = set_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)

    # Ausgabe
    print("🛰 ISS-Überflug:")
    print(f"   Beginn     : {rise_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Maximum    : {max_local.strftime('%Y-%m-%d %H:%M:%S %Z')} ({max_elev:.1f}°)")
    print(f"   Ende       : {set_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Dauer      : {duration_seconds // 60} min {duration_seconds % 60} sec")
    print(f"   Sichtbar   : {'✅ Ja' if visible else '❌ Nein'}")
    print("-" * 50)
