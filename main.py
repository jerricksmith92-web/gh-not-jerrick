from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
import socketio, json, os, time, uuid

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

DB_FILE = '/data/gh_not.json' if os.path.exists('/data') else 'gh_not.json'
db = {'users': {}, 'chats': {}, 'statuses': []}

try:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            old = json.load(f)
            if isinstance(old, dict): db.update(old)
except Exception: pass
for k in ('users','chats','statuses'): db.setdefault(k, {} if k != 'statuses' else [])

# Import old room messages without forcing users into one shared room.
if not db['chats']:
    for p in ['/data/gh_rooms.json','gh_rooms.json','/tmp/gh_rooms.json']:
        try:
            if os.path.exists(p):
                with open(p,'r',encoding='utf-8') as f: old=json.load(f)
                if isinstance(old,dict):
                    msgs=old.get('open-thread',[])
                    if msgs: db['chats']['legacy:legacy']=msgs
                break
        except Exception: pass

def save_db():
    try:
        tmp=DB_FILE+'.tmp'
        with open(tmp,'w',encoding='utf-8') as f: json.dump(db,f,ensure_ascii=False)
        os.replace(tmp,DB_FILE)
    except Exception: pass

def key(a,b): return ':'.join(sorted([str(a),str(b)]))

def user(uid,name=None):
    u=db['users'].get(uid,{})
    u['id']=uid
    u['name']=(name or u.get('name') or 'User').strip()[:40]
    u['about']=u.get('about','Hey there! I am using GH NOT.')[:80]
    u['last_seen']=time.time()
    db['users'][uid]=u
    return u

def public_users():
    now=time.time()
    return [{**u,'online':now-u.get('last_seen',0)<45} for u in db['users'].values()]

def clean_statuses():
    now=time.time()
    db['statuses']=[s for s in db.get('statuses',[]) if s.get('expires',0)>now]

@app.get('/manifest.json')
async def manifest():
    return JSONResponse({'name':'GH NOT','short_name':'GH NOT','start_url':'/','scope':'/','display':'standalone','background_color':'#efeae2','theme_color':'#075e54','icons':[{'src':'https://cdn-icons-png.flaticon.com/512/5962/5962463.png','sizes':'192x192','type':'image/png'},{'src':'https://cdn-icons-png.flaticon.com/512/5962/5962463.png','sizes':'512x512','type':'image/png'}]})

@app.get('/sw.js')
async def sw():
    js='self.addEventListener("install",e=>self.skipWaiting());self.addEventListener("activate",e=>self.clients.claim());self.addEventListener("fetch",e=>e.respondWith(fetch(e.request)));'
    return Response(js,media_type='application/javascript',headers={'Cache-Control':'no-cache'})

