from flask import Flask, request, render_template_string, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "rooms_data.json"
ADMIN_PASS = "ghana123"

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            all_rooms = json.load(f)
    except:
        all_rooms = {}
else:
    all_rooms = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(all_rooms, f)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GH NOT - {{room}}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui;background:#111b21;color:#e9edef;height:100vh;display:flex;flex-direction:column}
.brand{background:#25d366;color:#000;text-align:center;padding:6px;font-size:10px;font-weight:900;letter-spacing:0.5px}
.header{background:#202c33;padding:12px 15px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2a3942}
.header h2{font-size:14px;color:#fff}.header b{color:#25d366}
.top-bar{background:#182229;padding:8px 10px;display:flex;gap:6px}
.top-bar input{flex:1;padding:9px;border-radius:8px;border:none;background:#2a3942;color:#fff}
.top-bar button{padding:9px 12px;border-radius:8px;border:none;background:#25d366;color:#000;font-weight:800;font-size:12px}
.room-info{background:#182229;padding:5px 10px;font-size:11px;color:#8696a0;text-align:center;word-break:break-all}
#messages{flex:1;overflow-y:auto;padding:12px;background:#0b141a url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');}
.msg{background:#202c33;padding:8px 12px;border-radius:0 8px 8px 8px;margin:8px 0;max-width:82%;position:relative;box-shadow:0 1px 1px rgba(0,0,0,0.3)}
.msg.me{background:#005c4b;margin-left:auto;border-radius:8px 0 8px 8px}
.msg.name{font-size:11px;color:#25d366;font-weight:700;margin-bottom:2px}
.msg.txt{font-size:14.5px;word-wrap:break-word;white-space:pre-wrap}
.msg img{max-width:220px;border-radius:8px;margin-top:6px;cursor:pointer}
.msg audio{width:210px;margin-top:6px}
.reply-box{background:rgba(0,0,0,0.35);border-left:3px solid #25d366;padding:5px 8px;margin-bottom:6px;border-radius:4px;font-size:12px}
.time{font-size:10px;color:#8696a0;text-align:right;margin-top:4px;display:flex;justify-content:space-between}
.reply-btn{color:#53bdeb;cursor:pointer}
.del{position:absolute;top:3px;right:6px;cursor:pointer;color:#ff5c5c;font-size:14px;display:none}
.msg:hover.del{display:block}
.input-wrap{background:#202c33;padding:6px}
.stickers{display:flex;gap:6px;padding:6px 4px;overflow-x:auto}
.stickers span{background:#2a3942;padding:6px 10px;border-radius:15px;font-size:16px;cursor:pointer}
.reply-preview{background:#182229;padding:8px 12px;font-size:12px;border-left:4px solid #25d366;display:none;justify-content:space-between;align-items:center}
.input-area{display:flex;gap:6px;align-items:center;padding:8px}
.input-area input[type=text]{flex:1;padding:12px 15px;border:none;border-radius:25px;background:#2a3942;color:#fff;outline:none}
.icon-btn{width:44px;height:44px;border-radius:50%;border:none;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer}
.send{background:#25d366}
.mic{background:#00a884;color:white}
.mic.rec{background:#ea0038;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.15)}100%{transform:scale(1)}}
#fileInput{display:none}
</style>
</head>
<body>
<div class="brand">CREATED BY JERRICK SMITH • GH-BOT PRO • RENDER LIVE</div>
<div class="header">
<h2>The open thread • <b>{{room}}</b> • <span style="color:#25d366">{{count}} msgs</span> • LIVE</h2>
<button onclick="openAdmin()" style="background:#2a3942;border:none;color:#fff;padding:6px 10px;border-radius:6px;font-size:12px">Admin</button>
</div>
<div class="top-bar">
<input id="roomInput" value="{{room}}" placeholder="Create room e.g. accra-boys, jhs-2024">
<button onclick="joinRoom()">JOIN ROOM</button>
<button onclick="shareRoom()">SHARE LINK</button>
</div>
<div class="room-info" id="roomLink"></div>
<div id="replyPreview" class="reply-preview"><span id="replyText"></span><span onclick="cancelReply()" style="cursor:pointer;font-size:18px">✕</span></div>
<div id="messages"></div>
<div class="input-wrap">
<div class="stickers">
<span onclick="addSticker('😂')">😂</span><span onclick="addSticker('❤️')">❤️</span><span onclick="addSticker('🔥')">🔥</span><span onclick="addSticker('💀')">💀</span><span onclick="addSticker('😭')">😭</span><span onclick="addSticker('🙏')">🙏</span><span onclick="addSticker('💯')">💯</span><span onclick="addSticker('🇬🇭')">🇬🇭</span><span onclick="addSticker('😎')">😎</span><span onclick="addSticker('🥺')">🥺</span>
</div>
<div class="input-area">
<input id="name" type="text" placeholder="Name" style="max-width:75px">
<label for="fileInput" class="icon-btn" style="background:#2a3942">📷</label>
<input type="file" id="fileInput" accept="image/*" onchange="sendImage(this)">
<input id="text" type="text" placeholder="Type a message..." onkeypress="if(event.key==='Enter')sendText()">
<button class="icon-btn mic" id="micBtn" onclick="toggleRec()">🎤</button>
<button class="icon-btn send" onclick="sendText()">➤</button>
</div>
</div>
<script>
let room="{{room}}", replyTo=null, isAdmin=false;
let mediaRecorder, chunks=[], isRec=false;
document.getElementById('roomLink').innerText='🔗 Share this link to invite: '+location.href;
function joinRoom(){let r=document.getElementById('roomInput').value.trim().toLowerCase().replace(/[^a-z0-9-]/g,'-');if(r) location.href='/?room='+r;}
function shareRoom(){navigator.clipboard.writeText(location.href);alert('Link copied!\\n'+location.href);}
function addSticker(s){document.getElementById('text').value+=s;document.getElementById('text').focus();}
function setReply(n,t,i){replyTo={name:n,text:t.slice(0,50),id:i};document.getElementById('replyPreview').style.display='flex';document.getElementById('replyText').innerText='Replying to '+n+': '+t.slice(0,30);}
function cancelReply(){replyTo=null;document.getElementById('replyPreview').style.display='none';}
function openAdmin(){let p=prompt('Admin password:');if(p==='ghana123'){isAdmin=true;alert('Admin ON - tap X to delete');loadMsgs();}}
async function loadMsgs(){
 let r=await fetch('/msgs?room='+room);let data=await r.json();
 let box=document.getElementById('messages');box.innerHTML='';
 data.forEach((m,i)=>{
 let s=await navigator.mediaDevices.getUserMedia({audio:true});
   let mime = MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' : 'audio/webm';
   mediaRecorder=new MediaRecorder(s, {mimeType: mime});chunks=[];
  let rep=m.reply?`<div class="reply-box"><b>${m.reply.name}</b>: ${m.reply.text}</div>`:'';
  let cont='';
  if(m.type=='image') cont=`<img src="${m.text}" onclick="window.open(this.src)">`;
  else if(m.type=='audio') cont=`<audio controls src="${m.text}"></audio>`;
  else cont=`<div class="txt">${m.text}</div>`;
  let del=isAdmin?`<span class="del" onclick="delMsg(${i})">✕</span>`:'';
  d.innerHTML=`${del}${rep}<div class="name">${m.name}</div>${cont}<div class="time"><span class="reply-btn" onclick="setReply('${m.name.replace(/'/g,"")}','${(m.text||"").toString().slice(0,20).replace(/'/g,"")} ',${i})">↩ reply</span><span>${m.time}</span></div>`;
  box.appendChild(d);
 });
 box.scrollTop=box.scrollHeight;
}
async function sendText(){
 let name=document.getElementById('name').value||'Anon';let text=document.getElementById('text').value;
 if(!text.trim()) return;
 document.getElementById('text').value='';
 await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,name,text,type:'text',reply:replyTo})});
 cancelReply();loadMsgs();
}
async function sendImage(inp){
 let f=inp.files[0];if(!f) return;
 let rd=new FileReader();rd.readAsDataURL(f);
 rd.onloadend=async()=>{
  let name=document.getElementById('name').value||'Anon';
  await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,name,text:rd.result,type:'image',reply:replyTo})});
  cancelReply();loadMsgs();
 }
}
async function toggleRec(){
 let btn=document.getElementById('micBtn');
 if(!isRec){
  try{
   let s=await navigator.mediaDevices.getUserMedia({audio:true});
   mediaRecorder=new MediaRecorder(s);chunks=[];
   mediaRecorder.ondataavailable=e=>chunks.push(e.data);
   mediaRecorder.onstop=async()=>{
    let blob=new Blob(chunks,{type:'audio/webm'});
    let rd=new FileReader();rd.readAsDataURL(blob);
    rd.onloadend=async()=>{
     let name=document.getElementById('name').value||'Anon';
     await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,name,text:rd.result,type:'audio',reply:replyTo})});
     cancelReply();loadMsgs();
    }
   };
   mediaRecorder.start();isRec=true;btn.classList.add('rec');btn.innerText='⏹️';
  }catch(e){alert('Allow mic permission!');}
 }else{mediaRecorder.stop();isRec=false;btn.classList.remove('rec');btn.innerText='🎤';}
}
async function delMsg(i){if(!confirm('Delete?')) return;await fetch('/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,index:i,password:'ghana123'})});loadMsgs();}
setInterval(loadMsgs,2000);loadMsgs();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    room = request.args.get("room","open-thread").lower().strip() or "open-thread"
    room = "".join(c if c.isalnum() or c=="-" else "-" for c in room)
    count = len(all_rooms.get(room,[]))
    return render_template_string(HTML, room=room, count=count)

@app.route("/msgs")
def msgs():
    room = request.args.get("room","open-thread")
    return jsonify(all_rooms.get(room,[])[-200:])

@app.route("/send", methods=["POST"])
def send():
    d=request.json; room=d.get("room","open-thread")
    if room not in all_rooms: all_rooms[room]=[]
    all_rooms[room].append({
        "name": d.get("name","Anon")[:20],
        "text": d.get("text","")[:900000],
        "type": d.get("type","text"),
        "reply": d.get("reply"),
        "time": datetime.now().strftime("%H:%M")
    })
    if len(all_rooms[room])>400: all_rooms[room]=all_rooms[room][-400:]
    save_data(); return jsonify({"ok":True})

@app.route("/delete", methods=["POST"])
def delete_msg():
    d=request.json
    if d.get("password")!=ADMIN_PASS: return jsonify({"ok":False})
    room=d.get("room"); idx=d.get("index")
    if room in all_rooms and 0 <= idx < len(all_rooms[room]):
        all_rooms[room].pop(idx); save_data()
    return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
