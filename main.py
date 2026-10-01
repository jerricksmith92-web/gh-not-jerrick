from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
import socketio
from collections import defaultdict
import json, os

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# 100% PERMANENT - SAVES TO DISK /data IF EXISTS, ELSE LOCAL
POSSIBLE_PATHS = ["/data/gh_rooms.json", "gh_rooms.json", "/tmp/gh_rooms.json"]
DB_FILE = None
rooms_data = defaultdict(list)

# Try load from any existing file
for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        try:
            with open(p, "r") as f:
                d=json.load(f)
                for k,v in d.items():
                    rooms_data[k]=v
            DB_FILE = p
            print(f"Loaded from {p}")
            break
        except: pass

# Choose where to save
if not DB_FILE:
    if os.path.exists("/data"):
        DB_FILE = "/data/gh_rooms.json"
    else:
        DB_FILE = "gh_rooms.json"

def save_db():
    try:
        with open(DB_FILE, "w") as f:
            json.dump(dict(rooms_data), f)
        # backup
        try:
            with open("gh_rooms.json", "w") as f:
                json.dump(dict(rooms_data), f)
        except: pass
    except Exception as e:
        print("save error", e)

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "GH NOT - Ghana Chat",
        "short_name": "GH NOT",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#075e54",
        "theme_color": "#075e54",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/5962/5962463.png", "sizes": "192x192", "type": "image/png"},
            {"src": "https://cdn-icons-png.flaticon.com/512/5962/5962463.png", "sizes": "512x512", "type": "image/png"}
        ]
    })

@app.get("/sw.js")
async def sw():
    js="self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());self.addEventListener('fetch',e=>{e.respondWith(fetch(e.request))});"
    return Response(content=js, media_type="application/javascript", headers={"Cache-Control":"no-cache"})

