from pathlib import Path


def patch_calculator():
    p = Path('calculator.html')
    s = p.read_text(encoding='utf-8')
    if 'id="detailStructure"' in s:
        print('calculator.html already upgraded')
        return False

    style_needle = '.note{margin-top:15px;font-size:11px;color:var(--muted);line-height:1.5}'
    style_new = '''.note{margin-top:15px;font-size:11px;color:var(--muted);line-height:1.5}.structure{margin-top:15px;border-top:1px solid var(--line);padding-top:14px}.structure-title{font-size:13px;font-weight:800;color:var(--ink);margin-bottom:4px}.structure-intro{font-size:11px;color:var(--muted);line-height:1.5;margin-bottom:12px}.costgroup{border:1px solid var(--line);border-radius:11px;margin-top:9px;overflow:hidden;background:#fff}.costgroup-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:9px 11px;background:var(--soft);border-bottom:1px solid var(--line);font-size:11px;font-weight:800}.costgroup-head span:last-child{font-variant-numeric:tabular-nums}.costrow{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:9px 11px;border-bottom:1px dashed var(--line);font-size:11px}.costrow:last-child{border-bottom:0}.costrow .ctext{min-width:0}.costrow b{font-size:11px}.costrow small{display:block;color:var(--muted);line-height:1.45;margin-top:2px}.costrow strong{white-space:nowrap;font-variant-numeric:tabular-nums}.howbox{margin-top:10px;background:#f8f9fc;border:1px solid #e5e8f3;border-radius:11px;padding:11px;font-size:11px;line-height:1.5;color:var(--muted)}.howbox b{color:var(--ink)}'''
    if style_needle not in s:
        raise RuntimeError('calculator style anchor not found')
    s = s.replace(style_needle, style_new, 1)

    old_summary = '''<aside class="card summary"><div class="head"><h2>Cost result</h2><span class="modelname" id="sumModel"></span></div><div class="body"><div class="totalbox"><div class="lab">TOTAL COST / DEVICE</div><div class="big" id="unitTotal">€0.00</div><div class="smalltotal" id="lotTotal">1 device · €0.00 total</div></div><div class="break"><div class="line"><span>Parts / materials</span><strong id="parts">€0.00</strong></div><div class="line"><span>Repair labor</span><strong id="labor">€0.00</strong></div><div class="line"><span>Processing</span><strong id="processing">€0.00</strong></div><div class="line"><span>Cosmetic / software</span><strong id="extras">€0.00</strong></div></div><div class="laborlogic" id="logic"><b>No repair selected.</b></div><div class="selops" id="selected"></div><div class="btns"><button class="btn secondary" id="reset">Reset</button><button class="btn primary" onclick="window.print()">Print / PDF</button></div><div class="note">Part prices are taken from the Remalab 15.08.2026 price list. Repair levels are only used internally to calculate labor. Board-repair parts, when required, remain on quote.</div></div></aside>'''
    new_summary = '''<aside class="card summary"><div class="head"><h2>Detailed cost structure</h2><span class="modelname" id="sumModel"></span></div><div class="body"><div class="totalbox"><div class="lab">TOTAL COST / DEVICE</div><div class="big" id="unitTotal">€0.00</div><div class="smalltotal" id="lotTotal">1 device · €0.00 total</div></div><div class="break"><div class="line"><span>Parts / materials</span><strong id="parts">€0.00</strong></div><div class="line"><span>Repair labor</span><strong id="labor">€0.00</strong></div><div class="line"><span>Processing</span><strong id="processing">€0.00</strong></div><div class="line"><span>Cosmetic / software</span><strong id="extras">€0.00</strong></div></div><div class="laborlogic" id="logic"><b>No repair selected.</b></div><div class="structure" id="detailStructure"><div class="structure-title">How this price is built</div><div class="structure-intro">Parts are charged separately. Repair labor uses one base labor according to the most complex selected intervention, then €8.50 for each additional repair operation. Processing is charged once per repaired device.</div><div id="detailParts"></div><div id="detailLabor"></div><div id="detailExtras"></div></div><div class="selops" id="selected"></div><div class="btns"><button class="btn secondary" id="reset">Reset</button><button class="btn primary" onclick="window.print()">Print / PDF</button></div><div class="note">All prices are in EUR. Part prices are taken from the Remalab 15.08.2026 price list. Internal repair levels are not shown; only the client-facing labor structure is displayed. Board-repair parts, when required, remain on quote.</div></div></aside>'''
    if old_summary not in s:
        raise RuntimeError('calculator summary anchor not found')
    s = s.replace(old_summary, new_summary, 1)

    start = s.index('function calc(){')
    end = s.index('init();const ACCESS_HASH', start)
    new_calc = r'''function calc(){const m=MODELS[$("model").value],selectedOps=OPS.filter(o=>state.selected[o.id]&&available(o,m));const parts=selectedOps.reduce((sum,o)=>sum+opPartCost(o,m),0);const repairCount=selectedOps.length;let labor=0,processing=0,logic="",base=0,add=0,high="";if(repairCount){processing=LAB.processing;if(repairCount===1&&selectedOps[0].id==="battery"){labor=state.batteryIC?LAB.batteryIC:LAB.batteryOnly;logic=`<b>Battery-only labor:</b> ${money(labor)} + processing ${money(processing)}.`;}else{const score={BAT:0,L1:1,L2:2,L3:3};high="L1";selectedOps.forEach(o=>{if(score[o.level]>score[high])high=o.level});base=LAB[high]||LAB.L1;add=Math.max(0,repairCount-1)*LAB.additional;labor=base+add;logic=`<b>Repair labor:</b> ${money(base)}${repairCount>1?` + ${repairCount-1} additional operation${repairCount>2?"s":""} × ${money(LAB.additional)} = <b>${money(labor)}</b>`:""}.`;}}else logic="<b>No repair selected.</b>";let extra=0;const faces=($("polFront").checked?1:0)+($("polBack").checked?1:0);if(faces)extra+=faces*(repairCount?LAB.polishRepair:LAB.polishOnly);if($("ios").checked)extra+=LAB.ios;const unit=parts+labor+processing+extra,qty=Math.max(1,Number($("qty").value)||1);$("parts").textContent=money(parts);$("labor").textContent=money(labor);$("processing").textContent=money(processing);$("extras").textContent=money(extra);$("unitTotal").textContent=money(unit);$("lotTotal").textContent=`${qty.toLocaleString()} device${qty===1?"":"s"} · ${money(unit*qty)} total`;$("logic").innerHTML=logic;$("sumModel").textContent=$("model").value;
const partRows=selectedOps.length?selectedOps.map(o=>{const cost=opPartCost(o,m);const amount=(o.id==="board"&&!state.boardParts)?"On quote":money(cost);let note=opLabel(o,m);if(o.id==="camerarepair")note="Material basis: 60% of new main camera price";if(o.id==="blackspots")note="Camera black-spot repair material";return `<div class="costrow"><div class="ctext"><b>${o.name}</b><small>${note}</small></div><strong>${amount}</strong></div>`}).join(""):`<div class="costrow"><div class="ctext"><b>No parts selected</b><small>Select a repair operation to see its part or material cost.</small></div><strong>€0.00</strong></div>`;$("detailParts").innerHTML=`<div class="costgroup"><div class="costgroup-head"><span>1 · Parts & materials</span><span>${money(parts)}</span></div>${partRows}</div>`;
let laborRows="";if(!repairCount){laborRows=`<div class="costrow"><div class="ctext"><b>No repair labor</b><small>Labor appears when at least one repair operation is selected.</small></div><strong>€0.00</strong></div>`}else if(repairCount===1&&selectedOps[0].id==="battery"){laborRows=`<div class="costrow"><div class="ctext"><b>Battery replacement labor</b><small>${state.batteryIC?"Battery-only workflow with IC transplant":"Standard battery-only workflow"}</small></div><strong>${money(labor)}</strong></div>`}else{laborRows=`<div class="costrow"><div class="ctext"><b>Base repair labor</b><small>One base labor is applied according to the most complex intervention in the selected repair set.</small></div><strong>${money(base)}</strong></div>`;if(repairCount>1)laborRows+=`<div class="costrow"><div class="ctext"><b>Additional repair operations</b><small>${repairCount-1} additional operation${repairCount>2?"s":""} × ${money(LAB.additional)}. This avoids charging a full base labor for every repair performed on the same device.</small></div><strong>${money(add)}</strong></div>`}$("detailLabor").innerHTML=`<div class="costgroup"><div class="costgroup-head"><span>2 · Repair labor</span><span>${money(labor)}</span></div>${laborRows}</div>`;
let serviceRows=`<div class="costrow"><div class="ctext"><b>Device processing</b><small>Applied once per repaired device.</small></div><strong>${money(processing)}</strong></div>`;const cosmeticRate=repairCount?LAB.polishRepair:LAB.polishOnly;if($("polFront").checked)serviceRows+=`<div class="costrow"><div class="ctext"><b>Front polishing</b><small>${repairCount?"Polishing performed within a repair workflow":"Polishing-only rate"}</small></div><strong>${money(cosmeticRate)}</strong></div>`;if($("polBack").checked)serviceRows+=`<div class="costrow"><div class="ctext"><b>Back polishing</b><small>${repairCount?"Polishing performed within a repair workflow":"Polishing-only rate"}</small></div><strong>${money(cosmeticRate)}</strong></div>`;if($("ios").checked)serviceRows+=`<div class="costrow"><div class="ctext"><b>iOS update</b><small>Software update service.</small></div><strong>${money(LAB.ios)}</strong></div>`;$("detailExtras").innerHTML=`<div class="costgroup"><div class="costgroup-head"><span>3 · Processing & extras</span><span>${money(processing+extra)}</span></div>${serviceRows}</div><div class="howbox"><b>Why Remalab structures labor this way:</b> when several repairs are completed during the same device workflow, the most complex intervention sets the base labor and each extra repair is added at a reduced additional-operation fee. Parts and materials remain fully itemized above.</div>`;$("selected").innerHTML="";}
'''
    s = s[:start] + new_calc + s[end:]
    p.write_text(s, encoding='utf-8')
    print('calculator.html upgraded')
    return True


