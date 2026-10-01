from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import socketio
from collections import defaultdict

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)
rooms_data = defaultdict(list)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover'>
<title>GH NOT</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#efeae2;display:flex;flex-direction:column;height:100dvh}
.top{background:#075e54;color:#fff;padding:7px 8px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;flex-shrink:0;position:sticky;top:0;z-index:10}
.brand{font-weight:900;font-size:16px;letter-spacing:0.5px;flex:0 0 auto}
#roomInput{flex:1 1 90px;min-width:0;padding:9px 14px;border-radius:20px;border:0;outline:none;font-size:13px;font-weight:600}
.btn{border-radius:20px;padding:8px 14px;font-weight:900;font-size:11px;cursor:pointer;white-space:nowrap;flex:0 0 auto;box-shadow:0 1px 3px rgba(0,0,0,0.3)}
.btn-join{background:#25D366!important;color:#ffffff!important;border:2px solid #fff!important}
.btn-share{background:#0096FF!important;color:#ffffff!important;border:2px solid #fff!important}
.btn-momo{background:#FFD700!important;color:#000000!important;border:2px solid #000!important}
#chat{flex:1;overflow-y:auto;padding:8px;-webkit-overflow-scrolling:touch}
.msg{position:relative;background:#fff;padding:6px 8px 18px;margin:6px 0;max-width:84%;border-radius:0 8px 8px 8px;box-shadow:0 1px 0.5px rgba(0,0,0,.2);word-break:break-word}
.me{background:#dcf8c6;margin-left:auto;border-radius:8px 0 8px 8px}
.msg b{font-size:12px;color:#075e54;display:block;margin-bottom:2px}
.reply{border-left:3px solid #25D366;background:rgba(0,0,0,.06);padding:3px 6px;margin:3px 0;border-radius:3px;font-size:11px;color:#555;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.time{position:absolute;bottom:2px;right:6px;font-size:9px;color:#667781;display:flex;gap:8px;align-items:center}
.del{color:#ff3b30;background:#fff0f0;padding:1px 6px;border-radius:10px;border:1px solid #ffd0d0;cursor:pointer;font-weight:700}
.bottom{background:#f0f0f0;padding:6px 6px 8px;border-top:1px solid #ddd;flex-shrink:0}
#replyBox{display:none;background:#fff;border-left:4px solid #25D366;padding:6px 8px;font-size:11px;margin-bottom:6px;justify-content:space-between;border-radius:4px;align-items:center}
#stickers{display:flex;gap:5px;overflow-x:auto;padding:3px 0 5px;scrollbar-width:none}
#stickers::-webkit-scrollbar{display:none}
.st{background:#fff;min-width:36px;height:32px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 1px 2px rgba(0,0,0,.15);cursor:pointer;flex-shrink:0;border:1px solid #eee}
.row{display:flex;gap:5px;align-items:center;margin-top:4px}
.inp{border:0;border-radius:20px;padding:11px 13px;outline:none;font-size:14px;min-width:0}
#nameInput{flex:0 0 32%;background:#fff9c4;font-weight:700;font-size:13px;border:1px solid #f0d060}
#msgInput{flex:1;background:#fff;border:1px solid #ddd}
.circle{width:40px;height:40px;border-radius:50%;border:0;color:#fff;font-size:17px;display:flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0;box-shadow:0 1px 2px rgba(0,0,0,0.2)}
#momoModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:9999;align-items:center;justify-content:center;padding:20px}
.momoCard{background:#fff;border-radius:20px;padding:22px;width:100%;max-width:330px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3)}
.momoNum{font-size:26px;font-weight:900;background:#ffecb3;padding:14px;border-radius:14px;margin:12px 0;letter-spacing:1px;border:2px dashed #f5a623}
</style>
</head>
<body>
<div class=top>
<span class=brand>GH NOT</span>
<input id=roomInput value="open-thread">
<button class=btn btn-join onclick="joinRoom()">JOIN</button>
<button class=btn btn-share onclick="shareLink()">SHARE</button>
<button class=btn btn-momo onclick="openMomo()">MOMO</button>
</div>

<div id=chat></div>

<div id=momoModal onclick="closeMomo()">
<div class=momoCard onclick="event.stopPropagation()">
<h3 style="color:#075e54;margin-bottom:4px">Support GH NOT 🇬🇭</h3>
<p style="font-size:13px;color:#666">MTN Mobile Money</p>
<div class=momoNum>053 399 3024</div>
<p style="font-size:12px;color:#888;margin-bottom:4px">Name: Jerrick Smith</p>
<button onclick="copyMomo()" class=btn btn-momo style="width:100%;padding:12px;margin-top:10px;font-size:13px">COPY 0533993024</button>
<button onclick="closeMomo()" style="width:100%;margin-top:8px;padding:10px;border-radius:20px;border:0;background:#eee;font-weight:700;cursor:pointer">Close</button>
</div>
</div>

<div class=bottom>
<div id=replyBox><span id=replyText></span><span onclick="cancelReply()" style="font-weight:900;padding:0 10px;font-size:14px;cursor:pointer">✕</span></div>
<div id=stickers>
<div class=st onclick="sendSticker('😂')">😂</div>
<div class=st onclick="sendSticker('❤️')">❤️</div>
<div class=st onclick="sendSticker('🔥')">🔥</div>
<div class=st onclick="sendSticker('💀')">💀</div>
<div class=st onclick="sendSticker('😭')">😭</div>
<div class=st onclick="sendSticker('🙏')">🙏</div>
<div class=st onclick="sendSticker('💯')">💯</div>
<div class=st onclick="sendSticker('🇬🇭')">🇬🇭</div>
</div>
<div class=row>
<input id=nameInput class=inp placeholder="Your Name">
<button class=circle style="background:#54656f" onclick="document.getElementById('fileInput').click()">📷</button>
<input id=msgInput class=inp placeholder="Type message...">
<button class=circle id=micBtn style="background:#25D366" onclick="toggleMic()">🎤</button>
<button class=circle style="background:#25D366" onclick="sendMsg()">➤</button>
</div>
</div>

<input type=file id=fileInput accept="image/*" style="display:none" onchange="sendFile(this)">

<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
let socket=io(), curRoom=localStorage.getItem('gh_room')||new URLSearchParams(location.search).get('room')||'open-thread', replyTo=null, mediaRecorder=null, chunks=[], isRec=false;
const $=id=>document.getElementById(id);
let savedName=localStorage.getItem('gh_name')||'Jerrick Smith';
$('nameInput').value=savedName;
$('roomInput').value=curRoom;
$('nameInput').addEventListener('input',()=>localStorage.setItem('gh_name',$('nameInput').value));
$('roomInput').addEventListener('input',()=>localStorage.setItem('gh_room',$('roomInput').value));
function joinRoom(){ let r=$('roomInput').value.trim()||'open-thread'; localStorage.setItem('gh_room',r); location.href='?room='+encodeURIComponent(r); }
function shareLink(){ navigator.clipboard.writeText(location.href).then(()=>alert('Link copied! '+location.href)).catch(()=>{ prompt('Copy this link:', location.href); }); }
function openMomo(){ $('momoModal').style.display='flex'; }
function closeMomo(){ $('momoModal').style.display='none'; }
function copyMomo(){ navigator.clipboard.writeText('0533993024').then(()=>alert('Copied: 0533993024')).catch(()=>{ prompt('Copy MoMo:', '0533993024'); }); }
function cancelReply(){ replyTo=null; $('replyBox').style.display='none'; }
socket.on('connect',()=>socket.emit('join',curRoom));
socket.on('history',ms=>{ $('chat').innerHTML=''; ms.forEach(addMsg); });
socket.on('new_message',addMsg);
socket.on('delete_msg',id=>{ let el=document.getElementById('msg-'+id); if(el) el.remove(); });
function addMsg(m){
 if(document.getElementById('msg-'+m.id)) return;
 let d=document.createElement('div'); d.id='msg-'+m.id; d.className='msg'+(m.name==$('nameInput').value?' me':'');
 let rp=''; if(m.reply){ let t=m.reply; if(t.includes('data:')) t='[Media]'; if(t.length>55) t=t.slice(0,55)+'...'; rp=`<div class=reply>${t}</div>`; }
 let body='';
 if(m.type=='text') body=`<div style="font-size:14px;white-space:pre-wrap;line-height:1.3">${m.text}</div>`;
 if(m.type=='sticker') body=`<div style="font-size:34px">${m.text}</div>`;
 if(m.type=='image') body=`<img src="${m.text}" style="max-width:100%;border-radius:10px;margin-top:4px;display:block">`;
 if(m.type=='audio') body=`<audio controls preload="metadata" src="${m.text}" style="width:200px;height:36px;margin-top:4px"></audio>`;
 let me=m.name==$('nameInput').value; let del=me?`<span class=del onclick="deleteMsg('${m.id}')">DELETE</span>`:'';
 d.innerHTML=`<b>${m.name}</b>${rp}${body}<div class=time><span>${m.time||''}</span>${del}</div>`;
 d.addEventListener('click',e=>{ if(e.target.classList.contains('del')) return; replyTo=m; $('replyBox').style.display='flex'; let rt=m.type=='text'?m.text:'['+m.type.toUpperCase()+']'; if(rt.includes('data:')) rt='[Media]'; $('replyText').innerText='Reply to '+m.name+': '+rt.slice(0,30); });
 $('chat').appendChild(d); $('chat').scrollTop=$('chat').scrollHeight;
}
function getPayload(type,text,reply=''){
 return {id:'m'+Date.now()+Math.random().toString(36).slice(2,5), room:curRoom, name:($('nameInput').value.trim()||'Anon'), text:text, type:type, reply:reply, time:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}
}
function sendMsg(){
 let t=$('msgInput').value.trim(); if(!t) return;
 localStorage.setItem('gh_name',$('nameInput').value.trim());
 let r=''; if(replyTo){ r=replyTo.type!='text'?replyTo.name+': ['+replyTo.type+']':replyTo.name+': '+(replyTo.text||'').slice(0,45); }
 socket.emit('send',getPayload('text',t,r)); $('msgInput').value=''; cancelReply();
}
function sendSticker(e){ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('sticker',e)); }
function sendFile(inp){
 let f=inp.files[0]; if(!f) return;
 if(f.size>3500000){ alert('Image too big! Max 3.5MB'); inp.value=''; return; }
 let rd=new FileReader();
 rd.onload=ev=>{ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('image',ev.target.result)); inp.value=''; };
 rd.readAsDataURL(f);
}
function deleteMsg(id){ if(confirm('Delete for everyone?')) socket.emit('delete',{room:curRoom,id:id}); }
async function toggleMic(){
 let b=$('micBtn');
 if(!isRec){
  try{
   let s=await navigator.mediaDevices.getUserMedia({audio:true});
   let mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':MediaRecorder.isTypeSupported('audio/webm;codecs=opus')?'audio/webm;codecs=opus':'audio/webm';
   mediaRecorder=new MediaRecorder(s,{mimeType:mime});
   chunks=[];
   mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
   mediaRecorder.onstop=()=>{
    let blob=new Blob(chunks,{type:mediaRecorder.mimeType});
    if(blob.size>4000000){ alert('Voice too long! Max 30 sec'); return; }
    let rd=new FileReader();
    rd.onload=e=>{ localStorage.setItem('gh_name',$('nameInput').value.trim()); socket.emit('send',getPayload('audio',e.target.result)); };
    rd.readAsDataURL(blob);
   };
   mediaRecorder.start(); isRec=true; b.textContent='■'; b.style.background='red';
  }catch(err){ alert('Mic error: '+err.message+' - Allow mic in settings'); }
 }else{
  try{mediaRecorder.stop(); mediaRecorder.stream.getTracks().forEach(t=>t.stop());}catch{}
  isRec=false; b.textContent='🎤'; b.style.background='#25D366';
 }
}
$('msgInput').addEventListener('keydown',e=>{ if(e.key==='Enter') sendMsg(); });
</script>
</body>
</html>
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
    if len(data.get('text','')) > 4000000:
        return
    room = data.get('room', 'open-thread')
    rooms_data[room].append(data)
    if len(rooms_data[room]) > 500:
        rooms_data[room] = rooms_data[room][-500:]
    await sio.emit('new_message', data, room=room)

@sio.on('delete')
async def on_delete(sid, data):
    room = data.get('room', 'open-thread')
    mid = data.get('id')
    rooms_data[room] = [m for m in rooms_data[room] if m.get('id')!= mid]
    await sio.emit('delete_msg', mid, room=room)
