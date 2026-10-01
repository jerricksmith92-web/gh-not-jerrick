from flask import Flask, request, jsonify, render_template_string
import json, os, uuid, time
from datetime import datetime

app = Flask(__name__)
ADMIN_PASS = os.environ.get("ADMIN_PASS", "ghana123")
YOUR_MOMO = "0551234567" # CHANGE TO YOUR MOMO
CREATOR = "Jerrick Smith"

DB_FILE = "/tmp/messages.json" # Render free uses /tmp
messages = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE,'r') as f: messages=json.load(f)
    except: messages=[]

def save():
    try:
        with open(DB_FILE,'w') as f: json.dump(messages,f)
    except: pass

def clean():
    global messages
    now=time.time()
    messages=[m for m in messages if now-m.get('ts',0)<24*3600]

HTML="""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Built by Jerrick Smith 🇬🇭</title><style>
body{background:#f9f6f0;margin:0;font-family:system-ui;display:flex;justify-content:center}
.card{width:100%;max-width:520px;background:#fffdf9;margin:8px;border-radius:24px;box-shadow:0 4px 20px rgba(0,0,0,0.08);min-height:95vh;display:flex;flex-direction:column;overflow:hidden}
.creator-bar{background:#000;color:#ffcc00;text-align:center;padding:8px;font-size:11px;font-weight:bold}
.top{padding:16px 20px;display:flex;justify-content:space-between;border-bottom:1px solid #eee}
.list{flex:1;padding:14px;overflow-y:auto;max-height:65vh}
.msg{display:flex;gap:10px;margin-bottom:14px;cursor:pointer}
.avatar{width:36px;height:36px;background:#ffe8e0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0}
.bottom{padding:14px;border-top:1px solid #eee;position:sticky;bottom:0;background:#fffdf9}
.input{width:100%;padding:12px 16px;border-radius:20px;border:1px solid #ddd;box-sizing:border-box;outline:none}
.send{background:#111;color:#fff;border:none;padding:10px 18px;border-radius:20px;font-weight:bold}
.tools{display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap}
.tools button{border:1px solid #ddd;background:#fff;padding:6px 12px;border-radius:20px;font-size:12px}
.stickers{display:none;flex-wrap:wrap;gap:6px;background:#fff;border:1px solid #eee;padding:8px;border-radius:12px;margin-bottom:8px}
#replyBar{display:none;background:#fff3cd;padding:8px 12px;border-radius:10px;font-size:12px;margin-bottom:8px}
</style></head><body>
<div class="card">
<div class="creator-bar">👑 CREATED BY JERRICK SMITH 🇬🇭 • GH-BOT PRO • RENDER LIVE</div>
<div class="top"><div><div style="font-size:10px;letter-spacing:2px;opacity:0.5">SHARED ROOM BY JERRICK SMITH</div><div style="font-size:20px;font-weight:bold">The open thread 👑</div><div style="font-size:10px;background:#ffcc00;display:inline-block;padding:2px 8px;border-radius:10px;font-weight:bold">Jerrick Smith • Creator ✅</div></div><div style="color:#1a8a5c;font-size:12px;font-weight:bold">● LIVE</div></div>
<div class="list" id="chat"></div>
<div class="bottom">
<div id="replyBar"></div>
<div class="stickers" id="stPane"><span onclick="sendS('😂')">😂</span><span onclick="sendS('❤️')">❤️</span><span onclick="sendS('🔥')">🔥</span><span onclick="sendS('🇬🇭')">🇬🇭</span><span onclick="sendS('💀')">💀</span><span onclick="sendS('🙏')">🙏</span><span onclick="sendS('💯')">💯</span><span onclick="sendS('😎')">😎</span></div>
<div class="tools"><button onclick="toggleS()">😊 Stickers</button><label style="border:1px solid #ddd;background:#fff;padding:6px 12px;border-radius:20px;font-size:12px;cursor:pointer">📷 Photo<input type="file" accept="image/*" hidden onchange="sendImg(event)"></label><button onclick="clearOld()" style="color:red">Admin</button></div>
<input id="name" class="input" placeholder="Your name" style="margin-bottom:8px">
<input id="text" class="input" placeholder="Write a message...">
<div style="display:flex;justify-content:space-between;margin-top:8px"><span style="font-size:10px;opacity:0.5">24H AUTO-DELETE • BY JERRICK SMITH</span><button class="send" onclick="sendM()">Send ➤</button></div>
<div style="text-align:center;margin-top:10px;background:#000;color:#ffcc00;padding:8px;border-radius:12px;font-size:11px;font-weight:bold">© Built by Jerrick Smith 🇬🇭 <button onclick="pay()" style="background:#ffcc00;border:none;padding:4px 10px;border-radius:10px;margin-left:6px">MoMo PAY</button></div>
</div></div>
<script>
let replyTo=null;
function load(){fetch('/messages').then(r=>r.json()).then(d=>{let h='';d.forEach(m=>{let badge=m.name.toLowerCase().includes('jerrick')?'<span style="background:#000;color:#ffcc00;font-size:9px;padding:1px 6px;border-radius:10px">👑 CREATOR</span>':'';let rHtml=m.reply?`<div style="font-size:11px;background:#f3efe6;border-left:3px solid #b85c38;padding:4px 8px;border-radius:4px;margin:4px 0">↳ Reply to ${m.reply.name}: ${m.reply.text.slice(0,30)}</div>`:'';let img=m.image?`<br><img src="${m.image}" style="max-width:180px;border-radius:12px;margin-top:6px">`:'';h+=`<div class="msg" onclick="setR('${m.id}','${m.name.replace(/'/g,'')}','${m.text.replace(/'/g,'').slice(0,30)}')"><div class="avatar">${m.name[0].toUpperCase()}</div><div><div style="font-size:12px;opacity:0.7"><b>${m.name}</b> ${badge} ${m.time} <span onclick="delM('${m.id}');event.stopPropagation()" style="color:red;cursor:pointer;font-size:10px">[X]</span></div>${rHtml}<div style="background:#fff;border:1px solid #eee;padding:10px 14px;border-radius:18px;margin-top:4px;display:inline-block">${m.text}${img}</div><div style="font-size:10px;opacity:0.4">↩ tap to reply</div></div></div>`});document.getElementById('chat').innerHTML=h||'<div style="opacity:0.3;text-align:center;margin-top:30px">No messages yet<br>Built by Jerrick Smith</div>';});}
function setR(id,name,text){replyTo={id,name,text};let b=document.getElementById('replyBar');b.style.display='block';b.innerHTML=`Replying to <b>${name}</b>: ${text} <span onclick="cancelR()" style="float:right;cursor:pointer">X</span>`;}
function cancelR(){replyTo=null;document.getElementById('replyBar').style.display='none';}
function sendM(){let name=document.getElementById('name').value||'Anon';localStorage.setItem('gh_name',name);let text=document.getElementById('text').value;if(!text)return;fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,text,reply:replyTo})}).then(()=>{document.getElementById('text').value='';cancelR();load();});}
function sendS(s){let name=document.getElementById('name').value||'Anon';fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,text:s,reply:replyTo})}).then(()=>{cancelR();load();});}
function sendImg(e){let f=e.target.files[0];if(!f)return;let r=new FileReader();r.onload=()=>{let name=document.getElementById('name').value||'Anon';fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,text:'📷',image:r.result,reply:replyTo})}).then(()=>{cancelR();load();});};r.readAsDataURL(f);}
function delM(id){let p=prompt('Only Jerrick Smith can delete! Enter pass:');if(!p)return;fetch('/delete/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pass:p})}).then(r=>r.json()).then(d=>{if(d.error)alert(d.error);else load();});}
function clearOld(){let p=prompt('Admin pass?');fetch('/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pass:p})}).then(()=>load());}
function toggleS(){let el=document.getElementById('stPane');el.style.display=el.style.display=='flex'?'none':'flex';}
function pay(){alert('MoMo to Jerrick Smith: 0551234567 - 2 GHS for VIP');}
setInterval(load,2500);load();document.getElementById('name').value=localStorage.getItem('gh_name')||'';
</script></body></html>
"""

@app.route('/')
def home(): clean(); return render_template_string(HTML)
@app.route('/messages')
def msgs(): clean(); return jsonify(messages[-200:])
@app.route('/send',methods=['POST'])
def send():
    d=request.json; m={"id":str(uuid.uuid4())[:8],"name":d.get('name','Anon')[:20],"text":d.get('text','')[:500],"image":d.get('image','')[:400000],"reply":d.get('reply'),"time":datetime.now().strftime("%H:%M"),"ts":time.time()}
    if m['text'] or m['image']: messages.append(m); save()
    return jsonify({"ok":True})
@app.route('/delete/<mid>',methods=['POST'])
def delm(mid):
    p=(request.json or {}).get('pass')
    if p!=ADMIN_PASS: return jsonify({"error":f"Only {CREATOR} can delete!"}),403
    global messages; messages=[x for x in messages if x['id']!=mid]; save(); return jsonify({"ok":True})
@app.route('/clear',methods=['POST'])
def clear():
    p=(request.json or {}).get('pass')
    if p!=ADMIN_PASS: return jsonify({"error":"Wrong pass"}),403
    messages.clear(); save(); return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