HTML="""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'>
<meta name="theme-color" content="#075e54">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/5962/5962463.png">
<title>GH NOT App</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:sans-serif;background:#efeae2;display:flex;flex-direction:column;height:100dvh}
@keyframes pulse{0%{opacity:1}50%{opacity:.5}100%{opacity:1}}
.top{background:#075e54;color:#fff;padding:6px 6px;display:flex;flex-wrap:wrap;gap:5px;align-items:center;flex-shrink:0}
.brand{font-weight:900;font-size:14px}
#roomInput{flex:1 1 70px;min-width:0;padding:7px 10px;border-radius:20px;border:0;outline:none;font-size:12px;font-weight:700}
.btn{border-radius:20px;padding:6px 9px;font-weight:900;font-size:9px;cursor:pointer;white-space:nowrap;flex:0 0 auto;box-shadow:0 1px 2px rgba(0,0,0,.3)}
.btn-join{background:#e8e8e8!important;color:#0d6efd!important;border:1px solid #fff!important}
.btn-share{background:#e8e8e8!important;color:#0d6efd!important;border:1px solid #fff!important}
.btn-momo{background:#ffdd00!important;color:#000!important;border:1px solid #000!important}
.btn-clear{background:#ff3b30!important;color:#fff!important;border:1px solid #fff!important}
.btn-install{background:#25D366!important;color:#fff!important;border:1px solid #fff!important}
#chat{flex:1;overflow-y:auto;padding:8px}
.msg{position:relative;background:#fff;padding:6px 8px 18px 8px;margin:6px 0;max-width:84%;border-radius:0 8px 8px 8px;box-shadow:0 1px.5px rgba(0,0,0,.2);word-break:break-word}
.me{background:#dcf8c6;margin-left:auto;border-radius:8px 0 8px 8px}
.msg b{font-size:12px;color:#075e54}
.replyPreview{background:rgba(0,0,0,.06);border-left:3px solid #25D366;padding:4px 6px;border-radius:4px;font-size:11px;margin-bottom:4px;color:#555}
.time{position:absolute;bottom:1px;right:6px;font-size:9px;color:#667781;display:flex;gap:6px;align-items:center}
.del{color:#ff3b30;background:#fff0f0;padding:1px 5px;border-radius:10px;border:1px solid #ffd0d0;cursor:pointer}
.rep{color:#0d6efd;background:#e8f0ff;padding:1px 6px;border-radius:10px;border:1px solid #c0d4ff;cursor:pointer;font-weight:900}
.bottom{background:#f0f0f0;padding:5px 6px;border-top:1px solid #ddd;flex-shrink:0}
#replyBox{display:none;background:#fff;border-left:4px solid #25D366;padding:6px 8px;font-size:12px;margin-bottom:4px;justify-content:space-between;border-radius:4px;align-items:center}
#stickers{display:flex;gap:4px;overflow-x:auto;padding:2px 0}
#stickers::-webkit-scrollbar{display:none}
.st{background:#fff;min-width:34px;height:30px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 1px 1px rgba(0,0,0,.1);cursor:pointer;flex-shrink:0}
.row{display:flex;gap:4px;align-items:center}
.inp{border:0;border-radius:20px;padding:10px 12px;outline:none;font-size:14px;min-width:0}
#nameInput{flex:0 0 34%;background:#fff9c4;font-weight:800;font-size:12px;border:1.8px solid #ffca28}
#msgInput{flex:1;background:#fff}
.circle{width:38px;height:38px;border-radius:50%;border:0;color:#fff;font-size:16px;display:flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0}
#momoModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:999;align-items:center;justify-content:center;padding:20px}
.momoCard{background:#fff;border-radius:18px;padding:20px;width:100%;max-width:320px;text-align:center}
.momoNum{font-size:26px;font-weight:900;background:#ffecb3;padding:12px;border-radius:12px;margin:10px 0;border:2px dashed #f5a623}
#installBanner{background:#25D366;color:#fff;padding:10px;text-align:center;font-size:13px;font-weight:800;display:none}
#installHelp{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);z-index:1000;align-items:center;justify-content:center;padding:20px}
.helpCard{background:#fff;border-radius:16px;padding:20px;max-width:360px;width:100%}
</style></head><body>
<div id=installBanner onclick="showInstallHelp()">📲 TAP TO INSTALL GH NOT APP!</div>
<div id=installHelp onclick="this.style.display='none'"><div class=helpCard onclick="event.stopPropagation()">
<h3>📲 How to Install</h3>
<p style="margin:10px 0"><b>Android:</b> ⋮ > Add to Home screen > Install</p>
<p style="margin:10px 0"><b>iPhone:</b> Share [ ] > Add to Home Screen > Add</p>
<button onclick="document.getElementById('installHelp').style.display='none'" style="width:100%;padding:10px;background:#075e54;color:#fff;border:0;border-radius:20px;font-weight:800">Got it</button>
</div></div>
<div class=top>
<span class=brand>GH NOT</span>
<input id=roomInput value="open-thread">
<button class=btn btn-join onclick="joinRoom()">JOIN</button>
<button class=btn btn-share onclick="shareLink()">SHARE</button>
<button class=btn btn-momo onclick="openMomo()">MOMO</button>
<button class=btn btn-clear onclick="clearAll()">CLEAR ALL</button>
<button class=btn btn-install id=installBtn>📲 INSTALL</button>
</div>
<div id=chat></div>
<div id=momoModal onclick="closeMomo()"><div class=momoCard onclick="event.stopPropagation()">
<h3>Support GH NOT 🇬🇭</h3><div class=momoNum>053 399 3024</div>
<button onclick="navigator.clipboard.writeText('0533993024');alert('Copied')" class=btn btn-momo style="width:100%;padding:12px">COPY</button>
<button onclick="closeMomo()" style="width:100%;margin-top:8px;padding:10px;border-radius:20px;border:0;background:#eee">Close</button>
</div></div>
<div class=bottom>
<div id=replyBox><div><b id=replyName style="color:#25D366"></b><div id=replyText style="color:#666"></div></div><span onclick="cancelReply()" style="font-weight:900;padding:0 8px;font-size:18px">✕</span></div>
<div id=stickers>
<div class=st onclick="sendSticker('😂')">😂</div><div class=st onclick="sendSticker('❤️')">❤️</div><div class=st onclick="sendSticker('🔥')">🔥</div><div class=st onclick="sendSticker('💀')">💀</div><div class=st onclick="sendSticker('😭')">😭</div><div class=st onclick="sendSticker('🙏')">🙏</div><div class=st onclick="sendSticker('💯')">💯</div><div class=st onclick="sendSticker('🇬🇭')">🇬🇭</div>
</div>
<div class=row>
<input id=nameInput class=inp placeholder="Enter your name...">
<button class=circle style="background:#54656f" onclick="document.getElementById('fileInput').click()">📷</button>
<input id=msgInput class=inp placeholder="Message">
<button class=circle id=micBtn style="background:#25D366" onclick="toggleMic()">🎤</button>
<button class=circle style="background:#25D366" onclick="sendMsg()">➤</button>
</div>
</div>
<input type=file id=fileInput accept="image/*" style="display:none" onchange="sendFile(this)">
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
let deferredPrompt=null;
const installBtn=document.getElementById('installBtn');
const banner=document.getElementById('installBanner');
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredPrompt=e;installBtn.style.display='block';banner.style.display='block';});
installBtn.addEventListener('click',async()=>{if(deferredPrompt){deferredPrompt.prompt();await deferredPrompt.userChoice;deferredPrompt=null;installBtn.style.display='none';banner.style.display='none';}else{showInstallHelp();}});
function showInstallHelp(){document.getElementById('installHelp').style.display='flex';}
function installApp(){if(deferredPrompt){deferredPrompt.prompt();}else{showInstallHelp();}}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(()=>{});}
setTimeout(()=>{if(!window.matchMedia('(display-mode: standalone)').matches){banner.style.display='block';}},3000);
let urlRoom=new URLSearchParams(location.search).get('room');
let socket=io(), curRoom=urlRoom||localStorage.getItem('gh_room')||'open-thread', replyTo=null, mediaRecorder=null, chunks=[], isRec=false; if(urlRoom){localStorage.setItem('gh_room',urlRoom);}
const $=id=>document.getElementById(id);
$('nameInput').value=localStorage.getItem('gh_name')||'';
$('roomInput').value=curRoom;
$('nameInput').addEventListener('input',()=>localStorage.setItem('gh_name',$('nameInput').value));
$('roomInput').addEventListener('input',()=>localStorage.setItem('gh_room',$('roomInput').value));
function joinRoom(){let r=$('roomInput').value.trim()||'open-thread';localStorage.setItem('gh_room',r);location.href='?room='+encodeURIComponent(r);}
function shareLink(){let txt=`GH NOT App 🇬🇭\\n${location.href}`;navigator.clipboard.writeText(txt).then(()=>alert('Link copied!'));}
function openMomo(){$('momoModal').style.display='flex';}
function closeMomo(){$('momoModal').style.display='none';}
function cancelReply(){replyTo=null;$('replyBox').style.display='none';}
function setReply(id,name,text){replyTo={id:id,name:name,text:text.substring(0,60)};$('replyName').textContent='Replying to '+name;$('replyText').textContent=text.substring(0,80);$('replyBox').style.display='flex';$('msgInput').focus();}
function clearAll(){if(confirm('DELETE ALL FOR EVERYONE?')){socket.emit('clear_all',{room:curRoom});}}
socket.on('connect',()=>socket.emit('join',curRoom));
socket.on('history',ms=>{$('chat').innerHTML='';ms.forEach(addMsg);});
socket.on('new_message',addMsg);
socket.on('delete_msg',id=>{let el=document.getElementById('msg-'+id);if(el) el.remove();});
socket.on('clear_all',()=>{$('chat').innerHTML='<div style="text-align:center;padding:20px;color:#777">Chat cleared</div>';});
function addMsg(m){
 if(document.getElementById('msg-'+m.id)) return;
 let d=document.createElement('div');d.id='msg-'+m.id;d.className='msg'+(m.name==$('nameInput').value?' me':'');
 let replyHtml='';if(m.replyTo){replyHtml=`<div class=replyPreview><b>${m.replyTo.name}</b>: ${m.replyTo.text}</div>`;}
 let body='';if(m.type=='text') body=`<div style="font-size:14px;white-space:pre-wrap">${m.text}</div>`;
 if(m.type=='sticker') body=`<div style="font-size:32px">${m.text}</div>`;
 if(m.type=='image') body=`<img src="${m.text}" style="max-width:100%;border-radius:8px">`;
 if(m.type=='audio') body=`<audio controls src="${m.text}" style="width:200px;height:36px"></audio>`;
 let me=m.name==$('nameInput').value;let del=me?`<span class=del onclick="deleteMsg('${m.id}')">DEL</span>`:'';
 let repBtn=`<span class=rep onclick="setReply('${m.id}','${m.name.replace(/'/g, "\\'")}','${(m.text||'').toString().substring(0,50).replace(/'/g, "\\'").replace(/"/g,'&quot;')}')">↩️ REPLY</span>`;
 d.innerHTML=`<b>${m.name}</b>${replyHtml}${body}<div class=time><span>${m.time||''}</span>${repBtn}${del}</div>`;
 $('chat').appendChild(d);$('chat').scrollTop=$('chat').scrollHeight;
}
function getPayload(t,txt){let p={id:'m'+Date.now()+Math.random().toString(36).slice(2,5),room:curRoom,name:($('nameInput').value.trim()||'Anon'),text:txt,type:t,time:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})};if(replyTo){p.replyTo=replyTo;}return p;}
function sendMsg(){
 if(!$('nameInput').value.trim()){alert('Please enter your name first!');$('nameInput').focus();return;}
 let v=$('msgInput').value.trim();if(!v) return;localStorage.setItem('gh_name',$('nameInput').value.trim());socket.emit('send',getPayload('text',v));$('msgInput').value='';cancelReply();
}
function sendSticker(e){
 if(!$('nameInput').value.trim()){alert('Please enter your name first!');$('nameInput').focus();return;}
 localStorage.setItem('gh_name',$('nameInput').value.trim());socket.emit('send',getPayload('sticker',e));cancelReply();
}
function sendFile(inp){
 if(!$('nameInput').value.trim()){alert('Please enter your name first!');$('nameInput').focus();return;}
 let f=inp.files[0];if(!f) return;let r=new FileReader();r.onload=ev=>{socket.emit('send',getPayload('image',ev.target.result));cancelReply();};r.readAsDataURL(f);
}
function deleteMsg(id){socket.emit('delete',{room:curRoom,id:id});}
async function toggleMic(){
 if(!$('nameInput').value.trim()){alert('Please enter your name first!');$('nameInput').focus();return;}
 let b=$('micBtn');
 if(!isRec){
  try{
   let stream=await navigator.mediaDevices.getUserMedia({audio:true});
   let mimeType='';
   if(MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mimeType='audio/webm;codecs=opus';
   else if(MediaRecorder.isTypeSupported('audio/webm')) mimeType='audio/webm';
   else if(MediaRecorder.isTypeSupported('audio/mp4')) mimeType='audio/mp4';
   else if(MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) mimeType='audio/ogg;codecs=opus';
   mediaRecorder = mimeType? new MediaRecorder(stream,{mimeType:mimeType}) : new MediaRecorder(stream);
   chunks=[];
   mediaRecorder.ondataavailable=e=>{if(e.data.size>0) chunks.push(e.data);};
   mediaRecorder.onerror=e=>{alert('Mic error: '+e.error);isRec=false;b.textContent='🎤';b.style.background='#25D366';};
   mediaRecorder.onstop=()=>{
    if(chunks.length==0){alert('No audio - hold longer');return;}
    let blob=new Blob(chunks,{type:mimeType||'audio/webm'});
    if(blob.size>800000){alert('Voice too long, keep under 30sec');return;}
    let rd=new FileReader();
    rd.onload=e=>{socket.emit('send',getPayload('audio',e.target.result));cancelReply();};
    rd.readAsDataURL(blob);
   };
   mediaRecorder.start();
   isRec=true;b.textContent='■ STOP';b.style.background='red';b.style.animation='pulse 1s infinite';
   setTimeout(()=>{if(isRec) toggleMic();},30000);
  }catch(err){alert('Mic blocked! Allow mic in settings. Error: '+err.message);}
 }else{
  try{mediaRecorder.stop();mediaRecorder.stream.getTracks().forEach(t=>t.stop());}catch{}
  isRec=false;b.textContent='🎤';b.style.background='#25D366';b.style.animation='';
 }
}
$('msgInput').addEventListener('keydown',e=>{if(e.key==='Enter') sendMsg();});
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
    room=data.get('room','open-thread')
    rooms_data[room].append(data)
    if len(rooms_data[room])>400:
        rooms_data[room]=rooms_data[room][-400:]
    save_db()
    await sio.emit('new_message', data, room=room)
@sio.on('delete')
async def on_delete(sid, data):
    room=data.get('room'); mid=data.get('id')
    rooms_data[room]=[m for m in rooms_data[room] if m.get('id')!=mid]
    save_db()
    await sio.emit('delete_msg', mid, room=room)
@sio.on('clear_all')
async def on_clear(sid, data):
    room=data.get('room')
    rooms_data[room]=[]
    save_db()
    await sio.emit('clear_all', {}, room=room)
