import urllib.parse
import base64

svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="red"/></svg>'''
# Base64 data URI
b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
data_uri = f"data:image/svg+xml;base64,{b64}"
print("Base64 Data URI:", data_uri)
