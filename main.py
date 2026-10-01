from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import socketio
import uvicorn
from collections import defaultdict

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)
rooms_data = defaultdict(list)

HTML = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1'>
<title>GH NOT - Jerrick Smith</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#efeae2}
.top{position:fixed;top:0;left:0;right:0;background:#075e54;color:#fff;padding:10px 8px;display:flex;gap:6px;z-index:20;align-items:center}
.top.brand{font-weight:900;letter-spacing:1px;font-size:18px;white-space:nowrap}
.top input{flex:1;padding:9px;border-radius:20px;border:0;outline:none}
.top button{background:#25D366;color:#fff;border:0;padding:8px 12px;border-radius:20px;font-weight:700;font-size:12px}
#chat{margin-top:58px;margin-bottom:145px;padding:10px}
.msg{background:#fff;padding:8px 10px;border-radius:0 12px 12px 12px;margin:8px 0;max-width:85%;box-shadow:0 1px 0.5px rgba(0,0,0,.13);position:relative;word-break:break-word}
.me{background:#dcf8c6;border-radius:12px 0 12px 12px;margin-left:auto}
.msg b{font-size:13px;color:#075e54;display:block}
.msg.time{font-size:10px;color:#999;text-align:right;margin-top:4px}
.reply-line{border-left:4px solid #25D366;background:rgba(37,211,102,.15);padding:4px 6px;margin:4px 0;font-size:12px;color:#333;border-radius:4px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#f0f0f0;padding:6px 8px;display:flex;flex-direction:column;gap:6px;border-top:1px solid #ddd}
#replyBox{display:none;background:#fff;border-left:4px solid #25D366;padding:6px 8px;font-size:12px;justify-content:space-between;align-items:center}
#stickers{display:flex;gap:6px;overflow-x:auto;padding:2px 0} #stickers::-webkit-scrollbar{display:none}
.st{font-size:22px;background:#fff;min-width:38px;height:34px;display:flex;align-items:center;justify-content:center;border-radius:20px;cursor:pointer;box-shadow:0 1px 1px rgba(0,0,0,.1)}
.row{display:flex;gap:6px;align-items:center}
.row input{padding:11px 14px;border-radius:25px;border:0;outline:none;font-size:15px}
#nameInput{flex:0.7;background:#fff9c4} #msgInput{flex:1.3}
.circle{width:44px;height:44px;border-radius:50%;border:0;background:#075e54;color:#fff;font-size:20px;display:flex;align-items:center;justify-content:center}
#micBtn{background:#25D366}
</style></head><body>
<div class=top>
<span class=brand>GH NOT</span>
<input id=roomInput value="open-thread">
<button onclick="joinRoom()">JOIN ROOM</button>
<button onclick="shareLink()" style="background:#128c7e">SHARE LINK</button>
</div>
<div id=chat></div>
<div class=bottom>
<div id=replyBox><span id=replyText></span><span onclick="cancelReply()" style="padding:0 8px;font-weight:bold">✕</span></div>
<div id=stickers>
<div class=st onclick="sendSticker('😂')">😂</div><div class=st onclick="sendSticker('❤️')">❤️</div><div class=st onclick="sendSticker('🔥')">🔥</div><div class=st onclick="sendSticker('💀')">💀</div><div class=st onclick="sendSticker('😭')">😭</div><div class=st onclick="sendSticker('🙏')">🙏</div><div class=st onclick="sendSticker('💯')">💯</div><div class=st onclick="sendSticker('🇬🇭')">🇬🇭</div>
</div>
<div class=row>
<input id=nameInput placeholder="Jerrick Smith" value="Jerrick Smith">
<button class=circle onclick="document.getElementById('fileInput').click()">📷</button>
<input id=msgInput placeholder="Hi">
<button class=circle id=micBtn onclick="toggleMic()">🎤</button>
<button class=circle onclick="sendMsg()" style="background:#25D366">➤</button>
</div>
</div>
<input type=file id=fileInput accept="image/*" style="display:none" onchange="sendFile(this)">
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
let socket=io(); let curRoom=new URLSearchParams(location.search).get('room')||'open-thread';
let replyTo=null; let mediaRecorder=null; let chunks=[]; let isRec=false;
document.getElementById('roomInput').value=curRoom;
function joinRoom(){ let r=document.getElementById('roomInput').value.trim()||'open-thread'; location.href='?room='+encodeURIComponent(r); }
function shareLink(){ navigator.clipboard.writeText(location.href); alert('Link copied: '+location.href); }
function cancelReply(){ replyTo=null; document.getElementById('replyBox').style.display='none'; }
socket.on('connect',()=>{ socket.emit('join',curRoom); });
socket.on('history',msgs=>{ document.getElementById('chat').innerHTML=''; msgs.forEach(addMsg); });
socket.on('new_message',addMsg);
function addMsg(m){
 let d=document.createElement('div'); d.className='msg'+(m.name==document.getElementById('nameInput').value?' me':'');
 let safeReply=''; if(m.reply){ let rt=m.reply; if(rt.length>80) rt=rt.substring(0,80); if(rt.includes('data:')) rt='[Media]'; safeReply=`<div class=reply-line>${rt}</div>`; }
 let body=''; if(m.type=='text') body=`<div>${m.text}</div>`; if(m.type=='sticker') body=`<div style="font-size:34px">${m.text}</div>`;
 if(m.type=='image') body=`<div><img src="${m.text}" style="max-width:100%;border-radius:8px"></div>`;
 if(m.type=='audio') body=`<div><audio controls src="${m.text}" style="width:200px"></audio></div>`;
 d.innerHTML=`<b>${m.name}</b>${safeReply}${body}<div class=time>${m.time||new Date().toLocaleTimeString()}</div>`;
 d.onclick=()=>{ replyTo=m; document.getElementById('replyBox').style.display='flex'; let rt=m.text||''; if(rt.includes('data:')||m.type!='text') rt='['+m.type+']'; document.getElementById('replyText').innerText='Reply to '+m.name+': '+rt.substring(0,30); };
 document.getElementById('chat').appendChild(d); window.scrollTo(0,document.body.scrollHeight);
}
function sendMsg(){
 let name=document.getElementById('nameInput').value.trim()||'Anon'; let text=document.getElementById('msgInput').value.trim(); if(!text) return;
 let replyStr=''; if(replyTo){ if(replyTo.type!='text') replyStr=replyTo.name+': ['+replyTo.type+']'; else replyStr=replyTo.name+': '+(replyTo.text||'').substring(0,40); }
 socket.emit('send',{room:curRoom,name:name,text:text,type:'text',reply:replyStr,time:new Date().toLocaleTimeString()});
 document.getElementById('msgInput').value=''; cancelReply();
}
function sendSticker(e){ let name=document.getElementById('nameInput').value.trim()||'Anon'; socket.emit('send',{room:curRoom,name:name,text:e,type:'sticker',reply:'',time:new Date().toLocaleTimeString()}); }
function sendFile(inp){ let f=inp.files[0]; if(!f) return; let reader=new FileReader(); reader.onload=e=>{ let name=document.getElementById('nameInput').value.trim()||'Anon'; socket.emit('send',{room:curRoom,name:name,text:e.target.result,type:'image',reply:'',time:new Date().toLocaleTimeString()}); }; reader.readAsDataURL(f); }
async function toggleMic(){
 let btn=document.getElementById('micBtn'); if(!isRec){
  try{ let s=await navigator.mediaDevices.getUserMedia({audio:true}); let mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':'audio/webm'; mediaRecorder=new MediaRecorder(s,{mimeType:mime}); chunks=[];
   mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
   mediaRecorder.onstop=()=>{ let blob=new Blob(chunks,{type:mediaRecorder.mimeType}); let reader=new FileReader(); reader.onload=e=>{ let name=document.getElementById('nameInput').value.trim()||'Anon'; socket.emit('send',{room:curRoom,name:name,text:e.target.result,type:'audio',reply:'',time:new Date().toLocaleTimeString()}); }; reader.readAsDataURL(blob); };
   mediaRecorder.start(); isRec=true; btn.innerText='⏹️'; btn.style.background='red';
  }catch(err){ alert('Mic error: '+err.message); }
 }else{ mediaRecorder.stop(); isRec=false; btn.innerText='🎤'; btn.style.background='#25D366'; mediaRecorder.stream.getTracks().forEach(t=>t.stop()); }
}
document.getElementById('msgInput').addEventListener('keydown',e=>{ if(e.key==='Enter') sendMsg(); });
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(): return HTML
@sio.on('join')
async def on_join(sid, room):
    await sio.enter_room(sid, room)
    await sio.emit('history', rooms_data[room], to=sid)
@sio.on('send')
async def on_send(sid, data):
    if len(data.get('text',''))>3500000: return
    room=data.get('room','open-thread'); rooms_data[room].append(data)
    if len(rooms_data[room])>300: rooms_data[room]=rooms_data[room][-300:]
    await sio.emit('new_message', data, room=room)
