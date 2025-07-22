#!/usr/bin/python3
from flask import Flask, jsonify, request
from skyfield.api import Topos, load, EarthSatellite, wgs84
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import requests
import numpy as np
import threading
import os
import json

# Initialize Flask application
app = Flask(__name__)

# --- Configuration Constants ---
latitude = 48.262839        # Observer latitude in degrees (Garching Screen Location)
longitude = 11.666853       # Observer longitude in degrees (Garching Screen Location)
elevation_m = 481            # Observer elevation in meters above sea level (Garching Screen Location)
berlin_tz = ZoneInfo("Europe/Berlin")  # Local timezone
CACHE_FILE = 'passes_cache.json'       # File to cache calculated passes
CACHE_MAX_AGE_MINUTES = 60             # Cache expires after 60 minutes

# --- Skyfield Setup ---
ts = load.timescale()       # Skyfield timescale for accurate time calculations
eph = load('de421.bsp')     # JPL planetary ephemeris (includes Earth and Sun positions)
earth = eph['earth']        # Earth object for calculations
sun = eph['sun']            # Sun object for illumination calculations

# Create observer position object
observer_geodetic_position = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation_m)

# --- Satellite (ISS) Loading Function ---
def load_iss():
    """Download and parse Two-Line Element (TLE) data for the International Space Station."""
    TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"

    # Download TLE data from CelesTrak
    tle_text = requests.get(TLE_URL).text.splitlines()

    # Search for ISS in the TLE data
    for i, line in enumerate(tle_text):
        if "ISS" in line.upper():
            name = line.strip()                    # Satellite name
            tle_line1 = tle_text[i + 1].strip()   # First line of TLE data
            tle_line2 = tle_text[i + 2].strip()   # Second line of TLE data
            # Create and return an object representing the ISS to compute the ISS's real-time
            # position and trajectory to predict visible passes over the observer's location.
            return EarthSatellite(tle_line1, tle_line2, name, ts)

    raise ValueError("ISS not found in TLE data.")

# Load ISS satellite data at startup
iss = load_iss()

# --- Cache Management Functions ---
def cache_is_expired():
    """Check if the passes cache file is older than the maximum allowed age or doesn't exist."""
    if not os.path.exists(CACHE_FILE):
        return True

    # Check file modification time
    mtime = os.path.getmtime(CACHE_FILE)
    age = datetime.now().timestamp() - mtime
    return age > (CACHE_MAX_AGE_MINUTES * 60)

