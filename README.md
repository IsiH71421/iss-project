# ISS Interactive Information Screen (ISS)

## Table of Contents
- [Project Description](#project-description)
- [Project Architecture](#project-architecture)
- [CPEE Models](#cpee-models)
- [API Documentation](#api-documentation)
- [Installation](#installation)
- [Server Management](#server-management)
- [Testing and Validation](#testing-and-validation)
- [QR Navigation](#qr-navigation)
- [Tech Stack](#tech-stack)
- [License](#license)

---

## Project Description

This project powers an interactive ISS information display designed for public screens. It integrates with the [CPEE Process Engine](https://cpee.org) to show real-time ISS data such as upcoming passes, live location, crew details, and more — accessible via QR codes for a touchless experience.

### Display Screens:

- **Main screen:** Countdown and duration for the next ISS pass over TUM Garching (coordinates configurable).
- **Forecast screen:** Next 10 ISS passes with start/end times, visibility prediction, time remaining, and pass duration.
- **Location screen:** Live ISS position with zoom options.
- **Crew screen:** Current ISS crew members including names, countries, roles, grouped by mission (e.g. NASA/SpaceX Crew Dragon, Roskosmos Soyuz, Axiom Missions, Boeing Starliner).
- **NASA Picture of the Day screen:** Displays NASA's daily picture with description and navigation to past pictures.
- **Details screen:** Detailed info for the next pass including start/end time, altitude, azimuth, pass duration, visibility, max elevation, direction, and brightness estimate.

The repository also includes a demo video, screenshots, and XML models for CPEE workflows.

---

## Project Architecture
```
iss/
├── 📂 pass_server/                # Backend API Server
│   └── 📄 pass_service.py        # Flask server for ISS tracking API
│   └── 📄 de421.bsp                  # JPL planetary ephemeris data for astronomical calculations
└── 📄 passes_cache.json           # Cached ISS pass predictions
│
├── 📂 waitqr/                         # QR callback service
│   └── 📄 callback.php             # QR code scan callback handler (receives scan events)
│   └── 📄 callback.url              # CPEE Callback URL file
└── 📄 initiate.php                   # QR code callback initiation script
│
├── 📂 display/                           # Frontend HTML Pages
│   ├── 📄 index.html                 # Main countdown page
│   ├── 📄 forecast.html             # Forecast of next 10 passes
│   ├── 📄 location.html             # ISS position map
│   ├── 📄 details.html               # Pass details
│   ├── 📄 picture.html             # NASA Picture of the Day
│   └── 📄 crew.html                    # ISS crew information
│
├── 📂 assets/                           # Static resources (CSS, JS, QR codes)
│   ├──📄 css/style.css              # Stylesheet
│   ├──📄 js/functions.js          # JavaScript utilities for time formatting
│   └── 📄 qr_*.png                    # QR code navigation images for touchless operation
│
├── 📂 documentation/                 # Documentation and workflow models
│   ├── 📂 cpee_models                 # CPEE workflow models (SVG and XML files)
│   ├── 📄 Demo-Video.mkv          # Video demonstration of system functionality
│   ├── 📄 Screenshots.pdf           # Visual documentation with UI screenshots
├── 📄 README.md                      # This file
├── 📄 LICENSE                              # License
```

### Backend Services
- `pass_server/`: ISS orbit calculations and API (Python/Flask)
- `waitqr/`: QR code callback handling (PHP)

### Frontend
- `display/`: User-facing HTML pages
- `assets/`: Shared CSS, JS, and QR code images

### Documentation
- `cpee_models/`: XML and SVG workflow models
- Demo video and screenshots

---

## CPEE Models

The CPEE Process Engine ([cpee.org](https://cpee.org)) orchestrates navigation via XML-based workflows:

- Main model: `iss_screen_model.xml`
- Subprocesses:
  - `page/index.xml`
  - `page/crew.xml`
  - `page/forecast.xml`
  - `page/details.xml`
  - `page/location.xml`
  - `page/picture.xml`

All models are included in `documentation/cpee_models/` as `.xml` and `.svg` files.

---

## API Documentation

Used APIs:

- **Crew Info:**  
  https://corquaid.github.io/international-space-station-APIs/JSON/people-in-space.json
- **ISS Location:**  
  http://api.open-notify.org/iss-now.json
- **NASA Picture of the Day:**  
  https://api.nasa.gov/planetary/apod?api_key=YOUR_NASA_API_KEY_HERE
> **Note:** To use the NASA API, sign up for a free API key at [https://api.nasa.gov](https://api.nasa.gov).

---

### Pass Prediction Server
Implemented in `pass_server/pass_service.py` using:

- Skyfield for astronomical calculations
- CelesTrak TLE data
- WGS84 ellipsoid coordinates
- 60-minute cache refresh

#### Endpoints

**Next pass:** `GET /next_pass`

Example Response:

```json
{
  "start": "2025-01-23 19:30:15 CET",
  "start_timestamp": 1737653415,
  "end": "2025-01-23 19:36:45 CET",
  "end_timestamp": 1737653805,
  "max_elevation_deg": 45.2,
  "duration_sec": 390,
  "visible": true,
  "azimuth_start_deg": 245.7,
  "azimuth_end_deg": 87.3,
  "direction": "SW → E",
  "brightness_estimate": "bright",
  "distance_km": 687.4
}
```

**Upcoming Passes**: `GET /passes?days=7`

Parameters:
- `days` (optional): Number of days (1-7, default: 7)

Example Response:
```json
[
  {
    "start": "2025-01-23 19:30:15 CET",
    "start_timestamp": 1737653415,
    "end": "2025-01-23 19:36:45 CET", 
    "end_timestamp": 1737653805,
    "max": "2025-01-23 19:33:30 CET",
    "max_elevation_deg": 45.2,
    "duration_sec": 390,
    "visible": true
  }
]
```

---

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- Internet connection for TLE data

### Setup Steps
1. Clone this repository: git clone https://github.com/IsiH71421/iss-project.git
2. Install Python dependencies: pip install -r requirements.txt 
3. Update your location in pass_service.py:
observer_lat = 48.262839
observer_lon = 11.666853
observer_elevation = 0
4. Start the Flask server as described below.
5. Run `iss_screen_model.xml` on cpee.org.
6. Open the application at: https://cpee.org/out/frames/iss/ 
7. Navigate pages via QR Codes.
8. End the process with the QR Code `Exit ISS Screen`. This will stop the model on cpee.org

---

## Server Management
### Run in Background (Linux)
```bash
cd iss/pass_server
daemonize -c "$PWD" -o /dev/null -e /dev/null "$PWD/pass_service.py"
```

### Run Locally
```bash
cd iss/pass_server
./pass_service.py >/dev/null 2>/dev/null &
```

### To Stop the Server
```bash
ps aux | grep pass_service.py
kill <PID>
```

---

## Testing and Validation

Use [Heavens Above](https://heavens-above.com/PassSummary.aspx?satid=25544&lat=48.2514&lng=11.651&loc=Garching+bei+M%C3%BCnchen&alt=0&tz=CET) to verify predictions.

---

## QR Navigation
Test these endpoints directly or scan their QR codes:
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=end 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=index
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=crew
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=forecast 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=details  
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=location 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=location&zoom=in 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=location&zoom=out 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=picture
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=picture&days_back=before 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=picture&days_back=after 
-	https://lehre.bpm.in.tum.de/~ge25fel/iss/waitqr/callback.php?navigate=picture&days_back=today 

---

## Tech Stack
- Python 3 (Flask)
- JavaScript + HTML/CSS
- Skyfield / CelesTrak
- PHP (QR Handling)
- CPEE (Process Automation)

---

## License
This project is licensed for educational and personal use only.  
Commercial use is prohibited without explicit permission.  
See LICENSE for full terms.
