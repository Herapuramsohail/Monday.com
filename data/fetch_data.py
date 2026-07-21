import urllib.request
import ssl

ssl_context = ssl._create_unverified_context()

deal_url = "https://docs.google.com/spreadsheets/d/1jghv-FiZ_bmWtEtB7IyaKYlwT5omEwSl/export?format=csv"
work_url = "https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/export?format=csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_file(url, outfile):
    print(f"Downloading {url} to {outfile}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            content = response.read()
            with open(outfile, 'wb') as f:
                f.write(content)
            print(f"Successfully downloaded {outfile} ({len(content)} bytes)")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

download_file(deal_url, r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\deal_funnel.csv")
download_file(work_url, r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv")