HTML=r'''<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#075e54"><meta name="apple-mobile-web-app-capable" content="yes"><link rel="manifest" href="/manifest.json"><title>GH NOT</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%;overflow:hidden}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;background:#d7dbd5;color:#111b21}button,input,textarea{font:inherit}
#app{height:100dvh;max-width:1150px;margin:auto;display:flex;background:#f0f2f5;overflow:hidden;box-shadow:0 0 15px #999}
.side{width:390px;background:#fff;border-right:1px solid #d1d7db;display:flex;flex-direction:column}.head{height:64px;background:#075e54;color:#fff;display:flex;align-items:center;padding:8px 10px;gap:10px}.avatar{width:44px;height:44px;min-width:44px;border-radius:50%;background:linear-gradient(145deg,#25d366,#128c7e);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800}.title{font-size:18px;font-weight:800;flex:1}.ico{width:38px;height:38px;border:0;border-radius:50%;background:transparent;color:inherit;font-size:21px;cursor:pointer}.ico:active{background:#ffffff22}
.tabs{height:47px;display:flex;background:#fff;border-bottom:1px solid #e9edef}.tab{flex:1;border:0;background:#fff;color:#667781;font-size:12px;font-weight:800;border-bottom:3px solid transparent}.tab.active{color:#075e54;border-color:#25d366}.search{padding:8px;background:#f0f2f5}.search input{width:100%;border:0;outline:0;border-radius:20px;padding:9px 13px;font-size:14px}.list{flex:1;overflow:auto}.item{display:flex;gap:11px;align-items:center;padding:10px 12px;border-bottom:1px solid #f0f2f5;cursor:pointer}.item:active,.item.selected{background:#f0f2f5}.info{flex:1;min-width:0}.topline{display:flex;justify-content:space-between;gap:7px}.name{font-size:15px;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.small{font-size:10px;color:#667781}.preview{font-size:12px;color:#667781;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.badge{background:#25d366;color:#fff;border-radius:20px;padding:2px 6px;font-size:9px;font-weight:800}
.main{flex:1;min-width:0;display:flex;flex-direction:column;background:#efeae2}.chathead{height:64px;background:#075e54;color:#fff;display:flex;align-items:center;padding:8px;gap:8px}.back{display:none}.chatinfo{flex:1;min-width:0}.chatname{font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.chatstatus{font-size:11px;color:#d7eee9}.messages{flex:1;overflow:auto;padding:10px 7px 12px;background-color:#efeae2;background-image:radial-gradient(circle at 20% 20%,#6655440a 1px,transparent 1px),radial-gradient(circle at 70% 70%,#66554408 1px,transparent 1px);background-size:44px 44px,61px 61px}.date{width:max-content;margin:2px auto 10px;padding:5px 10px;border-radius:8px;background:#fff;color:#667781;font-size:10px;box-shadow:0 1px 1px #ddd}.row{display:flex;margin:2px 0}.row.me{justify-content:flex-end}.bubble{max-width:min(78%,470px);background:#fff;padding:6px 8px;border-radius:7px;box-shadow:0 1px 1px #00000018;word-break:break-word}.row.me .bubble{background:#d9fdd3;border-top-right-radius:2px}.row.other .bubble{border-top-left-radius:2px}.sender{font-size:10px;color:#075e54;font-weight:700;margin-bottom:2px}.body{font-size:14px;line-height:1.35;white-space:pre-wrap}.meta{float:right;display:flex;align-items:center;gap:3px;margin:4px 0 0 9px}.time{font-size:9px;color:#667781}.ticks{font-size:13px;color:#53bdeb;letter-spacing:-4px;padding-right:4px}.reply{border-left:4px solid #25d366;background:#00000009;padding:4px 6px;border-radius:4px;margin-bottom:4px;font-size:10px}.reply b{color:#128c7e;display:block}.photo{max-width:100%;max-height:360px;border-radius:6px;display:block}.audio{width:210px;height:36px;max-width:100%}.sticker{font-size:42px}.actions{clear:both;text-align:right}.act{border:0;background:transparent;color:#128c7e;font-size:9px;cursor:pointer}.danger{color:#d32f2f}
.composearea{background:#f0f2f5;padding:5px 7px calc(5px + env(safe-area-inset-bottom))}.replybar{display:none;background:#fff;border-left:4px solid #25d366;border-radius:6px;padding:6px;margin-bottom:5px;align-items:center}.replycontent{flex:1;min-width:0}.replyname{font-size:11px;color:#128c7e;font-weight:700}.replytext{font-size:10px;color:#667781;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.compose{display:flex;gap:5px;align-items:flex-end}.box{flex:1;background:#fff;border-radius:22px;display:flex;align-items:center;padding:2px 4px}.box button{width:36px;height:38px;border:0;background:transparent;font-size:20px;color:#54656f}.box textarea{flex:1;min-width:0;border:0;outline:0;resize:none;max-height:100px;padding:9px 2px;font-size:15px}.circle{width:44px;height:44px;border:0;border-radius:50%;background:#25d366;color:#fff;font-size:19px}.emoji{display:none;background:#fff;padding:7px;border-radius:10px;margin-bottom:5px}.emoji-grid{display:grid;grid-template-columns:repeat(8,1fr);max-height:150px;overflow:auto}.emoji-grid button{border:0;background:transparent;font-size:22px;padding:5px}
.status{padding:10px}.statusitem{background:#fff;border-radius:8px;padding:11px;margin-bottom:7px;box-shadow:0 1px 2px #0001;display:flex;gap:10px;align-items:center}.ring{width:50px;height:50px;border-radius:50%;border:2px solid #25d366;padding:3px}.ringin{width:100%;height:100%;border-radius:50%;background:#075e54;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800}.statusview{display:none;position:fixed;inset:0;background:#111;z-index:50;color:#fff}.sthead{height:60px;background:#0008;display:flex;align-items:center;padding:8px;gap:9px}.stbody{height:calc(100% - 60px);display:flex;align-items:center;justify-content:center;padding:20px;text-align:center}.sttext{font-size:28px;max-width:700px;word-break:break-word}.stimg{max-width:100%;max-height:85%;object-fit:contain}
.modal{display:none;position:fixed;inset:0;background:#000b;z-index:100;align-items:center;justify-content:center;padding:20px}.card{background:#fff;width:100%;max-width:360px;border-radius:15px;padding:20px}.card input{width:100%;padding:11px;border:1px solid #ddd;border-radius:8px;margin:5px 0;outline:0}.btn{width:100%;border:0;border-radius:22px;padding:11px;margin-top:8px;font-weight:800}.green{background:#075e54;color:#fff}.gray{background:#eee}
@media(max-width:700px){#app{width:100%;box-shadow:none}.side{width:100%;min-width:0}.main{display:none}.side.hide{display:none}.main.show{display:flex}.back{display:block}}
</style></head><body><div id="app">
<aside class="side" id="side"><div class="head"><div class="avatar">🇬🇭</div><div class="title">GH NOT</div><button class="ico" onclick="newChat()">＋</button><button class="ico" onclick="profile()">⋮</button></div><div class="tabs"><button class="tab active" id="ct" onclick="tab('chats')">CHATS</button><button class="tab" id="st" onclick="tab('status')">STATUS</button></div><div class="search"><input id="search" placeholder="🔎 Search users or chats" oninput="renderUsers()"></div><div class="list" id="list"></div></aside>
<main class="main" id="main"><div class="chathead"><button class="ico back" onclick="closeChat()">‹</button><div class="avatar" id="ca">👤</div><div class="chatinfo"><div class="chatname" id="cn">Select a chat</div><div class="chatstatus" id="cs">Choose a user to message</div></div><button class="ico" onclick="menu()">⋮</button></div><div class="messages" id="msgs"><div class="date">TODAY</div></div><div class="composearea"><div class="replybar" id="rb"><div class="replycontent"><div class="replyname" id="rn"></div><div class="replytext" id="rt"></div></div><button class="ico" style="color:#54656f" onclick="cancelReply()">✕</button></div><div class="emoji" id="ep"><div class="emoji-grid" id="eg"></div></div><div class="compose"><div class="box"><button onclick="emojiPanel()">😊</button><button onclick="pickImage()">📎</button><textarea id="input" rows="1" placeholder="Message"></textarea><button onclick="pickImage()">📷</button></div><button class="circle" id="mic" onclick="mic()">🎤</button><button class="circle" onclick="send()">➤</button></div></div></main></div>
<input id="image" type="file" accept="image/*" style="display:none" onchange="sendImage(this)"><input id="statusImage" type="file" accept="image/*" style="display:none" onchange="postStatusImage(this)">
<div class="modal" id="profileModal" onclick="closeModal('profileModal')"><div class="card" onclick="event.stopPropagation()"><h3>My Profile</h3><input id="pname" placeholder="Your name"><input id="pabout" placeholder="About"><button class="btn green" onclick="saveProfile()">SAVE</button><button class="btn gray" onclick="closeModal('profileModal')">CLOSE</button></div></div>
<div class="modal" id="newModal" onclick="closeModal('newModal')"><div class="card" onclick="event.stopPropagation()"><h3>New Chat</h3><input id="newname" placeholder="Enter user's name"><button class="btn green" onclick="createUser()">CREATE USER</button><button class="btn gray" onclick="closeModal('newModal')">CANCEL</button></div></div>
<div class="modal" id="statusModal" onclick="closeModal('statusModal')"><div class="card" onclick="event.stopPropagation()"><h3>Post Status</h3><input id="statusText" placeholder="Type a status..."><button class="btn green" onclick="postStatus()">POST STATUS</button><button class="btn gray" onclick="$('statusImage').click()">POST PHOTO</button><button class="btn gray" onclick="closeModal('statusModal')">CANCEL</button></div></div>
<div class="statusview" id="sv"><div class="sthead"><div class="avatar" id="sva">🇬🇭</div><div><b id="svu"></b><div id="svt" style="font-size:10px;color:#ddd"></div></div><button class="ico" style="margin-left:auto" onclick="closeStatus()">✕</button></div><div class="stbody" id="svb"></div></div>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script><script>
const $=id=>document.getElementById(id);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const idEsc=s=>String(s).replace(/[^a-zA-Z0-9_-]/g,'');
let meId=localStorage.getItem('gh_user_id')||('u_'+Date.now()+'_'+Math.random().toString(36).slice(2,7));localStorage.setItem('gh_user_id',meId);let meName=localStorage.getItem('gh_name')||'';let users=[],statuses=[],selected=null,reply=null,rec=null,chunks=[],recording=false;
const emojis='😀 😃 😄 😁 😆 😅 😂 🤣 😊 🙂 😉 😍 🥰 😘 😎 🤩 🥳 😭 😢 😤 😡 😱 ❤️ 🧡 💛 💚 💙 💜 🖤 🤍 👍 👎 👏 🙏 🔥 💯 💀 🇬🇭'.split(' ');
$('eg').innerHTML=emojis.map(e=>`<button onclick="insertEmoji(${JSON.stringify(e)})">${e}</button>`).join('');
const socket=io({transports:['websocket','polling'],reconnection:true,reconnectionDelay:300});
socket.on('connect',()=>socket.emit('register',{id:meId,name:meName||'User'}));
socket.on('users',d=>{users=d.users||[];renderUsers()});socket.on('registered',d=>{meName=d.user.name;localStorage.setItem('gh_name',meName);users=d.users||users;renderUsers()});
socket.on('chat_history',d=>{if(selected&&d.with_user===selected.id)renderMessages(d.messages||[])});
socket.on('new_message',m=>{if(selected&&((m.from===meId&&m.to===selected.id)||(m.from===selected.id&&m.to===meId))){append(m);scrollBottom()}renderUsers()});
socket.on('message_deleted',d=>{let e=document.getElementById('m_'+idEsc(d.id));if(e)e.remove()});socket.on('status_list',d=>{statuses=d.statuses||[];renderStatusList()});socket.on('new_status',s=>{statuses.push(s);renderStatusList()});
function tab(t){$('ct').classList.toggle('active',t==='chats');$('st').classList.toggle('active',t==='status');t==='status'?renderStatusList():renderUsers()}
function renderUsers(){if($('st').classList.contains('active'))return;let q=($('search').value||'').toLowerCase();let arr=users.filter(u=>u.id!==meId&&(!q||u.name.toLowerCase().includes(q)));$('list').innerHTML=arr.length?arr.map(u=>{let on=(Date.now()/1000-u.last_seen)<45;return `<div class="item ${selected&&selected.id===u.id?'selected':''}" onclick="openChat('${idEsc(u.id)}')"><div class="avatar">${initial(u.name)}</div><div class="info"><div class="topline"><div class="name">${esc(u.name)}</div><span class="small">${on?'online':''}</span></div><div class="preview">${esc(u.about||'Hey there!')}</div></div></div>`}).join(''):`<div style="padding:35px;text-align:center;color:#667781;font-size:13px">No other users yet.<br><br>Tap <b>＋</b> to create a user.</div>`}
function renderStatusList(){let now=Date.now()/1000;let arr=statuses.filter(s=>s.expires>now);let groups={};arr.forEach(s=>(groups[s.user_id]??=[]).push(s));let h=`<div class="statusitem" onclick="openStatusComposer()"><div class="ring"><div class="rinin">＋</div></div><div><b>My status</b><div class="small">Tap to add status</div></div></div>`;Object.values(groups).forEach(g=>{let s=g[g.length-1];h+=`<div class="statusitem" onclick="viewStatus('${idEsc(s.user_id)}')"><div class="ring"><div class="rinin">${initial(s.name)}</div></div><div><b>${esc(s.name)}</b><div class="small">${g.length} status${g.length>1?'es':''}</div></div></div>`});$('list').innerHTML=h+(arr.length?'':'<div style="padding:20px;text-align:center;color:#667781;font-size:12px">No status updates yet.</div>')}
function openChat(id){selected=users.find(u=>u.id===id);if(!selected)return;$('cn').textContent=selected.name;$('cs').textContent=((Date.now()/1000-selected.last_seen)<45)?'online':'offline';$('ca').textContent=initial(selected.name);$('side').classList.add('hide');$('main').classList.add('show');socket.emit('open_chat',{with_user:id});}
function closeChat(){$('side').classList.remove('hide');$('main').classList.remove('show');selected=null}
function renderMessages(ms){$('msgs').innerHTML='<div class="date">TODAY</div>';let f=document.createDocumentFragment();ms.forEach(m=>{let w=document.createElement('div');w.innerHTML=messageHtml(m);f.appendChild(w.firstElementChild)});$('msgs').appendChild(f);scrollBottom()}
function append(m){if(document.getElementById('m_'+idEsc(m.id)))return;$('msgs').insertAdjacentHTML('beforeend',messageHtml(m))}
function messageHtml(m){let mine=m.from===meId;let body=m.type==='image'?`<img class="photo" src="${esc(m.text)}">`:m.type==='audio'?`<audio class="audio" controls src="${esc(m.text)}"></audio>`:m.type==='sticker'?`<div class="sticker">${esc(m.text)}</div>`:`<div class="body">${esc(m.text)}</div>`;let rp=m.replyTo?`<div class="reply"><b>${esc(m.replyTo.name)}</b>${esc(m.replyTo.preview||'')}</div>`:'';return `<div class="row ${mine?'me':'other'}" id="m_${idEsc(m.id)}"><div class="bubble">${!mine&&m.sender_name?`<div class="sender">${esc(m.sender_name)}</div>`:''}${rp}${body}<div class="meta"><span class="time">${esc(m.time||'')}</span>${mine?'<span class="ticks">✓✓</span>':''}</div><div class="actions"><button class="act" onclick="replyTo(${JSON.stringify(m.id)},${JSON.stringify(m.sender_name||meName)},${JSON.stringify(preview(m))})">↩ Reply</button>${mine?`<button class="act danger" onclick="deleteMessage(${JSON.stringify(m.id)})"> Delete</button>`:''}</div></div></div>`}
function preview(m){if(m.type==='image')return'📷 Photo';if(m.type==='audio')return'🎤 Voice message';if(m.type==='sticker')return m.text;return String(m.text||'').slice(0,70)}
function payload(type,text){let p={id:'m_'+Date.now()+'_'+Math.random().toString(36).slice(2,7),from:meId,to:selected.id,text,type,time:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}),sender_name:meName||'User'};if(reply)p.replyTo={name:reply.name,preview:reply.preview};return p}
function send(){if(!selected)return alert('Select a user first');let v=$('input').value.trim();if(!v)return;socket.emit('send_message',payload('text',v));$('input').value='';autoSize();cancelReply()}
function sendSticker(e){if(selected)socket.emit('send_message',payload('sticker',e))}
function pickImage(){if(selected)$('image').click();else alert('Select a user first')}
function sendImage(i){let f=i.files[0];if(!f||!selected)return;let r=new FileReader();r.onload=e=>{socket.emit('send_message',payload('image',e.target.result));i.value='';cancelReply()};r.readAsDataURL(f)}
async function mic(){if(!selected)return alert('Select a user first');if(!recording){try{let stream=await navigator.mediaDevices.getUserMedia({audio:true});let mt=MediaRecorder.isTypeSupported('audio/webm;codecs=opus')?'audio/webm;codecs=opus':MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':'';rec=mt?new MediaRecorder(stream,{mimeType:mt}):new MediaRecorder(stream);chunks=[];rec.ondataavailable=e=>e.data.size&&chunks.push(e.data);rec.onstop=()=>{let b=new Blob(chunks,{type:mt||'audio/webm'});if(b.size>900000)return alert('Voice message is too large');let r=new FileReader();r.onload=e=>socket.emit('send_message',payload('audio',e.target.result));r.readAsDataURL(b);stream.getTracks().forEach(t=>t.stop())};rec.start();recording=true;$('mic').textContent='■';$('mic').style.background='#d32f2f';setTimeout(()=>{if(recording)mic()},30000)}catch(e){alert('Microphone permission is required')}}else{try{rec.stop()}catch(e){}recording=false;$('mic').textContent='🎤';$('mic').style.background='#25d366'}}
function deleteMessage(id){socket.emit('delete_message',{id,with_user:selected.id})}
function replyTo(id,name,previewText){reply={id,name,preview:previewText};$('rn').textContent='Replying to '+name;$('rt').textContent=previewText;$('rb').style.display='flex';$('input').focus()}
function cancelReply(){reply=null;$('rb').style.display='none'}
function emojiPanel(){$('ep').style.display=$('ep').style.display==='block'?'none':'block'}function insertEmoji(e){$('input').value+=e;$('input').focus();autoSize()}function autoSize(){$('input').style.height='auto';$('input').style.height=Math.min($('input').scrollHeight,100)+'px'}$('input').addEventListener('input',autoSize);$('input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}})
function newChat(){$('newModal').style.display='flex';$('newname').focus()}function createUser(){let n=$('newname').value.trim();if(!n)return;socket.emit('create_user',{name:n});closeModal('newModal');$('newname').value=''}
function profile(){$('pname').value=meName;$('pabout').value='Hey there! I am using GH NOT.';$('profileModal').style.display='flex'}function saveProfile(){let n=$('pname').value.trim();if(!n)return alert('Enter your name');meName=n;localStorage.setItem('gh_name',n);socket.emit('update_profile',{name:n,about:$('pabout').value.trim()});closeModal('profileModal');renderUsers()}function closeModal(id){$(id).style.display='none'}
function openStatusComposer(){$('statusModal').style.display='flex'}function postStatus(){let t=$('statusText').value.trim();if(!t)return;socket.emit('post_status',{type:'text',text:t});$('statusText').value='';closeModal('statusModal')}function postStatusImage(i){let f=i.files[0];if(!f)return;let r=new FileReader();r.onload=e=>{socket.emit('post_status',{type:'image',text:e.target.result});i.value='';closeModal('statusModal')};r.readAsDataURL(f)}
function viewStatus(uid){let arr=statuses.filter(s=>s.user_id===uid&&s.expires>Date.now()/1000);if(!arr.length)return;let i=0;function show(){let s=arr[i];$('sva').textContent=initial(s.name);$('svu').textContent=s.name;$('svt').textContent=new Date(s.time*1000).toLocaleString();$('svb').innerHTML=s.type==='image'?`<img class="stimg" src="${esc(s.text)}">`:`<div class="sttext">${esc(s.text)}</div>`;$('sv').style.display='block'}show();$('sv').onclick=e=>{if(e.target.id==='sv'||e.target.id==='svb'){i=(i+1)%arr.length;show()}}}function closeStatus(){$('sv').style.display='none'}
function menu(){if(!selected)return;alert('Chat options: '+selected.name)}function focusSearch(){$('search').focus()}function initial(n){let p=(n||'U').trim().split(/\s+/);return (p[0][0]||'U').toUpperCase()+(p[1]?.[0]||'').toUpperCase()}function scrollBottom(){$('msgs').scrollTop=$('msgs').scrollHeight}
function timeAgo(t){let x=Math.max(1,Math.floor(Date.now()/1000-t));return x<60?x+'s':x<3600?Math.floor(x/60)+'m':Math.floor(x/3600)+'h'}

socket.on('connect',()=>socket.emit('get_statuses'));
if(!meName)setTimeout(profile,300);
</script></body></html>'''

