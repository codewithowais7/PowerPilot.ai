import requests, json

base = "http://localhost:8000/api/v1"

print("=== HEALTH ===")
r = requests.get("http://localhost:8000/health")
print(r.json())

print("\n=== ENERGY DATA ===")
r = requests.get(f"{base}/energy-data?limit=3")
d = r.json()
print(f"Total records: {d['total']} | Showing: {d['returned']}")

print("\n=== ANALYSIS ===")
r = requests.get(f"{base}/analysis")
a = r.json()
print(f"Daily: {a['daily_usage']} kWh | Weekly: {a['weekly_usage']} | Trend: {a['trend']}")
print(f"Peak hours: {a['peak_hours']}")

print("\n=== PREDICTION (next_hour) ===")
r = requests.get(f"{base}/predict?horizon=next_hour")
print("Status:", r.status_code)
if r.status_code == 200:
    p = r.json()
    print(f"Horizon: {p['horizon']} | Points: {len(p['predictions'])}")
    if p["predictions"]:
        print(f"First: {p['predictions'][0]}")
else:
    print("Error:", r.text[:300])

print("\n=== ANOMALY DETECTION ===")
r = requests.post(f"{base}/anomalies/detect")
print("Status:", r.status_code)
if r.status_code == 200:
    a = r.json()
    print(f"Total: {a['total_records']} | Anomalies: {a['total_anomalies']} | Rate: {a['anomaly_rate']}%")
else:
    print("Error:", r.text[:200])
