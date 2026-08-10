import xml.etree.ElementTree as ET
import json, math, re

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def parse_coords(text):
    pts = []
    for tok in text.strip().split():
        parts = tok.split(',')
        lng, lat = float(parts[0]), float(parts[1])
        pts.append((lng, lat))
    return pts

def parse_polygon(poly_el):
    outer_el = poly_el.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
    outer = parse_coords(outer_el.text)
    holes = []
    for hole_el in poly_el.findall('.//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates', ns):
        holes.append(parse_coords(hole_el.text))
    return outer, holes

# --- panchayat boundary ---
tree = ET.parse('D:/Map/Pazhayannur_panchayat.kml')
root = tree.getroot()
pm = root.find('.//kml:Placemark', ns)
poly = pm.find('.//kml:Polygon', ns)
boundary_outer, boundary_holes = parse_polygon(poly)

# --- wards ---
tree2 = ET.parse('D:/Map/Pazhayannur_wards.kml')
root2 = tree2.getroot()
wards_raw = []
for pm2 in root2.findall('.//kml:Placemark', ns):
    name_el = pm2.find('kml:name', ns)
    name = name_el.text.strip() if name_el is not None else 'Ward'
    poly2 = pm2.find('.//kml:Polygon', ns)
    if poly2 is None:
        continue
    outer, holes = parse_polygon(poly2)
    wards_raw.append({'name': name, 'outer': outer, 'holes': holes})

print('wards parsed:', len(wards_raw))

# --- compute bbox across boundary + wards ---
all_pts = list(boundary_outer)
for w in wards_raw:
    all_pts.extend(w['outer'])

lngs = [p[0] for p in all_pts]
lats = [p[1] for p in all_pts]
lng_min, lng_max = min(lngs), max(lngs)
lat_min, lat_max = min(lats), max(lats)
lat0 = (lat_min + lat_max) / 2
cos_lat0 = math.cos(math.radians(lat0))

TARGET_W = 1000.0
span_x = (lng_max - lng_min) * cos_lat0
span_y = (lat_max - lat_min)
scale = TARGET_W / span_x if span_x > 0 else 1.0

def project(lng, lat):
    x = (lng - lng_min) * cos_lat0 * scale
    y = (lat_max - lat) * scale  # north-up
    return [round(x, 2), round(y, 2)]

def project_ring(ring):
    return [project(lng, lat) for lng, lat in ring]

boundary = {
    'outer': project_ring(boundary_outer),
    'holes': [project_ring(h) for h in boundary_holes],
}

def centroid(ring):
    # simple polygon centroid (area-weighted)
    a = 0.0
    cx = 0.0
    cy = 0.0
    pts = ring
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    if abs(a) < 1e-9:
        # fallback: average of points
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return [sum(xs) / len(xs), sum(ys) / len(ys)]
    cx /= (6 * a)
    cy /= (6 * a)
    return [round(cx, 2), round(cy, 2)]

wards = []
for i, w in enumerate(wards_raw, start=1):
    proj_outer = project_ring(w['outer'])
    c = centroid(proj_outer)
    # clean up name: "Ward 1 - NEERNAMUKKU" -> number + label
    m = re.match(r'Ward\s*(\d+)\s*-\s*(.+)', w['name'], re.IGNORECASE)
    if m:
        num = int(m.group(1))
        label = m.group(2).strip().title()
    else:
        num = i
        label = w['name'].title()
    wards.append({
        'number': num,
        'name': label,
        'outer': proj_outer,
        'centroid': c,
    })

wards.sort(key=lambda w: w['number'])

height = round((lat_max - lat_min) * scale, 2)

out = {
    'width': round(TARGET_W, 2),
    'height': height,
    'boundary': boundary,
    'wards': wards,
}

with open('D:/pazhayannur.com/src/data/wards-geo.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=0)

print('width', out['width'], 'height', out['height'])
print('ward count', len(wards))
print('sample ward:', wards[0]['number'], wards[0]['name'], 'points:', len(wards[0]['outer']))
