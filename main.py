from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
import socketio
from collections import defaultdict

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)
rooms_data = defaultdict(list)

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "GH NOT - Ghana Chat",
        "short_name": "GH NOT",
        "description": "Ghana Anonymous Chat - No number needed",
        "start_url": "/?room=open-thread",
        "display": "standalone",
        "background_color": "#075e54",
        "theme_color": "#075e54",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/1384/1384023.png", "sizes": "512x512", "type": "image/png"},
            {"src": "https://cdn-icons-png.flaticon.com/512/1384/1384023.png", "sizes": "192x192", "type": "image/png"}
        ]
    })

@app.get("/sw.js")
async def sw():
    js = """
    self.addEventListener('install', e => self.skipWaiting());
    self.addEventListener('activate', e => self.clients.claim());
    self.addEventListener('fetch', e => {
        e.respondWith(fetch(e.request));
    });
    """
    return Response(content=js, media_type="application/javascript")

HTML = """<!DOCTYPE html><html><head>
<meta charset="utf-8">
<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover'>
<meta name="theme-color" content="#075e54">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1384/1384023.png">
<title>GH NOT - Ghana Chat App</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#efeae2;display:flex;flex-direction:column;height:100dvh}
.top{background:#075e54;color:#fff;padding:7px 6px;display:flex;flex-wrap:wrap;gap:5px;align-items:center;flex-shrink:0}
.brand{font-weight:900;font-size:14px;letter-spacing:0.5px}
#roomInput{flex:1 1 80px;min-width:0;padding:7px 10px;border-radius:20px;border:0;outline:none;font-size:12px;font-weight:700}
.btn{border-radius:20px;padding:6px 9px;font-weight:900;font-size:9px;cursor:pointer;white-space:nowrap;flex:0 0 auto;box-shadow:0 1px 2px rgba(0,0,0,.3);border:1px solid #fff}
.btn-join{background:#e8e8e8!important;color:#0d6efd!important}
.btn-share{background:#e8e8e8!important;color:#0d6efd!important}
.btn-momo{background:#ffdd00!important;color:#000!important;border-color:#000!important}
.btn-clear{background:#ff3b30!important;color:#fff!important}
.btn-install{background:#25D366!important;color:#fff!important;display:none}
#chat{flex:1;overflow-y:auto;padding:8px;-webkit-overflow-scrolling:touch}
.msg{position:relative;background:#fff;padding:6px 8px 18px;margin:6px 0;max-width:84%;border-radius:0 8px 8px 8px;box-shadow:0 1px 0.5px rgba(0,0,0,.2);word-break:break-word}
.me{background:#dcf8c6;margin-left:auto;border-radius:8px 0 8px 8px}
.msg b{font-size:12px;color:#075e54}
.time{position:absolute;bottom:1px;right:6px;font-size:9px;color:#667781;display:flex;gap:6px}
.del{color:#ff3b30;background:#fff0f0;padding:1px 5px;border-radius:10px;border:1px solid #ffd0d0;cursor:pointer}
.bottom{background:#f0f0f0;padding:5px 6px;border-top:1px solid #ddd;flex-shrink:0}
#replyBox{display:none;background:#fff;border-left:4px solid #25D366;padding:5px 8px;font-size:11px;margin-bottom:4px;justify-content:space-between;border-radius:4px}
#stickers{display:flex;gap:4px;overflow-x:auto;padding:2px 0}
#stickers::-webkit-scrollbar{display:none}
.st{background:#fff;min-width:34px;height:30px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 1px 1px rgba(0,0,0,.1);cursor:pointer;flex-shrink:0}
.row{display:flex;gap:4px;align-items:center}
.inp{border:0;border-radius:20px;padding:10px 12px;outline:none;font-size:14px;min-width:0}
#nameInput{flex:0 0 27%;background:#fff9c4;font-weight:700;font-size:12px}
#msgInput{flex:1;background:#fff}
.circle{width:38px;height:38px;border-radius:50%;border:0;color:#fff;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0}
#momoModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:999;align-items:center;justify-content:center;padding:20px}
.momoCard{background:#fff;border-radius:18px;padding:20px;width:100%;max-width:320px;text-align:center}
.momoNum{font-size:26px;font-weight:900;background:#ffecb3;padding:12px;border-radius:12px;margin:10px 0;letter-spacing:1px;border:2px dashed #f5a623}
#installBanner{display:none;background:#25D366;color:#fff;padding:8px 12px;text-align:center;font-size:12px;font-weight:700;cursor:pointer}
</style></head><body>
<div id=installBanner onclick="installApp()">📲 Tap to Install GH NOT App - Works like WhatsApp!</div>
<div class=top>
<span class=brand>GH NOT</span>
<input id=roomInput value="open-thread">
<button class=btn btn-join onclick="joinRoom()">JOIN</button>
<button class=btn btn-share onclick="shareLink()">SHARE</button>
<button class=btn btn-momo onclick="openMomo()">MOMO</button>
<button class=btn btn-clear onclick="clearAll()">CLEAR ALL</button>
<button class=btn btn-install id=installBtn onclick="installApp()">📲 INSTALL</button>
</div>
<div id=chat></div>
<div id=momoModal onclick="closeMomo()"><div class=momoCard onclick="event.stopPropagation()">
<h3 style="color:#075e54">Support GH NOT 🇬🇭</h3>
<p style="font-size:12px;color:#555;margin-top:4px">MTN MoMo</p>
<div class=momoNum>053 399 3024</div>
<p style="font-size:11px;color:#777">Jerrick Smith</p>
<button onclick="copyMomo()" class=btn btn-momo style="width:100%;padding:11px;margin-top:8px">COPY 0533993024</button>
<button onclick="closeMomo()" style="width:100%;margin-top:6px;padding:9px;border-radius:18px;border:0;background:#eee">Close</button>
</div></div>
<div class=bottom>
<div id=replyBox><span id=replyText></span><span onclick="cancelReply()" style="font-weight:900;padding:0 8px">✕</span></div>
<div id=stickers>
<div class=st onclick="sendSticker('😂')">😂</div><div class=st onclick="sendSticker('❤️')">❤️</div><div class=st onclick="sendSticker('🔥')">🔥</div><div class=st onclick="sendSticker('💀')">💀</div><div class=st onclick="sendSticker('😭')">😭</div><div class=st onclick="sendSticker('🙏')">🙏</div><div class=st onclick="sendSticker('💯')">💯</div><div class=st onclick="sendSticker('🇬🇭')">🇬🇭</div>
</div>
<div class=row>
<input id=nameInput class=inp placeholder="Your Name">
<button class=circle style="background:#54656f" onclick="document.getElementById('fileInput').click()">📷</button>
<input id=msgInput class=inp placeholder="Hi">
<button class=circle id=micBtn style="background:#25D366" onclick="toggleMic()">🎤</button>
<button class=circle style="background:#25D366" onclick="sendMsg()">➤</button>
</div>
</div>
<input type=file id=fileInput accept="image/*" style="display:none" onchange="sendFile(this)">
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
let deferredPrompt=null;
window.addEventListener('beforeinstallprompt', (e)=>{ e.preventDefault(); deferredPrompt=e; document.getElementById('installBtn').style.display='block'; document.getElementById('installBanner').style.display='block'; });
function installApp(){ if(deferredPrompt){ deferredPrompt.prompt(); deferredPrompt.userChoice.then(c=>{ if(c.outcome==='accepted'){ document.getElementById('installBanner').style.display='none'; } deferredPrompt=null; }); } else { alert('To install:\\nAndroid: Tap ⋮ > Add to Home screen / Install app\\niPhone: Tap Share > Add to Home Screen'); } }
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js'); }
let socket=io(), curRoom=localStorage.getItem('gh_room')||new URLSearchParams(location.search).get('room')||'open-thread', replyTo=null, mediaRecorder=null, chunks=[], isRec=false;
const $=id=>document.getElementById(id);
let savedName=localStorage.getItem('gh_name')||'Jerrick Smith';
$('nameInput').value=savedName;
$('roomInput').value=curRoom;
$('nameInput').addEventListener('input',()=>{ localStorage.setItem('gh_name',$('nameInput').value); });
$('roomInput').addEventListener('input',()=>{ localStorage.setItem('gh_room',$('roomInput').value); });
function joinRoom(){ let r=$('roomInput').value.trim()||'open-thread'; localStorage.setItem('gh_room',r); location.href='?room='+encodeURIComponent(r); }
function shareLink(){ let txt=`🇬🇭 Download GH NOT App - Ghana Chat!\\nNo number needed!\\n\\n👉 ${location.href}\\nRoom: ${curRoom}\\n\\n📲 Open > Tap INSTALL to add to phone!`; if(navigator.share){ navigator.share({title:'GH NOT App', text:txt, url:location.href}); } else { navigator.clipboard.writeText(txt).then(()=>alert('App link copied! Share to class group')); } }
function openMomo(){ $('momoModal').style.display='flex'; }
function closeMomo(){ $('momoModal').style.display='none'; }
function copyMomo(){ navigator.clipboard.writeText('0533993024'); alert('Copied: 0533993024 - Jerrick Smith'); }
function cancelReply(){ replyTo=null; $('replyBox').style.display='none'; }
function clearAll(){ if(confirm('⚠️ DELETE ALL MESSAGES FOR EVERYONE?\\nThis will clear chat for ALL people in room: '+curRoom)){ socket.emit('clear_all', {room:curRoom}); } }
socket.on('connect',()=>socket.emit('join',curRoom));
socket.on('history',ms=>{ $('chat').innerHTML=''; ms.forEach(addMsg); });
socket.on('new_message',addMsg);
socket.on('delete_msg',id=>{ let el=document.getElementById('msg-'+id); if(el) el.remove(); });
socket.on('clear_all',()=>{ $('chat').innerHTML='<div style="text-align:center;padding:30px 10px;color:#075e54"><div style="font-size:40px">🧹</div><div style="font-weight:900;margin-top:8px">Chat Cleared</div><div style="font-size:11px;color:#777;margin-top:4px">All messages deleted for everyone by admin</div></div>'; });
function addMsg(m){
 if(document.getElementById('msg-'+m.id)) return;
 let d=document.createElement('div'); d.id='msg-'+m.id; d.className='msg'+(m.name==$('nameInput').value?' me':'');
 let body=''; if(m.type=='text') body=`<div style="font-size:14px;white-space:pre-wrap">${m.text}</div>`;
 if(m.type=='sticker') body=`<div style="font-size:32px">${m.text}</div>`;
 if(m.type=='image') body=`<img src="${m.text}" style="max-width:100%;border-radius:8px;margin-top:3px">`;
 if(m.type=='audio') body=`<audio controls preload="metadata" src="${m.text}" style="width:190px;height:32px;margin-top:3px"></audio>`;
 let me=m.name==$('nameInput').value; let del=me?`<span class=del onclick="deleteMsg('${m.id}')">DELETE</span>`:'';
 d.innerHTML=`<b>${m.name}</b>${body}<div class=time><span>${m.time||''}</span>${del}</div>`;
 $('chat').appendChild(d); $('chat').scrollTop=$('chat').scrollHeight;
}
function getPayload(type,text){ return {id:'m'+Date.now()+Math.random().toString(36).slice(2,5), room:curRoom, name:($('nameInput').value.trim()||'Anon'), text:text, type:type, time:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})} }
function sendMsg(){ let t=$('msgInput').value.trim(); if(!t) return; localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('text',t)); $('msgInput').value=''; }
function sendSticker(e){ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('sticker',e)); }
function sendFile(inp){ let f=inp.files[0]; if(!f) return; if(f.size>3000000){ alert('Image too big max 3MB'); return; } let rd=new FileReader(); rd.onload=ev=>{ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('image',ev.target.result)); }; rd.readAsDataURL(f); }
function deleteMsg(id){ if(confirm('Delete this message for everyone?')) socket.emit('delete',{room:curRoom,id:id}); }
async function toggleMic(){
 let b=$('micBtn'); if(!isRec){
  try{ let s=await navigator.mediaDevices.getUserMedia({audio:true}); let mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':'audio/webm'; mediaRecorder=new MediaRecorder(s,{mimeType:mime}); chunks=[]; mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); }; mediaRecorder.onstop=()=>{ let blob=new Blob(chunks,{type:mediaRecorder.mimeType}); if(blob.size>3000000){ alert('Voice too long'); return; } let rd=new FileReader(); rd.onload=e=>{ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('audio',e.target.result)); }; rd.readAsDataURL(blob); }; mediaRecorder.start(); isRec=true; b.textContent='■'; b.style.background='red'; }catch(err){ alert('Mic blocked: '+err.message); }
 }else{ try{mediaRecorder.stop(); mediaRecorder.stream.getTracks().forEach(t=>t.stop());}catch{} isRec=false; b.textContent='🎤'; b.style.background='#25D366'; }
}
$('msgInput').addEventListener('keydown',e=>{ if(e.key==='Enter') sendMsg(); });
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
    if len(data.get('text',''))>3500000:
        return
    room=data.get('room','open-thread')
    rooms_data[room].append(data)
    if len(rooms_data[room])>400:
        rooms_data[room]=rooms_data[room][-400:]
    await sio.emit('new_message', data, room=room)

@sio.on('delete')
async def on_delete(sid, data):
    room=data.get('room','open-thread')
    mid=data.get('id')
    rooms_data[room]=[m for m in rooms_data[room] if m.get('id')!=mid]
    await sio.emit('delete_msg', mid, room=room)

@sio.on('clear_all')
async def on_clear(sid, data):
    room=data.get('room','open-thread')
    rooms_data[room]=[]
    await sio.emit('clear_all', {}, room=room)
