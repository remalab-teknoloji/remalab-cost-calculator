from pathlib import Path

# --- Backend: make voice responses harder to cut off ---
p = Path('api/realtime-token.js')
s = p.read_text(encoding='utf-8')
s = s.replace('max_output_tokens: 900,', 'max_output_tokens: 1200,')
s = s.replace("""        turn_detection: {
          type: 'semantic_vad',
          create_response: true,
          interrupt_response: true
        }""", """        turn_detection: {
          type: 'semantic_vad',
          eagerness: 'low',
          create_response: true,
          interrupt_response: false
        }""")
p.write_text(s, encoding='utf-8')

# --- Frontend: prominent manual simulator + echo-safe voice ---
p = Path('ai.html')
s = p.read_text(encoding='utf-8')

if '.manual-hero{' not in s:
    s = s.replace('.workspace{display:grid;', '.manual-hero{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:16px;padding:18px 20px;background:linear-gradient(135deg,#202b55,#344578);color:#fff;border-radius:18px;box-shadow:0 8px 24px rgba(32,43,85,.12)}.manual-hero .manual-copy{min-width:0}.manual-kicker{font-size:10px;letter-spacing:.11em;text-transform:uppercase;font-weight:850;opacity:.62}.manual-hero h2{font-size:19px;margin:4px 0 4px}.manual-hero p{font-size:12px;line-height:1.45;margin:0;opacity:.72}.manual-big{border:0;background:#fff;color:#26345f;border-radius:12px;padding:13px 18px;font-weight:850;font-size:13px;cursor:pointer;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.08)}.manual-big:hover{transform:translateY(-1px)}.mode-or{font-size:11px;opacity:.58;margin-left:8px}@media(max-width:700px){.manual-hero{align-items:stretch;flex-direction:column}.manual-big{width:100%}.mode-or{display:none}}.workspace{display:grid;', 1)

hero = '''<section class="manual-hero"><div class="manual-copy"><div class="manual-kicker">Manual simulation</div><h2>Prefer to build the cost yourself?</h2><p>Choose the model, repair operations and part quality directly. See each part, labor step and processing charge update instantly.</p></div><div><button id="manualHeroBtn" class="manual-big" type="button">Open Manual Cost Simulator</button><span class="mode-or">or use the AI below</span></div></section>'''
if 'id="manualHeroBtn"' not in s:
    s = s.replace('\n<div class="workspace">', '\n'+hero+'\n<div class="workspace">', 1)

s = s.replace("navigator.mediaDevices.getUserMedia({audio:true})", "navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}})")

# Protect the assistant from speaker echo: pause outgoing mic only while model audio is playing.
old_handler = "function handleRealtimeEvent(e){let ev;try{ev=JSON.parse(e.data)}catch{return}if(ev.type==='conversation.item.input_audio_transcription.completed'&&ev.transcript){lastLanguage=detectLanguage(ev.transcript);appendMessage('user',ev.transcript)}"
new_handler = "function handleRealtimeEvent(e){let ev;try{ev=JSON.parse(e.data)}catch{return}if(ev.type==='output_audio_buffer.started'&&connectionMode==='voice'&&localStream){localStream.getAudioTracks().forEach(t=>t.enabled=false);setStatus('Speaking…','live')}if(ev.type==='output_audio_buffer.stopped'&&connectionMode==='voice'&&localStream){localStream.getAudioTracks().forEach(t=>t.enabled=true);setStatus('Listening','live')}if(ev.type==='conversation.item.input_audio_transcription.completed'&&ev.transcript){lastLanguage=detectLanguage(ev.transcript);appendMessage('user',ev.transcript)}"
if old_handler in s:
    s = s.replace(old_handler, new_handler, 1)

# Fix previous auto-scroll placement: do not jump away while asking a clarification.
s = s.replace("function showQuickChoices(items){quickArea.innerHTML='';const autoDetailScroll=true;if(autoDetailScroll){advanced.open=true;setTimeout(()=>advanced.scrollIntoView({behavior:'smooth',block:'start'}),1400)};", "function showQuickChoices(items){quickArea.innerHTML='';")

# Once a final quote exists, open the didactic manual structure and move the client to it after a short delay.
quote_tail = "document.getElementById('qExtras').textContent=q.breakdown?.cosmetic_software||'';quickArea.innerHTML=''}"
quote_new = "document.getElementById('qExtras').textContent=q.breakdown?.cosmetic_software||'';quickArea.innerHTML='';advanced.open=true;setTimeout(()=>advanced.scrollIntoView({behavior:'smooth',block:'start'}),1800)}"
if quote_tail in s:
    s = s.replace(quote_tail, quote_new, 1)

manual_listener = "document.getElementById('manualBtn').addEventListener('click',()=>{advanced.open=true;advanced.scrollIntoView({behavior:'smooth',block:'start'})});"
if manual_listener in s and "manualHeroBtn').addEventListener" not in s:
    s = s.replace(manual_listener, manual_listener+"document.getElementById('manualHeroBtn').addEventListener('click',()=>{advanced.open=true;advanced.scrollIntoView({behavior:'smooth',block:'start'});setTimeout(()=>{try{frame.contentDocument.getElementById('model')?.focus()}catch(e){}},500)});", 1)

p.write_text(s, encoding='utf-8')

# Remove one-shot patch files after execution so the repo stays clean.
Path('scripts/upgrade_voice_manual_v2.py').unlink(missing_ok=True)
Path('.github/workflows/upgrade-voice-manual-v2.yml').unlink(missing_ok=True)
print('Voice stability and manual simulator UX upgraded.')