def patch_ai():
    p = Path('ai.html')
    s = p.read_text(encoding='utf-8')
    changed = False
    old = '<details id="advanced" class="advanced"><summary>Advanced / Manual calculator <span>Open only when you want to edit the technical selections yourself</span></summary><iframe id="calculator" title="Remalab Cost Calculator"></iframe></details>'
    new = '<details id="advanced" class="advanced"><summary>Detailed repair cost structure <span>Parts, materials, labor, processing and manual editing</span></summary><iframe id="calculator" title="Remalab Detailed Cost Structure"></iframe></details>'
    if old in s:
        s = s.replace(old, new, 1)
        changed = True
    if '>Manual calculator</button>' in s:
        s = s.replace('>Manual calculator</button>', '>View detailed structure</button>', 1)
        changed = True
    if "quickArea.innerHTML=''" in s and 'autoDetailScroll' not in s:
        s = s.replace("quickArea.innerHTML=''", "quickArea.innerHTML='';const autoDetailScroll=true;if(autoDetailScroll){advanced.open=true;setTimeout(()=>advanced.scrollIntoView({behavior:'smooth',block:'start'}),1400)}", 1)
        changed = True
    if changed:
        p.write_text(s, encoding='utf-8')
        print('ai.html upgraded')
    else:
        print('ai.html already upgraded or anchors not found')
    return changed


patch_calculator()
patch_ai()
