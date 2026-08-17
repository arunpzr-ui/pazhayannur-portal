"""
Builds src/data/terrain.json: a real elevation heightmap for Pazhayannur
Grama Panchayat, clipped/tagged against the actual panchayat boundary
from the KML, for a WebGL 3D terrain on the Geography page.

Run manually (not part of the build):
    python scripts/process-terrain.py

Requires scripts/Pazhayannur_panchayat.kml and scripts/Pazhayannur_wards.kml
(copied in from the source KML the user supplied). Elevation comes from
the free Open-Elevation API (https://api.open-elevation.com) - real
SRTM-derived data, not invented or eyeballed from a map screenshot.

Coordinates are projected to real metres (equirectangular approximation
centred on the panchayat's mean latitude), NOT the 1000-unit scale
kml_to_geo.py uses for the flat ward map - this component needs true
ground-distance-to-elevation proportions, not an arbitrary icon scale.
"""
import json
import math
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

ns = {"kml": "http://www.opengis.net/kml/2.2"}
METRES_PER_DEGREE_LAT = 111320.0

# Grid resolution and how far past the administrative boundary the
# terrain extends, so hills don't look artificially cut off at the edge.
GRID_COLS = 90
GRID_ROWS = 75
PADDING_FRACTION = 0.14


def parse_coords(text):
    pts = []
    for tok in text.strip().split():
        lng, lat = tok.split(",")[:2]
        pts.append((float(lng), float(lat)))
    return pts


def parse_polygon(poly_el):
    outer_el = poly_el.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
    outer = parse_coords(outer_el.text)
    holes = []
    for hole_el in poly_el.findall(".//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates", ns):
        holes.append(parse_coords(hole_el.text))
    return outer, holes


def point_in_ring(lng, lat, ring):
    """Standard ray-casting point-in-polygon test."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        lng_i, lat_i = ring[i]
        lng_j, lat_j = ring[j]
        if ((lat_i > lat) != (lat_j > lat)) and (
            lng < (lng_j - lng_i) * (lat - lat_i) / (lat_j - lat_i) + lng_i
        ):
            inside = not inside
        j = i
    return inside


def centroid(ring):
    """Area-weighted polygon centroid (same algorithm as kml_to_geo.py)."""
    a = 0.0
    cx = 0.0
    cy = 0.0
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    if abs(a) < 1e-9:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        return [round(sum(xs) / len(xs), 1), round(sum(ys) / len(ys), 1)]
    return [round(cx / (6 * a), 1), round(cy / (6 * a), 1)]


def point_in_boundary(lng, lat, outer, holes):
    if not point_in_ring(lng, lat, outer):
        return False
    for hole in holes:
        if point_in_ring(lng, lat, hole):
            return False
    return True


def fetch_elevations(points):
    """Batched POST requests to Open-Elevation. Returns list of floats, same order as points."""
    elevations = []
    batch_size = 350
    url = "https://api.open-elevation.com/api/v1/lookup"
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        body = json.dumps(
            {"locations": [{"latitude": round(lat, 6), "longitude": round(lng, 6)} for lng, lat in batch]}
        ).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.loads(r.read())
                results = data["results"]
                if len(results) != len(batch):
                    raise ValueError(f"expected {len(batch)} results, got {len(results)}")
                elevations.extend(res["elevation"] for res in results)
                break
            except Exception as e:
                print(f"  batch {i}-{i+len(batch)} attempt {attempt+1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2)
        print(f"  fetched {min(i + batch_size, len(points))}/{len(points)}")
    return elevations


# --- parse the panchayat boundary ---
tree = ET.parse("scripts/Pazhayannur_panchayat.kml")
root = tree.getroot()
pm = root.find(".//kml:Placemark", ns)
poly = pm.find(".//kml:Polygon", ns)
boundary_outer, boundary_holes = parse_polygon(poly)

lngs = [p[0] for p in boundary_outer]
lats = [p[1] for p in boundary_outer]
lng_min, lng_max = min(lngs), max(lngs)
lat_min, lat_max = min(lats), max(lats)
lat0 = (lat_min + lat_max) / 2
cos_lat0 = math.cos(math.radians(lat0))
metres_per_degree_lng = METRES_PER_DEGREE_LAT * cos_lat0

# padded sampling extent
lng_span = lng_max - lng_min
lat_span = lat_max - lat_min
lng_pad = lng_span * PADDING_FRACTION
lat_pad = lat_span * PADDING_FRACTION
sample_lng_min = lng_min - lng_pad
sample_lng_max = lng_max + lng_pad
sample_lat_min = lat_min - lat_pad
sample_lat_max = lat_max + lat_pad


def project(lng, lat):
    """North-up, metres, origin at the padded sample area's top-left."""
    x = (lng - sample_lng_min) * metres_per_degree_lng
    z = (sample_lat_max - lat) * METRES_PER_DEGREE_LAT
    return round(x, 1), round(z, 1)


