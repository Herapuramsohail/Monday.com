import urllib.request
import ssl

ssl_context = ssl._create_unverified_context()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

urls_to_try = [
    ("https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/export?format=csv", r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv"),
    ("https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/export?format=xlsx", r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.xlsx"),
    ("https://drive.google.com/uc?export=download&id=1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j", r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker_drive.xlsx")
]

for url, outfile in urls_to_try:
    print(f"Trying {url} -> {outfile}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
            content = response.read()
            if len(content) > 200:
                with open(outfile, 'wb') as f:
                    f.write(content)
                print(f"SUCCESS {outfile} ({len(content)} bytes)")
                break
            else:
                print(f"Returned too small: {len(content)} bytes")
    except Exception as e:
        print(f"Failed {url}: {e}")
