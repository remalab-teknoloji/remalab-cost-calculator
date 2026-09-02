from pathlib import Path

# Calculator: rename and explain Camera Wash while preserving the existing €4.50 + labor pricing logic.
p = Path('calculator.html')
s = p.read_text(encoding='utf-8')
s = s.replace('"id":"blackspots","name":"Camera Black Spots","level":"L2","desc":"Camera cleaning / black spot repair","kind":"service"', '"id":"blackspots","name":"Camera Wash / Black Spots","level":"L2","desc":"Camera wash for black spots, stains or dust on the camera","kind":"service"')
s = s.replace('<span>Repair material</span><b>${money(LAB.blackspots)}</b>', '<span>Camera wash fee</span><b>${money(LAB.blackspots)}</b>')
s = s.replace('if(op.id==="blackspots")note="Camera black-spot repair material";', 'if(op.id==="blackspots")note="Camera wash fee for black spots, stains or dust";')
p.write_text(s, encoding='utf-8')

# AI UX: use the same client-facing name in the quote card.
p = Path('ai.html')
s = p.read_text(encoding='utf-8')
s = s.replace("blackspots:'Camera Black Spots'", "blackspots:'Camera Wash / Black Spots'")
p.write_text(s, encoding='utf-8')

# AI backend: teach the assistant exactly when Camera Wash applies.
p = Path('api/realtime-token.js')
s = p.read_text(encoding='utf-8')
s = s.replace('- blackspots: camera black spots/dust cleaning repair.', '- blackspots: Camera Wash. Use this when the client reports black spots, stains, marks or dust visible through the camera. The calculator applies a €4.50 camera-wash fee plus the applicable repair labor. Do not choose a full camera replacement unless the client describes an actual camera failure or explicitly asks for replacement. French examples: taches noires, taches sur la caméra, poussière caméra. Turkish examples: kamera lekesi, siyah nokta, kamera tozu.')
p.write_text(s, encoding='utf-8')

# Self-clean the one-shot patch files.
Path('scripts/add_camera_wash.py').unlink(missing_ok=True)
Path('.github/workflows/add-camera-wash.yml').unlink(missing_ok=True)
print('Camera Wash added to calculator and AI assistant.')
