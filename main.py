from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import socketio
import uvicorn
from collections import defaultdict
import base64

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# rooms: {room_name: [messages]}
rooms_data = defaultdict(list)

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{margin:0;font-family:sans-serif;background:#e5ddd5}
.top{position:fixed;top:0;left:0;right:0;background:#202c33;color:#fff;padding:10px;display:flex;gap:6px;z-index:10}
.top input{flex:1;padding:8px;border-radius:8px;border:0}
.top button{background:#25D366;border:0;padding:8px 12px;border-radius:8px;font-weight:bold}
#chat{margin-top:55px;margin-bottom:120px;padding:10px}
.msg{background:#fff;padding:8px 10px;border-radius:8px;margin:6px 0;max-width:80%;word-wrap:break-word}
.me{background:#dcf8c6;margin-left:auto}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#202c33;padding:8px;display:flex;flex-direction:column;gap:6px}
.row{display:flex;gap:6px;align-items:center}
.row input{flex:1;padding:10px;border-radius:20px;border:0}
.row button{width:42px;height:42px;border-radius:50%;border:0;background:#25D366;font-size:18px}
#stickers{display:flex;gap:6px;overflow-x:auto}
.st{font-size:24px;background:#111b21;padding:6px 10px;border-radius:20px;cursor:pointer}
.reply-box{background:#111b21;color:#25D366;padding:4px 8px;font-size:12px;display:none}
</style></head><body>
<div class=top>
<input id=roomInput placeholder="room name" value="open-thread">
<button onclick="joinRoom()">JOIN ROOM</button>
<button onclick="shareLink()">SHARE LINK</button>
</div>
<div id=chat></div>
<div class=bottom>
<div id=replyBox class=reply-box></div>
<div id=stickers>
<div class=st onclick="sendSticker('😂')">😂</div><div class=st onclick="sendSticker('❤️')">❤️</div>
<div class=st onclick="sendSticker('🔥')">🔥</div><div class=st onclick="sendSticker('💀')">💀</div>
<div class=st onclick="sendSticker('😭')">😭</div><div class=st onclick="sendSticker('🙏')">🙏</div>
<div class=st onclick="sendSticker('💯')">💯</div><div class=st onclick="sendSticker('🇬🇭')">🇬🇭</div>
</div>
<div class=row>
<input id=nameInput placeholder="Name">
<input type=file id=fileInput accept="image/*" style="display:none" onchange="sendFile(this)">
<button onclick="document.getElementById('fileInput').click()">📷</button>
<input id=msgInput placeholder="Hi">
<button id=micBtn onclick="toggleMic()">🎤</button>
<button onclick="sendMsg()">➤</button>
</div>
</div>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
let socket=io();
let curRoom=new URLSearchParams(location.search).get('room')||'open-thread';
let replyTo=null;
let mediaRecorder=null; let chunks=[]; let isRec=false;
document.getElementById('roomInput').value=curRoom;
function joinRoom(){
 let r=document.getElementById('roomInput').value.trim()||'open-thread';
 location.href='?room='+encodeURIComponent(r);
}
function shareLink(){
 navigator.clipboard.writeText(location.href);
 alert('Link copied: '+location.href);
}
socket.on('connect',()=>{ socket.emit('join',curRoom); });
socket.on('history',msgs=>{
 document.getElementById('chat').innerHTML='';
 msgs.forEach(addMsg);
});
socket.on('new_message',addMsg);
function addMsg(m){
 let d=document.createElement('div');
 d.className='msg'+(m.name==document.getElementById('nameInput').value?' me':'');
 let html=`<b>${m.name}</b>`;
 if(m.reply){ html+=`<div style="border-left:3px solid #25D366;padding-left:6px;margin:4px 0;color:#555;font-size:12px">${m.reply}</div>`; }
 if(m.type=='text'){ html+=`<div>${m.text}</div>`; }
 if(m.type=='sticker'){ html+=`<div style="font-size:32px">${m.text}</div>`; }
 if(m.type=='image'){ html+=`<div><img src="${m.text}" style="max-width:100%;border-radius:8px"></div>`; }
 if(m.type=='audio'){ html+=`<div><audio controls src="${m.text}"></audio></div>`; }
 html+=`<div style="font-size:10px;color:#999;text-align:right">${m.time||''}</div>`;
 d.innerHTML=html;
 d.onclick=()=>{ replyTo=m; document.getElementById('replyBox').style.display='block'; document.getElementById('replyBox').innerText='Reply to '+m.name+': '+(m.text||'').substring(0,30); };
 document.getElementById('chat').appendChild(d);
 window.scrollTo(0,document.body.scrollHeight);
}
function sendMsg(){
 let name=document.getElementById('nameInput').value.trim()||'Anon';
 let text=document.getElementById('msgInput').value.trim();
 if(!text) return;
 let payload={room:curRoom,name:name,text:text,type:'text',reply:replyTo?replyTo.name+': '+(replyTo.text||'').substring(0,40):''};
 socket.emit('send',payload);
 document.getElementById('msgInput').value='';
 replyTo=null; document.getElementById('replyBox').style.display='none';
}
function sendSticker(e){
 let name=document.getElementById('nameInput').value.trim()||'Anon';
 socket.emit('send',{room:curRoom,name:name,text:e,type:'sticker',reply:''});
}
function sendFile(inp){
 let f=inp.files[0]; if(!f) return;
 let reader=new FileReader();
 reader.onload=e=>{
  let name=document.getElementById('nameInput').value.trim()||'Anon';
  socket.emit('send',{room:curRoom,name:name,text:e.target.result,type:'image',reply:''});
 };
 reader.readAsDataURL(f);
}
async function toggleMic(){
 let btn=document.getElementById('micBtn');
 if(!isRec){
  try{
   let s=await navigator.mediaDevices.getUserMedia({audio:true});
   let mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':'audio/webm';
   mediaRecorder=new MediaRecorder(s,{mimeType:mime}); chunks=[];
   mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
   mediaRecorder.onstop=()=>{
    let blob=new Blob(chunks,{type:mediaRecorder.mimeType});
    let reader=new FileReader();
    reader.onload=e=>{
     let name=document.getElementById('nameInput').value.trim()||'Anon';
     socket.emit('send',{room:curRoom,name:name,text:e.target.result,type:'audio',reply:''});
    };
    reader.readAsDataURL(blob);
   };
   mediaRecorder.start(); isRec=true; btn.innerText='⏹️'; btn.style.background='red';
  }catch(err){ alert('Mic error: '+err.message); }
 }else{
  mediaRecorder.stop(); isRec=false; btn.innerText='🎤'; btn.style.background='#25D366';
  mediaRecorder.stream.getTracks().forEach(t=>t.stop());
 }
}
document.getElementById('msgInput').addEventListener('keydown',e=>{ if(e.key==='Enter') sendMsg(); });
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@sio.on('join')
async def on_join(sid, room):
    await sio.enter_room(sid, room)
    await sio.emit('history', rooms_data[room], to=sid)

@sio.on('send')
async def on_send(sid, data):
    room = data.get('room','open-thread')
    # limit size to 2MB to prevent crash
    if len(data.get('text','')) > 3000000:
        return
    rooms_data[room].append(data)
    if len(rooms_data[room]) > 200:
        rooms_data[room] = rooms_data[room][-200:]
    await sio.emit('new_message', data, room=room)

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=10000)
