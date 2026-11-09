"""City Events Finder. Python standard library; no credentials in source."""
import concurrent.futures
import datetime as dt
import json
import os
import re
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
UTC = dt.timezone.utc


def fetch(url, params, headers=None):
    request = Request(url + '?' + urlencode(params), headers=headers or {})
    with urlopen(request, timeout=12) as response:
        return json.load(response)


def clean(value):
    value = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode()
    return ' '.join(re.findall(r'[a-z0-9]+', value.lower()))


def merge(events):
    """Merge exact normalized title + local date + venue; missing venues stay separate."""
    merged = {}
    for event in events:
        if not event.get('date'):
            continue
        key = (clean(event['title']), event['date'], clean(event.get('venue')))
        if not key[2]:
            key += (event['source'], event['id'])
        if key in merged:
            current = merged[key]
            current['sources'] = sorted(set(current['sources'] + event['sources']))
            current['links'].update(event['links'])
        else:
            merged[key] = dict(event, sources=list(event['sources']), links=dict(event['links']))
    return sorted(merged.values(), key=lambda e: (e['date'], e.get('time') or '23:59:59', e['title']))


def event(source, identifier, title, date, time='', venue='', url=''):
    return dict(source=source, id=identifier, title=title, date=date, time=time,
                venue=venue, sources=[source], links={source: url} if url else {})


def date_bounds(place, start, end):
    """Express the inclusive city-local date range as UTC timestamps."""
    from zoneinfo import ZoneInfo
    zone = ZoneInfo(place.get('timezone') or 'UTC')
    first = dt.datetime.combine(dt.date.fromisoformat(start), dt.time.min, zone)
    last = dt.datetime.combine(dt.date.fromisoformat(end) + dt.timedelta(days=1), dt.time.min, zone) - dt.timedelta(seconds=1)
    return tuple(value.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ') for value in (first, last))


def ticketmaster(place, start, end):
    key = os.getenv('TICKETMASTER_API_KEY')
    if not key:
        raise ValueError('API key not configured')
    first, last = date_bounds(place, start, end)
    data = fetch('https://app.ticketmaster.com/discovery/v2/events.json', {
        'apikey': key, 'latlong': f"{place['latitude']},{place['longitude']}",
        'radius': 15, 'unit': 'miles', 'startDateTime': first,
        'endDateTime': last, 'sort': 'date,asc', 'size': 200})
    results = []
    for item in data.get('_embedded', {}).get('events', []):
        if item.get('dates', {}).get('status', {}).get('code') == 'cancelled':
            continue
        dates = item.get('dates', {}).get('start', {})
        venues = item.get('_embedded', {}).get('venues', [])
        results.append(event('Ticketmaster', item['id'], item['name'], dates.get('localDate'),
                             dates.get('localTime', ''), venues[0].get('name', '') if venues else '', item.get('url', '')))
    return results


def predicthq(place, start, end):
    token = os.getenv('PREDICTHQ_API_TOKEN')
    if not token:
        raise ValueError('API token not configured')
    first, last = date_bounds(place, start, end)
    data = fetch('https://api.predicthq.com/v1/events/', {
        'within': f"24km@{place['latitude']},{place['longitude']}",
        'start.gte': first, 'start.lte': last, 'sort': 'start', 'limit': 50,
        'category': 'concerts,sports,performing-arts,festivals,community', 'state': 'active'},
        {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    results = []
    from zoneinfo import ZoneInfo
    for item in data.get('results', []):
        timestamp = item.get('start')
        if not timestamp:
            continue
        local = dt.datetime.fromisoformat(timestamp.replace('Z', '+00:00')).astimezone(ZoneInfo(item.get('timezone') or place.get('timezone') or 'UTC'))
        if not start <= local.date().isoformat() <= end:
            continue
        venue = next((e.get('name', '') for e in item.get('entities', []) if e.get('type') == 'venue'), '')
        results.append(event('PredictHQ', item['id'], item['title'], local.date().isoformat(), local.time().isoformat(), venue))
    return results


def weather(place, start, end):
    data = fetch('https://api.open-meteo.com/v1/forecast', {
        'latitude': place['latitude'], 'longitude': place['longitude'],
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max',
        'temperature_unit': 'fahrenheit', 'timezone': place.get('timezone', 'auto'),
        'start_date': start, 'end_date': end})
    daily = data.get('daily', {})
    return {date: {'high_f': daily['temperature_2m_max'][i],
                   'low_f': daily['temperature_2m_min'][i],
                   'rain_percent': daily['precipitation_probability_max'][i]}
            for i, date in enumerate(daily.get('time', []))}


def search(city):
    locations = fetch('https://geocoding-api.open-meteo.com/v1/search',
                      {'name': city, 'count': 1, 'language': 'en'})
    if not locations.get('results'):
        raise ValueError('City not found. Try a city followed by its state or country.')
    place = locations['results'][0]
    from zoneinfo import ZoneInfo
    today = dt.datetime.now(ZoneInfo(place.get('timezone') or 'UTC')).date()
    start, end = today.isoformat(), (today + dt.timedelta(days=6)).isoformat()
    statuses, all_events, forecast = {}, [], {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs = {pool.submit(fn, place, start, end): name for name, fn in [
            ('Ticketmaster', ticketmaster), ('PredictHQ', predicthq), ('Open-Meteo', weather)]}
        for future in concurrent.futures.as_completed(jobs):
            name = jobs[future]
            try:
                result = future.result()
                if name == 'Open-Meteo':
                    forecast = result
                else:
                    all_events.extend(result)
                statuses[name] = {'ok': True, 'count': len(result)}
            except ValueError as error:
                statuses[name] = {'ok': False, 'message': str(error)}
            except Exception:
                # Do not return upstream URLs/exceptions: a URL may contain the API key.
                statuses[name] = {'ok': False, 'message': 'Provider request failed. Check account access, quota, and configuration.'}
    events = merge(all_events)
    for item in events:
        item['weather'] = forecast.get(item['date'])
    return {'location': ', '.join(filter(None, [place['name'], place.get('admin1'), place.get('country')])),
            'start': start, 'end': end, 'events': events, 'providers': statuses,
            'complete': all(s['ok'] for s in statuses.values()),
            'coverage_note': 'Within about 15 miles; next seven calendar days. Up to 200 Ticketmaster and 50 PredictHQ records per search.'}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Avoid logging request URLs and search contents.
        pass

    def send(self, code, body, content_type='application/json; charset=utf-8'):
        raw = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parts = urlsplit(self.path)
        if parts.path == '/health':
            return self.send(200, 'OK', 'text/plain; charset=utf-8')
        if parts.path in ('/', '/app.js', '/style.css'):
            filename, mime = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'application/javascript'),
                              '/style.css': ('style.css', 'text/css')}[parts.path]
            return self.send(200, (ROOT / filename).read_text(), mime + '; charset=utf-8')
        if parts.path == '/api/events':
            city = parse_qs(parts.query).get('city', [''])[0].strip()
            if not 2 <= len(city) <= 100:
                return self.send(400, {'error': 'Enter a city between 2 and 100 characters.'})
            try:
                return self.send(200, search(city))
            except ValueError as error:
                return self.send(400, {'error': str(error)})
            except Exception:
                return self.send(502, {'error': 'Location lookup failed. Please try again.'})
        return self.send(404, {'error': 'Not found'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.getenv('PORT', '8080'))), Handler).serve_forever()
