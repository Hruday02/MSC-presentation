import os, base64

IMG_PATHS = {
    'clean': r'C:\Users\hruda\.gemini\antigravity-cli\brain\7877d74c-3f5e-4b00-8f9b-bbdc5e511fe8\msc_tank_inspection_cross_section_1793768833677.jpg',
    'rust': r'C:\Users\hruda\.gemini\antigravity-cli\brain\7877d74c-3f5e-4b00-8f9b-bbdc5e511fe8\msc_tank_corrosion_detected_1793768887441.jpg',
    'repaired': r'C:\Users\hruda\.gemini\antigravity-cli\brain\7877d74c-3f5e-4b00-8f9b-bbdc5e511fe8\msc_tank_maintenance_completed_1793768935222.jpg',
}

IMAGE_DATA = {}
for k, path in IMG_PATHS.items():
    if os.path.exists(path):
        with open(path, 'rb') as f:
            IMAGE_DATA[k] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8')

print("All 3 images loaded into memory:")
for k, v in IMAGE_DATA.items():
    print(f"  {k}: {len(v)} base64 chars")
