from flask import Flask, Response
import requests
from prometheus_client import Gauge, generate_latest
from datetime import datetime, timezone

app = Flask(__name__)

# Define your endpoints and auth
API_ENDPOINTS = [
    {
        "site": "AFM",
        "url": "https://reports.aeonfantasy.com.my/monitor/getdata.aspx?script=UploadMonitorsyc",
        "auth": ("admin", "parafait")
    },
    {
        "site": "AWS2-SG",
        "url": "https://cvmitrawebreports.parafait1.com/Monitor/getdata.aspx?script=UploadMonitorsyc",
        "auth": ("admin", "parafait")
    },
    {
        "site": "AWS1-SG",
        "url": "https://cowplayfalcon.parafait.com/Monitor/getdata.aspx?script=UploadMonitorsyc",
        "auth": ("admin", "parafait")
    },
    {
        "site": "PNL-SG",
        "url": "https://playnlearnindo.parafait1.com/Monitor/getdata.aspx?script=UploadMonitorsyc",
        "auth": ("admin", "parafait")
    }
]


# Define Prometheus metric
data_status = Gauge('site_update_status', '1 = fresh, 0 = stale', ['site'])

@app.route('/metrics')
def metrics():
    data_status.clear()
    for endpoint in API_ENDPOINTS:
        try:
            r = requests.get(endpoint['url'], auth=endpoint['auth'], timeout=10)
            row = r.json()[0]
            last_update = datetime.fromisoformat(row['last_update'].replace('Z', '+00:00'))
            diff_minutes = (datetime.now(timezone.utc) - last_update).total_seconds() / 60
            is_fresh = 1 if diff_minutes < 10 else 0
            data_status.labels(site=endpoint['site']).set(is_fresh)
        except Exception:
            data_status.labels(site=endpoint['site']).set(0)
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
