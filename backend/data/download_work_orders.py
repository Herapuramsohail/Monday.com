import urllib.request
import ssl
import time

ssl_context = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

urls = [
    "https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/export?format=csv",
    "https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/gviz/tq?tqx=out:csv",
    "https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/export?format=xlsx"
]

outfiles = [
    r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv",
    r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv",
    r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.xlsx"
]

for url, outfile in zip(urls, outfiles):
    print(f"Trying URL: {url}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
                data = resp.read()
                if len(data) > 100:
                    with open(outfile, "wb") as f:
                        f.write(data)
                    print(f"SUCCESS saved {outfile} ({len(data)} bytes)")
                    exit(0)
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(2)