@app.get('/',response_class=HTMLResponse)
async def home(): return HTML

@sio.on('register')
async def register(sid,data):
    uid=str(data.get('id','')).strip()[:100]
    if not uid:return
    u=user(uid,data.get('name'))
    await sio.save_session(sid,{'user_id':uid})
    save_db()
    await sio.emit('registered',{'user':u,'users':public_users()},to=sid)
    await sio.emit('users',{'users':public_users()})
    clean_statuses();await sio.emit('status_list',{'statuses':db['statuses']},to=sid)

@sio.on('create_user')
async def create_user(sid,data):
    try: me=(await sio.get_session(sid)).get('user_id')
    except Exception: me=None
    if not me:return
    name=str(data.get('name','')).strip()[:40]
    if not name:return
    uid='u_'+uuid.uuid4().hex[:12]
    user(uid,name);save_db();await sio.emit('users',{'users':public_users()})

@sio.on('update_profile')
async def update_profile(sid,data):
    try: uid=(await sio.get_session(sid)).get('user_id')
    except Exception: uid=None
    if not uid:return
    u=user(uid,data.get('name'));u['about']=str(data.get('about','')).strip()[:80];save_db();await sio.emit('users',{'users':public_users()})

@sio.on('open_chat')
async def open_chat(sid,data):
    try: me=(await sio.get_session(sid)).get('user_id')
    except Exception: me=None
    other=str(data.get('with_user','')).strip()
    if not me or not other or other not in db['users']:return
    u=user(me);save_db();await sio.emit('chat_history',{'with_user':other,'messages':db['chats'].get(key(me,other),[])},to=sid)