# --- build the sample grid ---
grid_points = []  # (lng, lat)
for row in range(GRID_ROWS):
    lat = sample_lat_max - (row / (GRID_ROWS - 1)) * (sample_lat_max - sample_lat_min)
    for col in range(GRID_COLS):
        lng = sample_lng_min + (col / (GRID_COLS - 1)) * (sample_lng_max - sample_lng_min)
        grid_points.append((lng, lat))

print(f"Fetching elevation for {len(grid_points)} points ({GRID_COLS}x{GRID_ROWS})...")
elevations = fetch_elevations(grid_points)

inside_mask = [point_in_boundary(lng, lat, boundary_outer, boundary_holes) for lng, lat in grid_points]

width_m, height_m = project(sample_lng_max, sample_lat_min)

boundary_projected = [list(project(lng, lat)) for lng, lat in boundary_outer]
holes_projected = [[list(project(lng, lat)) for lng, lat in hole] for hole in boundary_holes]

# --- parse and project the 24 ward boundaries, same coordinate system ---
wards_tree = ET.parse("scripts/Pazhayannur_wards.kml")
wards_root = wards_tree.getroot()
wards = []
for pm2 in wards_root.findall(".//kml:Placemark", ns):
    name_el = pm2.find("kml:name", ns)
    raw_name = name_el.text.strip() if name_el is not None else "Ward"
    poly2 = pm2.find(".//kml:Polygon", ns)
    if poly2 is None:
        continue
    ward_outer, _ = parse_polygon(poly2)
    m = re.match(r"Ward\s*(\d+)\s*-\s*(.+)", raw_name, re.IGNORECASE)
    number = int(m.group(1)) if m else len(wards) + 1
    label = m.group(2).strip().title() if m else raw_name.title()
    wards.append({
        "number": number,
        "name": label,
        "outer": [list(project(lng, lat)) for lng, lat in ward_outer],
        "centroid": centroid([list(project(lng, lat)) for lng, lat in ward_outer]),
    })
wards.sort(key=lambda w: w["number"])
print(f"Parsed {len(wards)} ward boundaries")

out = {
    "_source": "Real elevation from api.open-elevation.com (SRTM-derived); boundary and ward outlines from user-supplied KML survey data.",
    "gridCols": GRID_COLS,
    "gridRows": GRID_ROWS,
    "widthMetres": width_m,
    "heightMetres": height_m,
    "elevationMin": round(min(elevations), 1),
    "elevationMax": round(max(elevations), 1),
    "elevations": [round(e, 1) for e in elevations],
    "insideMask": inside_mask,
    "boundary": {
        "outer": boundary_projected,
        "holes": holes_projected,
    },
    "wards": wards,
}

with open("src/data/terrain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

print("Wrote src/data/terrain.json")
print(f"Extent: {width_m:.0f}m x {height_m:.0f}m")
print(f"Elevation range: {min(elevations):.0f}m - {max(elevations):.0f}m")
print(f"Points inside boundary: {sum(inside_mask)}/{len(inside_mask)}")
