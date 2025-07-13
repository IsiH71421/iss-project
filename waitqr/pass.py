from skyfield.api import Topos, load, EarthSatellite, wgs84
from datetime import timedelta
from zoneinfo import ZoneInfo  # für Zeitzonenumwandlung
import requests

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

# Zeitraum: Jetzt bis 2 Tage in die Zukunft
now = ts.now()
t0 = now
t1 = ts.utc(now.utc_datetime() + timedelta(days=2))

# Zeitzone Europa/Berlin (automatisch CEST oder MEZ)
berlin_tz = ZoneInfo("Europe/Berlin")

# Finde Überflüge (Events: Aufgang, Maximum, Untergang)
times, events = satellite.find_events(observer, t0, t1, altitude_degrees=10.0)

for i in range(0, len(events), 3):
    if i + 2 >= len(events):
        break  # unvollständiger Pass, abbrechen

    rise_time = times[i].utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
    max_time = times[i + 1].utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
    set_time = times[i + 2].utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)

    # Maximale Elevation über Beobachter
    alt, az, _ = (satellite - observer).at(times[i + 1]).altaz()
    max_elev = alt.degrees

    # Position der ISS zur max Zeit
    iss_position = satellite.at(times[i + 1])

    # Koordinaten der ISS (lat, lon, Höhe)
    subpoint = wgs84.subpoint(iss_position)
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees
    elevation = subpoint.elevation.m

    # Beobachter-Objekt an ISS-Position
    iss_observer = wgs84.latlon(latitude_degrees=lat,
                                longitude_degrees=lon,
                                elevation_m=elevation)

    # Sonnenhöhe aus Sicht der ISS
    iss_location = earth + iss_observer
    sun_alt_at_iss = iss_location.at(times[i + 1]).observe(sun).apparent().altaz()[0].degrees
    iss_lit = sun_alt_at_iss > 0.0  # ISS wird von Sonne beleuchtet

    # Sonnenhöhe aus Sicht des Bodenbeobachters
    obs_pos = earth + observer
    sun_apparent = obs_pos.at(times[i + 1]).observe(sun).apparent()
    sun_alt = sun_apparent.altaz()[0].degrees
    observer_in_darkness = sun_alt < 0.0  # Sonnenuntergang

    # Sichtbarkeit des Überflugs: ISS beleuchtet & Boden dunkel
    visible = iss_lit and observer_in_darkness

    # Ausgabe
    print("🛰 ISS-Überflug:")
    print(f"   Beginn     : {rise_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Maximum    : {max_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ({max_elev:.1f}°)")
    print(f"   Ende       : {set_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    duration = int((times[i + 2].utc_datetime() - times[i].utc_datetime()).total_seconds())
    print(f"   Dauer      : {duration // 60} min {duration % 60} sec")
    print(f"   Sichtbar   : {'✅ Ja' if visible else '❌ Nein'}")
    print("-" * 50)