@sio.on('send_message')
async def send_message(sid,data):
    try: me=(await sio.get_session(sid)).get('user_id')
    except Exception: me=None
    if not me:return
    to=str(data.get('to','')).strip()
    if not to or to==me or to not in db['users']:return
    m={'id':str(data.get('id') or ('m_'+uuid.uuid4().hex)),'from':me,'to':to,'text':data.get('text',''),'type':data.get('type','text'),'time':data.get('time',''),'sender_name':db['users'][me]['name']}
    if data.get('replyTo'):m['replyTo']=data['replyTo']
    k=key(me,to);db['chats'].setdefault(k,[]).append(m);db['chats'][k]=db['chats'][k][-500:]
    user(me);save_db()
    # Only the two participants receive the private message.
    await sio.emit('new_message',m,to=sid)
    for s,session in list(sio.manager.get_participants('/', '')) if False else []: pass
    for other_sid, session in list(sio.eio.sockets.items()):
        try:
            ss=await sio.get_session(other_sid)
            if ss.get('user_id')==to and other_sid!=sid: await sio.emit('new_message',m,to=other_sid)
        except Exception: pass

@sio.on('delete_message')
async def delete_message(sid,data):
    try: me=(await sio.get_session(sid)).get('user_id')
    except Exception: me=None
    other=str(data.get('with_user','')).strip();mid=str(data.get('id',''))
    if not me or not other:return
    k=key(me,other);arr=db['chats'].get(k,[]);db['chats'][k]=[m for m in arr if not (m.get('id')==mid and m.get('from')==me)];save_db()
    for other_sid in list(sio.eio.sockets.keys()):
        try:
            ss=await sio.get_session(other_sid)
            if ss.get('user_id') in (me,other):await sio.emit('message_deleted',{'id':mid},to=other_sid)
        except Exception:pass

@sio.on('post_status')
async def post_status(sid,data):
    try: uid=(await sio.get_session(sid)).get('user_id')
    except Exception: uid=None
    if not uid:return
    clean_statuses();u=db['users'].get(uid)
    if not u:return
    s={'id':'s_'+uuid.uuid4().hex,'user_id':uid,'name':u['name'],'type':data.get('type','text'),'text':data.get('text',''),'time':time.time(),'expires':time.time()+86400}
    db['statuses'].append(s);save_db();await sio.emit('new_status',s)

@sio.on('get_statuses')
async def get_statuses(sid):
    clean_statuses();await sio.emit('status_list',{'statuses':db['statuses']},to=sid)

@sio.event
async def disconnect(sid):
    try: uid=(await sio.get_session(sid)).get('user_id')
    except Exception: uid=None
    if uid in db['users']:
        db['users'][uid]['last_seen']=time.time();save_db();await sio.emit('users',{'users':public_users()})
