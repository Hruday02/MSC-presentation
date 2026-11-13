import story_app

svg = story_app.render_ship_svg("rust")
html_doc = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin: 0; padding: 0; background-color: #f8fafc; overflow: hidden; }}
  svg {{ width: 100%; height: 100%; display: block; }}
</style>
</head>
<body>
{svg}
</body>
</html>"""

print("HTML doc length:", len(html_doc))
assert "<svg" in html_doc
assert "</svg>" in html_doc
print("srcDoc construction verified!")
