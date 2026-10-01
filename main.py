from flask import Flask, request, render_template_string, jsonify
import json, os, base64
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
DATA_FILE = "rooms_data.json"

# Load rooms
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

def get_room_messages(room):
    return all_rooms.get(room, [])

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GH NOT - {{room}}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui;background:#111b21;color:#e9edef;height:100vh;display:flex;flex-direction:column}
.header{background:#202c33;padding:12px 15px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2a3942}
.header h2{font-size:16px;color:#25d366}
.room-link{font-size:11px;background:#182229;padding:5px 8px;border-radius:10px;color:#8696a0;word-break:break-all}
#messages{flex:1;overflow-y:auto;padding:15px;background:#0b141a url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');}
.msg{background:#202c33;padding:8px 12px;border-radius:8px;margin:6px 0;max-width:85%;position:relative}
.msg.me{background:#005c4b;margin-left:auto}
.msg.name{font-size:12px;color:#25d366;font-weight:bold}
.msg.text{font-size:14px;margin:4px 0;word-wrap:break-word}
.msg.time{font-size:10px;color:#8696a0;text-align:right}
.msg audio{width:200px;margin-top:5px}
.input-area{background:#202c33;padding:10px;display:flex;gap:8px;align-items:center}
.input-area input{flex:1;padding:12px;border:none;border-radius:25px;background:#2a3942;color:white;outline:none}
.btn{border:none;border-radius:50%;width:45px;height:45px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:20px}
.send{background:#25d366}
.mic{background:#00a884;color:white}
.mic.rec{background:red;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
.top-bar{background:#182229;padding:8px 15px;display:flex;gap:8px}
.top-bar input{flex:1;padding:8px;border-radius:8px;border:none;background:#2a3942;color:white}
.top-bar button{padding:8px 12px;border-radius:8px;border:none;background:#25d366;color:black;font-weight:bold}
</style>
</head>
<body>
<div class="header">
<h2>🇬🇭 GH NOT • {{room}}</h2>
<span style="font-size:12px">{{count}} msgs</span>
</div>
<div class="top-bar">
<input id="roomInput" placeholder="Type room name e.g. accra-boys" value="{{room}}">
<button onclick="joinRoom()">Join / Create</button>
<button onclick="shareRoom()">Share Link</button>
</div>
<div class="room-link" id="roomLink"></div>
<div id="messages"></div>
<div class="input-area">
<input id="name" placeholder="Your name" style="max-width:90px">
<input id="text" placeholder="Type message..." onkeypress="if(event.key==='Enter')sendText()">
<button class="btn mic" id="micBtn" onclick="toggleRecord()">🎤</button>
<button class="btn send" onclick="sendText()">➤</button>
</div>

<script>
let room = "{{room}}";
let mediaRecorder, audioChunks=[], isRecording=false;
document.getElementById('roomLink').innerText = window.location.href;

function joinRoom(){
 let r = document.getElementById('roomInput').value.trim().toLowerCase().replace(/[^a-z0-9-]/g,'-');
 if(!r) return alert('Type room name');
 window.location.href = '/?room='+r;
}
function shareRoom(){
 navigator.clipboard.writeText(window.location.href);
 alert('Link copied! Share am: '+window.location.href);
}

async function loadMsgs(){
 let res = await fetch('/msgs?room='+room);
 let data = await res.json();
 let box = document.getElementById('messages');
 box.innerHTML='';
 data.forEach(m=>{
   let div = document.createElement('div');
   div.className='msg'+(m.name==document.getElementById('name').value?' me':'');
   let content = '';
   if(m.type=='audio'){
     content = `<audio controls src="${m.text}"></audio>`;
   } else {
     content = `<div class="text">${m.text}</div>`;
   }
   div.innerHTML=`<div class="name">${m.name}</div>${content}<div class="time">${m.time}</div>`;
   box.appendChild(div);
 });
 box.scrollTop = box.scrollHeight;
}

async function sendText(){
 let name=document.getElementById('name').value||'Anon';
 let text=document.getElementById('text').value;
 if(!text.trim()) return;
 document.getElementById('text').value='';
 await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,name,text,type:'text'})});
 loadMsgs();
}

async function toggleRecord(){
 let btn=document.getElementById('micBtn');
 if(!isRecording){
   let stream = await navigator.mediaDevices.getUserMedia({audio:true});
   mediaRecorder = new MediaRecorder(stream);
   audioChunks=[];
   mediaRecorder.ondataavailable=e=>audioChunks.push(e.data);
   mediaRecorder.onstop=async()=>{
     let blob=new Blob(audioChunks,{type:'audio/webm'});
     let reader=new FileReader();
     reader.readAsDataURL(blob);
     reader.onloadend=async()=>{
       let base64=reader.result;
       let name=document.getElementById('name').value||'Anon';
       await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room,name,text:base64,type:'audio'})});
       loadMsgs();
     }
   };
   mediaRecorder.start();
   isRecording=true;
   btn.classList.add('rec');
   btn.innerText='⏹️';
 } else {
   mediaRecorder.stop();
   isRecording=false;
   btn.classList.remove('rec');
   btn.innerText='🎤';
 }
}

setInterval(loadMsgs,2000);
loadMsgs();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    room = request.args.get("room", "open-thread").lower().strip() or "open-thread"
    room = "".join(c if c.isalnum() or c=="-" else "-" for c in room)
    count = len(all_rooms.get(room, []))
    return render_template_string(HTML, room=room, count=count)

@app.route("/msgs")
def msgs():
    room = request.args.get("room", "open-thread")
    return jsonify(all_rooms.get(room, [])[-100:])

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    room = data.get("room","open-thread")
    if room not in all_rooms:
        all_rooms[room] = []
    all_rooms[room].append({
        "name": data.get("name","Anon")[:20],
        "text": data.get("text","")[:500000],
        "type": data.get("type","text"),
        "time": datetime.now().strftime("%H:%M")
    })
    # keep last 200 msgs per room
    if len(all_rooms[room]) > 200:
        all_rooms[room] = all_rooms[room][-200:]
    save_data()
    return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