def save_passes_to_cache(passes):
    """Save calculated passes to cache file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(passes, f)

def load_passes_from_cache():
    """Load passes from cache file."""
    if not os.path.exists(CACHE_FILE):
        return []
    with open(CACHE_FILE, 'r') as f:
        return json.load(f)

def update_passes_cache():
    """Calculate new passes and update the cache file (run in a background thread)."""
    passes = find_passes(days=7)
    save_passes_to_cache(passes)

# --- Pass Calculation Function ---
def find_passes(days=7):
    """Calculate ISS passes for the next days."""
    # Set up time range for calculation
    now = ts.now()
    t0 = now
    t1 = ts.utc(now.utc_datetime() + timedelta(days=days))

    # Find events with minimum altitude of 10 degrees (otherwise passes are too low to observe)
    times, events = iss.find_events(observer_geodetic_position, t0, t1, altitude_degrees=10.0)
    passes = []

    # Process events in groups of 3: rise, culmination (max), set
    for i in range(0, len(events), 3):
        if i + 2 >= len(events):
            break  # Incomplete pass - skip

        # Extract the three key times for this pass
        rise_time = times[i]      # ISS rises above 10 degrees
        max_time = times[i + 1]   # ISS reaches maximum elevation
        set_time = times[i + 2]   # ISS sets below 10 degrees

        # Calculate maximum elevation angle during this pass
        alt, az, _ = (iss - observer_geodetic_position).at(max_time).altaz()
        max_elev = alt.degrees

        # Calculate total pass duration in seconds
        duration_seconds = int((set_time.utc_datetime() - rise_time.utc_datetime()).total_seconds())

        # --- Visibility Calculation ---
        # Sample multiple time points during the pass to check if ISS is visible
        steps = max(1, duration_seconds // 10)  # Sample every ~10 seconds
        sample_times = ts.utc([
            (rise_time.utc_datetime() + timedelta(seconds=sec)) for sec in np.linspace(0, duration_seconds, steps)
        ])

        visible = False
        for t in sample_times:
            # Get ISS position at this sample time
            iss_position = iss.at(t)

            # Get the subpoint on Earth (latitude, longitude, elevation) directly beneath the ISS at the
            # given time, using the WGS84 reference ellipsoid (standard Earth model).
            iss_subpoint = wgs84.subpoint(iss_position)

            # Define the ISS position using geodetic coordinates (latitude, longitude, altitude)
            # The latitude and longitude come from the subpoint; altitude is the ISS altitude (~400 km)
            iss_geodetic_position = wgs84.latlon(latitude_degrees=iss_subpoint.latitude.degrees,
                                        longitude_degrees=iss_subpoint.longitude.degrees,
                                        elevation_m=iss_subpoint.elevation.m)

            # Convert the geodetic position into a full Skyfield observer object
            # Needed to compute astronomical observations (e.g. sun altitude) from the ISS location
            iss_skyfield_location = earth + iss_geodetic_position

            # Get the apparent altitude of the Sun as seen from the ISS location at this time
            sun_altitude_from_iss_location = iss_skyfield_location.at(t).observe(sun).apparent().altaz()[0].degrees

            # ISS is illuminated when sun is higher than -6 degrees (not in Earth's shadow)
            iss_is_illuminated = sun_altitude_from_iss_location > -6.0

            # Check if observer is in darkness (nautical twilight or darker)
            observer_skyfield_location = earth + observer_geodetic_position
            sun_altitude = observer_skyfield_location.at(t).observe(sun).apparent().altaz()[0].degrees
            observer_in_darkness = sun_altitude < -6.0

            # Verify ISS is high enough above horizon for good visibility
            iss_altitude, _, _ = (iss - observer_geodetic_position).at(t).altaz()
            iss_high_enough = iss_altitude.degrees >= 10.0

            # Pass is visible if all conditions are met:
            # 1. ISS is illuminated by sun
            # 2. Observer is in darkness
            # 3. ISS is high enough above horizon
            if iss_is_illuminated and observer_in_darkness and iss_high_enough:
                visible = True
                break

        # Convert UTC times to local Berlin timezone
        rise_time_local = rise_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
        max_time_local = max_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)
        set_time_local = set_time.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(berlin_tz)

        # Build pass data dictionary
        passes.append({
            "start": rise_time_local.strftime('%Y-%m-%d %H:%M:%S %Z'),       # Human readable start time
            "start_timestamp": int(rise_time_local.timestamp()),             # Unix timestamp for start
            "end": set_time_local.strftime('%Y-%m-%d %H:%M:%S %Z'),          # Human readable end time
            "end_timestamp": int(set_time_local.timestamp()),                # Unix timestamp for end
            "max": max_time_local.strftime('%Y-%m-%d %H:%M:%S %Z'),          # Human readable time of maximum elevation
            "max_elevation_deg": round(max_elev, 1),                    # Maximum elevation in degrees
            "duration_sec": duration_seconds,                           # Total pass duration in seconds
            "visible": visible                                          # Whether pass is visible for the common observer
         })

    return passes

# --- API Endpoints ---
@app.route('/passes')
def passes_endpoint():
    """API endpoint to get ISS passes for the specified number of days."""
    # Update cache if expired (in background thread to avoid blocking)
    if cache_is_expired():
        threading.Thread(target=update_passes_cache).start()

    # Load passes from cache
    passes = load_passes_from_cache()

    # Parse and validate 'days' parameter
    days_str = request.args.get('days', '7')
    try:
        days = int(days_str)
        if days < 1 or days > 7:
            return jsonify({"error": "days must be between 1 and 7"}), 400
        return jsonify(passes[:10])  # Return maximum 10 passes
    except ValueError:
        return jsonify({"error": "Invalid days parameter"}), 400

@app.route('/next_pass')
def next_pass_endpoint():
    """API endpoint to get detailed information about the next ISS pass."""

    # Update cache if expired (in background thread to avoid blocking)
    if cache_is_expired():
        threading.Thread(target=update_passes_cache).start()

    # Load cached ISS passes
    cached_passes = load_passes_from_cache()
    if not cached_passes:
        return jsonify({"error": "No passes found"}), 404

   # Select the next upcoming ISS pass
    next_iss_pass = cached_passes[0]

    # Calculate additional details for the next pass.
    # These can be calculated quickly in comparison to the cached prediction data:

    # Calculate the time of maximum elevation (start time + half duration) in UTC
    # datetime object (Python standard library)
    max_elevation_time_dt = datetime.fromtimestamp(next_iss_pass['start_timestamp'] + (next_iss_pass['duration_sec'] // 2), tz=ZoneInfo("UTC"))
    # Skyfield Time object (astronomy library)
    max_elevation_time = ts.utc(max_elevation_time_dt)

    # Calculate rise and set times in UTC
    rise_time_utc = ts.utc(datetime.fromtimestamp(next_iss_pass['start_timestamp'], tz=ZoneInfo("UTC")))
    set_time_utc = ts.utc(datetime.fromtimestamp(next_iss_pass['end_timestamp'], tz=ZoneInfo("UTC")))

    # Calculate altitude and azimuth at rise and set times
    altitude_at_rise, azimuth_at_rise, _ = (iss - observer_geodetic_position).at(rise_time_utc).altaz()
    altitide_at_set, azimuth_at_set, _ = (iss - observer_geodetic_position).at(set_time_utc).altaz()

    def azimuth_to_direction(deg):
        """Convert azimuth angle in degrees to compass direction."""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
        idx = int((deg + 22.5) // 45)
        return directions[idx]

    # Determine ISS pass path direction from rise azimuth to set azimuth
    pass_direction = f"{azimuth_to_direction(azimuth_at_rise.degrees)} → {azimuth_to_direction(azimuth_at_set.degrees)}"

    # Get ISS position at maximum elevation time and calculate distance from earth center in kilometers
    iss_position_at_max = iss.at(max_elevation_time)
    distance_km_at_max = round(iss_position_at_max.distance().km, 1)

    # Estimate brightness based on maximum elevation angle:
    # Higher elevation = closer distance = brighter appearance
    max_elev = next_iss_pass['max_elevation_deg']
    if max_elev >= 60:
        brightness_level = "very bright"
    elif max_elev >= 40:
        brightness_level = "bright"
    elif max_elev >= 20:
        brightness_level = "moderate"
    else:
        brightness_level = "faint"

    # Add calculated details to the pass data response
    next_iss_pass.update({
        "azimuth_start_deg": round(azimuth_at_rise.degrees, 1),
        "azimuth_end_deg": round(azimuth_at_set.degrees, 1),
        "direction": pass_direction,
        "distance_km": distance_km_at_max,
        "brightness_estimate": brightness_level
    })

    return jsonify(next_iss_pass)

# --- Server Startup ---
if __name__ == "__main__":
    # Start server accessible from external connections on port 52139
    # Using IPv6 localhost (::1)
    app.run(host='::1', port=52139)
