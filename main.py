from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
import socketio
from collections import defaultdict
import json, os

app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

POSSIBLE_PATHS = ["/data/gh_rooms.json", "gh_rooms.json", "/tmp/gh_rooms.json"]
DB_FILE = None
rooms_data = defaultdict(list)

for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
            for k, v in d.items():
                rooms_data[k] = v
            DB_FILE = p
            break
        except Exception:
            pass

if not DB_FILE:
    DB_FILE = "/data/gh_rooms.json" if os.path.exists("/data") else "gh_rooms.json"

def save_db():
    try:
        payload = dict(rooms_data)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        try:
            with open("gh_rooms.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception:
            pass
    except Exception:
        pass


@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "GH NOT",
        "short_name": "GH NOT",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#efeae2",
        "theme_color": "#075e54",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/5962/5962463.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/5962/5962463.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })


@app.get("/sw.js")
async def sw():
    js = """
self.addEventListener("install", e => self.skipWaiting());
self.addEventListener("activate", e => self.clients.claim());
self.addEventListener("fetch", e => {
    e.respondWith(fetch(e.request));
});
"""
    return Response(
        content=js,
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#075e54">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<title>GH NOT</title>

<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden}
body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    background:#efeae2;
    color:#111b21;
    height:100dvh;
}

button,input{font:inherit}

:root{
    --green:#075e54;
    --green2:#128c7e;
    --light-green:#25d366;
    --out:#d9fdd3;
    --in:#fff;
    --bg:#efeae2;
    --text:#111b21;
    --muted:#667781;
    --line:#e9edef;
}

/* APP */
#app{
    height:100dvh;
    width:100%;
    display:flex;
    flex-direction:column;
    background:var(--bg);
}

/* TOP BAR */
.header{
    height:64px;
    min-height:64px;
    background:var(--green);
    color:#fff;
    display:flex;
    align-items:center;
    padding:8px 10px;
    gap:10px;
    box-shadow:0 1px 3px rgba(0,0,0,.25);
    z-index:20;
}

.avatar{
    width:44px;
    height:44px;
    min-width:44px;
    border-radius:50%;
    background:linear-gradient(145deg,#25d366,#128c7e);
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-size:20px;
    font-weight:800;
    overflow:hidden;
}

.avatar img{
    width:100%;
    height:100%;
    object-fit:cover;
}

.head-info{
    flex:1;
    min-width:0;
}

.head-name{
    font-size:17px;
    font-weight:700;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.head-status{
    margin-top:2px;
    font-size:12px;
    color:rgba(255,255,255,.8);
    white-space:nowrap;
}

.header-actions{
    display:flex;
    align-items:center;
    gap:2px;
}

.icon-btn{
    width:40px;
    height:40px;
    border:0;
    background:transparent;
    color:#fff;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    font-size:20px;
    -webkit-tap-highlight-color:transparent;
}

.icon-btn:active{
    background:rgba(255,255,255,.14);
}

/* CHAT */
#chat{
    position:relative;
    flex:1;
    min-height:0;
    overflow-y:auto;
    overflow-x:hidden;
    padding:10px 7px 12px;
    scroll-behavior:auto;
    -webkit-overflow-scrolling:touch;
    background-color:var(--bg);
}

/* subtle WhatsApp-like wallpaper */
#chat:before{
    content:"";
    position:fixed;
    inset:64px 0 74px;
    pointer-events:none;
    opacity:.055;
    background-image:
        radial-gradient(circle at 15% 20%, #6b5e52 1px, transparent 1.5px),
        radial-gradient(circle at 75% 70%, #6b5e52 1px, transparent 1.5px);
    background-size:44px 44px,58px 58px;
}

/* DATE CHIP */
.date-chip{
    width:max-content;
    max-width:90%;
    margin:5px auto 10px;
    background:#fff;
    color:#54656f;
    padding:5px 11px;
    border-radius:8px;
    font-size:11px;
    box-shadow:0 1px 1px rgba(0,0,0,.12);
    position:relative;
    z-index:1;
}

/* MESSAGE */
.msg-row{
    width:100%;
    display:flex;
    margin:2px 0;
    position:relative;
    z-index:2;
}

.msg-row.incoming{justify-content:flex-start}
.msg-row.outgoing{justify-content:flex-end}

.msg{
    position:relative;
    max-width:min(82%,440px);
    min-width:54px;
    padding:6px 8px 5px;
    border-radius:7px;
    box-shadow:0 1px 1px rgba(0,0,0,.12);
    word-wrap:break-word;
    overflow-wrap:anywhere;
}

.incoming .msg{
    background:var(--in);
    border-top-left-radius:2px;
}

.outgoing .msg{
    background:var(--out);
    border-top-right-radius:2px;
}

.msg-tail{
    position:absolute;
    top:0;
    width:0;
    height:0;
    border-style:solid;
}

.incoming .msg-tail{
    left:-6px;
    border-width:0 7px 7px 0;
    border-color:transparent #fff transparent transparent;
}

.outgoing .msg-tail{
    right:-6px;
    border-width:0 0 7px 7px;
    border-color:transparent transparent transparent var(--out);
}

.sender{
    color:#075e54;
    font-size:12px;
    font-weight:700;
    margin-bottom:2px;
}

.message-text{
    font-size:14.5px;
    line-height:1.3;
    white-space:pre-wrap;
    padding-right:3px;
}

.meta{
    float:right;
    display:flex;
    align-items:center;
    gap:3px;
    margin-left:8px;
    margin-top:5px;
    padding-left:3px;
    height:14px;
}

.msg-time{
    font-size:10px;
    color:#667781;
    white-space:nowrap;
}

.ticks{
    font-size:15px;
    line-height:10px;
    letter-spacing:-5px;
    padding-right:4px;
    color:#667781;
}

.ticks.read{
    color:#53bdeb;
}

.msg-image{
    display:block;
    width:auto;
    max-width:100%;
    max-height:360px;
    border-radius:6px;
    object-fit:cover;
    margin-bottom:3px;
}

.audio-wrap{
    width:220px;
    max-width:100%;
    display:flex;
    align-items:center;
    gap:7px;
    padding:2px 0;
}

.audio-play{
    width:36px;
    height:36px;
    min-width:36px;
    border:0;
    border-radius:50%;
    background:#25d366;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
}

.audio-el{
    width:170px;
    height:34px;
}

.reply{
    background:rgba(0,0,0,.06);
    border-left:4px solid #25d366;
    border-radius:5px;
    padding:4px 7px;
    margin-bottom:4px;
    font-size:11px;
    color:#667781;
    overflow:hidden;
}

.reply b{
    color:#128c7e;
    display:block;
    margin-bottom:1px;
}

.reply-text{
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.sticker{
    font-size:42px;
    line-height:1.05;
    padding:2px;
}

/* ACTIONS */
.message-actions{
    display:flex;
    justify-content:flex-end;
    gap:3px;
    margin-top:2px;
}

.action{
    border:0;
    background:transparent;
    color:#667781;
    font-size:10px;
    padding:2px 4px;
    cursor:pointer;
}

.action.reply-action{
    color:#128c7e;
    font-weight:700;
}

.action.delete-action{
    color:#d32f2f;
}

/* COMPOSER */
.composer-area{
    flex-shrink:0;
    background:#f0f2f5;
    border-top:1px solid rgba(0,0,0,.08);
    padding:5px 7px calc(5px + env(safe-area-inset-bottom));
    z-index:20;
}

.reply-bar{
    display:none;
    align-items:center;
    gap:8px;
    background:#fff;
    border-left:4px solid #25d366;
    border-radius:7px;
    padding:6px 8px;
    margin-bottom:5px;
    box-shadow:0 1px 2px rgba(0,0,0,.08);
}

.reply-bar-content{
    flex:1;
    min-width:0;
}

.reply-bar-name{
    color:#128c7e;
    font-weight:700;
    font-size:12px;
}

.reply-bar-text{
    color:#667781;
    font-size:11px;
    margin-top:1px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.reply-close{
    width:30px;
    height:30px;
    border:0;
    background:transparent;
    color:#54656f;
    font-size:18px;
    cursor:pointer;
}

.composer{
    display:flex;
    align-items:flex-end;
    gap:6px;
}

.composer-main{
    flex:1;
    min-width:0;
    min-height:44px;
    background:#fff;
    border-radius:22px;
    display:flex;
    align-items:center;
    padding:3px 7px;
    box-shadow:0 1px 1px rgba(0,0,0,.06);
}

.composer-icon{
    width:36px;
    height:38px;
    border:0;
    background:transparent;
    color:#54656f;
    font-size:21px;
    cursor:pointer;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-shrink:0;
}

#msgInput{
    flex:1;
    min-width:0;
    max-height:110px;
    resize:none;
    border:0;
    outline:none;
    font-size:15px;
    line-height:20px;
    padding:9px 3px;
    background:transparent;
    color:#111b21;
}

#nameInput{
    display:none;
}

.send-btn{
    width:44px;
    height:44px;
    min-width:44px;
    border:0;
    border-radius:50%;
    background:#25d366;
    color:#fff;
    font-size:20px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    box-shadow:0 1px 2px rgba(0,0,0,.2);
}

.send-btn:active,.mic-btn:active{
    transform:scale(.95);
}

.mic-btn{
    width:44px;
    height:44px;
    min-width:44px;
    border:0;
    border-radius:50%;
    background:#25d366;
    color:#fff;
    font-size:20px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
}

/* EMOJI PANEL */
.emoji-panel{
    display:none;
    background:#fff;
    border-radius:12px;
    padding:8px;
    margin-bottom:5px;
    box-shadow:0 1px 4px rgba(0,0,0,.15);
}

.emoji-grid{
    display:grid;
    grid-template-columns:repeat(8,1fr);
    gap:4px;
    max-height:150px;
    overflow:auto;
}

.emoji{
    border:0;
    background:transparent;
    font-size:23px;
    padding:5px 0;
    cursor:pointer;
    border-radius:6px;
}

.emoji:active{background:#f0f2f5}

/* MENU */
.menu{
    display:none;
    position:absolute;
    right:8px;
    top:58px;
    width:190px;
    background:#fff;
    border-radius:8px;
    padding:5px 0;
    box-shadow:0 3px 12px rgba(0,0,0,.25);
    z-index:100;
}

.menu button{
    width:100%;
    border:0;
    background:#fff;
    padding:12px 15px;
    text-align:left;
    font-size:14px;
    color:#111b21;
    cursor:pointer;
}

.menu button:active{background:#f0f2f5}

/* INSTALL */
#installBanner{
    display:none;
    background:#25d366;
    color:#fff;
    padding:9px;
    text-align:center;
    font-size:12px;
    font-weight:700;
    cursor:pointer;
}

.install-help{
    display:none;
    position:fixed;
    inset:0;
    z-index:999;
    background:rgba(0,0,0,.7);
    align-items:center;
    justify-content:center;
    padding:20px;
}

.help-card{
    width:100%;
    max-width:350px;
    background:#fff;
    border-radius:14px;
    padding:20px;
}

.help-card h3{margin-bottom:12px}
.help-card p{margin:9px 0;color:#54656f;font-size:14px}

.help-card button{
    width:100%;
    border:0;
    background:#075e54;
    color:#fff;
    border-radius:20px;
    padding:11px;
    font-weight:700;
    margin-top:8px;
}

/* MODALS */
.modal{
    display:none;
    position:fixed;
    inset:0;
    z-index:200;
    background:rgba(0,0,0,.72);
    align-items:center;
    justify-content:center;
    padding:20px;
}

.card{
    width:100%;
    max-width:330px;
    background:#fff;
    border-radius:16px;
    padding:20px;
    text-align:center;
}

.momo-number{
    font-size:25px;
    font-weight:900;
    background:#ffecb3;
    padding:12px;
    border-radius:10px;
    margin:12px 0;
}

.card-btn{
    width:100%;
    border:0;
    border-radius:22px;
    padding:11px;
    margin-top:7px;
    font-weight:700;
    cursor:pointer;
}

.green-btn{background:#075e54;color:#fff}
.gray-btn{background:#eee;color:#111}
.yellow-btn{background:#ffdd00;color:#000}

/* EMPTY */
.empty{
    position:absolute;
    inset:0;
    display:flex;
    align-items:center;
    justify-content:center;
    pointer-events:none;
    color:#667781;
    font-size:13px;
    text-align:center;
    padding:30px;
}

.empty div{
    background:rgba(255,255,255,.75);
    padding:8px 12px;
    border-radius:8px;
}

/* RECORDING */
.recording{
    animation:pulse 1s infinite;
    background:#d32f2f!important;
}

@keyframes pulse{
    0%,100%{opacity:1}
    50%{opacity:.55}
}

/* DESKTOP */
@media(min-width:700px){
    body{
        background:#d9dbd5;
    }

    #app{
        max-width:1100px;
        margin:0 auto;
        box-shadow:0 0 12px rgba(0,0,0,.2);
    }

    .msg{
        max-width:65%;
    }
}
</style>
</head>

<body>
<div id="app">

<div id="installBanner" onclick="showInstallHelp()">📲 Tap here to install GH NOT</div>

<header class="header">
    <div class="avatar">🇬🇭</div>
    <div class="head-info">
        <div class="head-name" id="roomTitle">GH NOT</div>
        <div class="head-status" id="statusText">connecting...</div>
    </div>
    <div class="header-actions">
        <button class="icon-btn" title="Search" onclick="focusSearch()">⌕</button>
        <button class="icon-btn" title="Menu" onclick="toggleMenu()">⋮</button>
    </div>
</header>

<div class="menu" id="menu">
    <button onclick="openRoom()">Change chat room</button>
    <button onclick="shareLink();closeMenu()">Share chat</button>
    <button onclick="openMomo();closeMenu()">Support GH NOT</button>
    <button onclick="clearAll();closeMenu()">Clear chat</button>
</div>

<main id="chat">
    <div class="empty" id="emptyState"><div>🔒 Messages are stored in this GH NOT room</div></div>
</main>

<div class="composer-area">

    <div class="reply-bar" id="replyBar">
        <div class="reply-bar-content">
            <div class="reply-bar-name" id="replyName"></div>
            <div class="reply-bar-text" id="replyText"></div>
        </div>
        <button class="reply-close" onclick="cancelReply()">✕</button>
    </div>

    <div class="emoji-panel" id="emojiPanel">
        <div class="emoji-grid" id="emojiGrid"></div>
    </div>

    <div class="composer">

        <div class="composer-main">
            <button class="composer-icon" onclick="toggleEmoji()">😊</button>
            <button class="composer-icon" onclick="document.getElementById('fileInput').click()">📎</button>
            <input id="nameInput" autocomplete="name">
            <textarea id="msgInput" rows="1" placeholder="Type a message"></textarea>
            <button class="composer-icon" onclick="document.getElementById('fileInput').click()">📷</button>
        </div>

        <button class="mic-btn" id="micBtn" onclick="toggleMic()">🎤</button>
        <button class="send-btn" onclick="sendMsg()">➤</button>

    </div>
</div>

<input type="file" id="fileInput" accept="image/*" style="display:none" onchange="sendFile(this)">

<div class="modal" id="momoModal" onclick="closeMomo()">
    <div class="card" onclick="event.stopPropagation()">
        <h3>Support GH NOT 🇬🇭</h3>
        <div class="momo-number">053 399 3024</div>
        <button class="card-btn yellow-btn" onclick="copyMomo()">COPY NUMBER</button>
        <button class="card-btn gray-btn" onclick="closeMomo()">CLOSE</button>
    </div>
</div>

<div class="install-help" id="installHelp" onclick="this.style.display='none'">
    <div class="help-card" onclick="event.stopPropagation()">
        <h3>📲 Install GH NOT</h3>
        <p><b>Android:</b> browser menu → Add to Home screen → Install.</p>
        <p><b>iPhone:</b> Share → Add to Home Screen.</p>
        <button onclick="hideInstallHelp()">Got it</button>
    </div>
</div>

<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>

<script>
const $ = id => document.getElementById(id);

let deferredPrompt = null;
let replyTo = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentRoom = new URLSearchParams(location.search).get("room")
    || localStorage.getItem("gh_room")
    || "open-thread";

let currentName = localStorage.getItem("gh_name") || "";

const emojis = [
    "😀","😃","😄","😁","😆","😅","😂","🤣",
    "😊","😇","🙂","🙃","😉","😌","😍","🥰",
    "😘","😗","😙","😚","😋","😛","😝","😜",
    "🤪","🤨","🧐","🤓","😎","🤩","🥳","😏",
    "😒","😞","😔","😟","😕","🙁","☹️","😣",
    "😖","😫","😩","🥺","😢","😭","😤","😠",
    "😡","🤬","🤯","😳","🥵","🥶","😱","😨",
    "❤️","🧡","💛","💚","💙","💜","🖤","🤍",
    "💯","🔥","🙏","👏","👍","👎","💀","🇬🇭"
];

function initEmoji(){
    $("emojiGrid").innerHTML = emojis.map(e =>
        `<button class="emoji" onclick="insertEmoji('${e}')">${e}</button>`
    ).join("");
}

function insertEmoji(e){
    const input = $("msgInput");
    input.value += e;
    input.focus();
}

function toggleEmoji(){
    const p = $("emojiPanel");
    p.style.display = p.style.display === "block" ? "none" : "block";
}

function toggleMenu(){
    const m = $("menu");
    m.style.display = m.style.display === "block" ? "none" : "block";
}

function closeMenu(){
    $("menu").style.display = "none";
}

document.addEventListener("click", e => {
    if (!e.target.closest(".header-actions") && !e.target.closest("#menu")) {
        closeMenu();
    }
});

function updateHeader(){
    $("roomTitle").textContent = currentRoom;
    $("statusText").textContent = navigator.onLine ? "online" : "offline";
}

function showInstallHelp(){
    $("installHelp").style.display = "flex";
}

function hideInstallHelp(){
    $("installHelp").style.display = "none";
}

window.addEventListener("beforeinstallprompt", e => {
    e.preventDefault();
    deferredPrompt = e;
    $("installBanner").style.display = "block";
});

$("installBanner").addEventListener("click", async () => {
    if(deferredPrompt){
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        $("installBanner").style.display = "none";
    }else{
        showInstallHelp();
    }
});

if("serviceWorker" in navigator){
    navigator.serviceWorker.register("/sw.js").catch(()=>{});
}

window.addEventListener("online", () => {
    $("statusText").textContent = "online";
});

window.addEventListener("offline", () => {
    $("statusText").textContent = "offline";
});

function saveName(){
    currentName = $("nameInput").value.trim();
    if(currentName) localStorage.setItem("gh_name", currentName);
}

function ensureName(){
    if(!currentName){
        currentName = prompt("Enter your name") || "";
        currentName = currentName.trim();
        if(!currentName) return false;
        localStorage.setItem("gh_name", currentName);
    }
    return true;
}

function openRoom(){
    const room = prompt("Enter chat room", currentRoom);
    if(room === null) return;
    const r = room.trim() || "open-thread";
    localStorage.setItem("gh_room", r);
    location.href = "?room=" + encodeURIComponent(r);
}

function shareLink(){
    const text = "GH NOT 🇬🇭\\n" + location.href;
    if(navigator.share){
        navigator.share({title:"GH NOT", text:text}).catch(()=>{});
    }else if(navigator.clipboard){
        navigator.clipboard.writeText(text).then(() => alert("Chat link copied!"));
    }
}

function openMomo(){
    $("momoModal").style.display = "flex";
}

function closeMomo(){
    $("momoModal").style.display = "none";
}

function copyMomo(){
    navigator.clipboard.writeText("0533993024")
        .then(() => alert("MoMo number copied"));
}

function focusSearch(){
    const q = prompt("Search messages");
    if(!q) return;
    const text = q.toLowerCase();
    const messages = document.querySelectorAll(".message-text");
    let found = false;
    messages.forEach(el => {
        if(el.textContent.toLowerCase().includes(text)){
            el.scrollIntoView({behavior:"smooth",block:"center"});
            el.style.background = "#fff3a8";
            setTimeout(() => el.style.background = "", 1400);
            found = true;
        }
    });
    if(!found) alert("Message not found");
}

/* SOCKET */
const socket = io({
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 300
});

socket.on("connect", () => {
    $("statusText").textContent = "online";
    socket.emit("join", currentRoom);
});

socket.on("disconnect", () => {
    $("statusText").textContent = "reconnecting...";
});

socket.on("history", messages => {
    const chat = $("chat");
    chat.innerHTML = '<div class="date-chip">TODAY</div>';
    if(!messages.length){
        chat.innerHTML += '<div class="empty" id="emptyState"><div>🔒 Start chatting in this room</div></div>';
    }else{
        messages.forEach(addMessage);
    }
    requestAnimationFrame(scrollBottom);
});

socket.on("new_message", m => {
    const empty = $("emptyState");
    if(empty) empty.remove();
    addMessage(m);
    requestAnimationFrame(scrollBottom);
});

socket.on("delete_msg", id => {
    const row = document.getElementById("msg-" + id);
    if(row) row.remove();
});

socket.on("clear_all", () => {
    $("chat").innerHTML = '<div class="date-chip">TODAY</div><div class="empty"><div>Chat cleared</div></div>';
});

function scrollBottom(){
    const chat = $("chat");
    chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(value){
    return String(value ?? "")
        .replace(/&/g,"&amp;")
        .replace(/</g,"&lt;")
        .replace(/>/g,"&gt;")
        .replace(/"/g,"&quot;")
        .replace(/'/g,"&#039;");
}

function cleanPreview(m){
    if(!m) return "";
    if(m.type === "audio" || String(m.text||"").startsWith("data:audio")) return "🎤 Voice message";
    if(m.type === "image" || String(m.text||"").startsWith("data:image")) return "📷 Photo";
    if(m.type === "sticker") return m.text || "";
    return String(m.text || "").slice(0,80);
}

function setReply(id,name,text,type){
    replyTo = {
        id:id,
        name:name,
        text:cleanPreview({text:text,type:type}),
        type:type
    };

    $("replyName").textContent = "Replying to " + name;
    $("replyText").textContent = replyTo.text;
    $("replyBar").style.display = "flex";
    $("msgInput").focus();
}

function cancelReply(){
    replyTo = null;
    $("replyBar").style.display = "none";
}

function addMessage(m){
    if(!m || !m.id) return;
    if(document.getElementById("msg-" + m.id)) return;

    const mine = m.name === currentName;
    const row = document.createElement("div");
    row.className = "msg-row " + (mine ? "outgoing" : "incoming");
    row.id = "msg-" + m.id;

    const bubble = document.createElement("div");
    bubble.className = "msg";

    const tail = document.createElement("span");
    tail.className = "msg-tail";

    let html = "";

    if(!mine){
        html += `<div class="sender">${escapeHtml(m.name || "Anon")}</div>`;
    }

    if(m.replyTo){
        html += `
            <div class="reply">
                <b>${escapeHtml(m.replyTo.name || "User")}</b>
                <div class="reply-text">${escapeHtml(cleanPreview(m.replyTo))}</div>
            </div>
        `;
    }

    if(m.type === "image"){
        html += `<img class="msg-image" src="${m.text}" loading="lazy">`;
    }else if(m.type === "audio"){
        html += `
            <div class="audio-wrap">
                <button class="audio-play" onclick="playAudio(this)">▶</button>
                <audio class="audio-el" preload="metadata" src="${m.text}"></audio>
            </div>
        `;
    }else if(m.type === "sticker"){
        html += `<div class="sticker">${escapeHtml(m.text)}</div>`;
    }else{
        html += `<span class="message-text">${escapeHtml(m.text)}</span>`;
    }

    const ticks = mine ? `<span class="ticks read">✓✓</span>` : "";

    html += `
        <span class="meta">
            <span class="msg-time">${escapeHtml(m.time || "")}</span>
            ${ticks}
        </span>
    `;

    html += `
        <div class="message-actions">
            <button class="action reply-action"
                onclick="setReply(
                    '${escapeHtml(m.id)}',
                    '${escapeHtml(m.name || "Anon").replace(/'/g,"&#39;")}',
                    '${escapeHtml(cleanPreview(m)).replace(/'/g,"&#39;")}',
                    '${escapeHtml(m.type || "text")}'
                )">↩ Reply</button>
    `;

    if(mine){
        html += `<button class="action delete-action" onclick="deleteMsg('${escapeHtml(m.id)}')">Delete</button>`;
    }

    html += `</div>`;

    bubble.innerHTML = html;
    bubble.appendChild(tail);
    row.appendChild(bubble);
    $("chat").appendChild(row);
}

function playAudio(button){
    const audio = button.parentElement.querySelector("audio");
    if(audio.paused){
        document.querySelectorAll(".audio-el").forEach(a => {
            if(a !== audio) a.pause();
        });
        audio.play().catch(()=>{});
        button.textContent = "❚❚";
        audio.onended = () => button.textContent = "▶";
    }else{
        audio.pause();
        button.textContent = "▶";
    }
}

function payload(type,text){
    const p = {
        id:"m" + Date.now() + Math.random().toString(36).slice(2,7),
        room:currentRoom,
        name:currentName || "Anon",
        text:text,
        type:type,
        time:new Date().toLocaleTimeString([],{
            hour:"2-digit",
            minute:"2-digit"
        })
    };

    if(replyTo){
        p.replyTo = {...replyTo};
    }

    return p;
}

function sendMsg(){
    if(!ensureName()) return;
    saveName();

    const input = $("msgInput");
    const text = input.value.trim();
    if(!text) return;

    socket.emit("send", payload("text", text));
    input.value = "";
    input.style.height = "auto";
    cancelReply();
    $("emojiPanel").style.display = "none";
}

function sendSticker(e){
    if(!ensureName()) return;
    saveName();
    socket.emit("send", payload("sticker", e));
    cancelReply();
}

function sendFile(input){
    if(!ensureName()){
        input.value = "";
        return;
    }

    saveName();

    const file = input.files && input.files[0];
    if(!file){
        input.value = "";
        return;
    }

    if(file.size > 8 * 1024 * 1024){
        alert("Please choose an image under 8 MB.");
        input.value = "";
        return;
    }

    const reader = new FileReader();

    reader.onload = e => {
        socket.emit("send", payload("image", e.target.result));
        cancelReply();
    };

    reader.readAsDataURL(file);
    input.value = "";
}

function deleteMsg(id){
    if(confirm("Delete this message?")){
        socket.emit("delete", {
            room:currentRoom,
            id:id
        });
    }
}

function clearAll(){
    if(confirm("Clear this entire chat for everyone?")){
        socket.emit("clear_all", {room:currentRoom});
    }
}

/* VOICE */
async function toggleMic(){
    if(!ensureName()) return;
    saveName();

    const btn = $("micBtn");

    if(!isRecording){
        try{
            const stream = await navigator.mediaDevices.getUserMedia({audio:true});

            let mime = "";
            if(MediaRecorder.isTypeSupported("audio/webm;codecs=opus")){
                mime = "audio/webm;codecs=opus";
            }else if(MediaRecorder.isTypeSupported("audio/webm")){
                mime = "audio/webm";
            }else if(MediaRecorder.isTypeSupported("audio/mp4")){
                mime = "audio/mp4";
            }else if(MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")){
                mime = "audio/ogg;codecs=opus";
            }

            mediaRecorder = mime
                ? new MediaRecorder(stream,{mimeType:mime})
                : new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.ondataavailable = e => {
                if(e.data && e.data.size) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                stream.getTracks().forEach(t => t.stop());

                if(!audioChunks.length) return;

                const blob = new Blob(audioChunks,{
                    type:mime || "audio/webm"
                });

                if(blob.size > 900000){
                    alert("Voice message is too large. Keep it short.");
                    return;
                }

                const reader = new FileReader();

                reader.onload = e => {
                    socket.emit("send", payload("audio",e.target.result));
                    cancelReply();
                };

                reader.readAsDataURL(blob);
            };

            mediaRecorder.start();
            isRecording = true;
            btn.classList.add("recording");
            btn.textContent = "■";

            setTimeout(() => {
                if(isRecording) toggleMic();
            },30000);

        }catch(err){
            alert("Microphone permission is required.");
        }

    }else{
        try{
            mediaRecorder.stop();
        }catch(e){}

        isRecording = false;
        btn.classList.remove("recording");
        btn.textContent = "🎤";
    }
}

/* TEXT INPUT */
$("msgInput").addEventListener("input", function(){
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight,110) + "px";
});

$("msgInput").addEventListener("keydown", e => {
    if(e.key === "Enter" && !e.shiftKey){
        e.preventDefault();
        sendMsg();
    }
});

$("msgInput").addEventListener("focus", () => {
    setTimeout(scrollBottom,80);
});

$("nameInput").value = currentName;
updateHeader();
initEmoji();

if(!currentName){
    setTimeout(() => {
        const n = prompt("Welcome to GH NOT 🇬🇭\\nEnter your name:");
        if(n && n.trim()){
            currentName = n.trim();
            localStorage.setItem("gh_name",currentName);
        }
    },300);
}

if(!window.matchMedia("(display-mode: standalone)").matches){
    setTimeout(() => {
        if(!deferredPrompt) $("installBanner").style.display = "block";
    },3500);
}
</script>
</div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@sio.on("join")
async def on_join(sid, room):
    room = room or "open-thread"
    await sio.enter_room(sid, room)
    await sio.emit("history", rooms_data[room], to=sid)


@sio.on("send")
async def on_send(sid, data):
    room = data.get("room", "open-thread")
    data["room"] = room

    rooms_data[room].append(data)

    if len(rooms_data[room]) > 400:
        rooms_data[room] = rooms_data[room][-400:]

    save_db()
    await sio.emit("new_message", data, room=room)


@sio.on("delete")
async def on_delete(sid, data):
    room = data.get("room", "open-thread")
    mid = data.get("id")

    rooms_data[room] = [
        m for m in rooms_data[room]
        if m.get("id") != mid
    ]

    save_db()
    await sio.emit("delete_msg", mid, room=room)


@sio.on("clear_all")
async def on_clear(sid, data):
    room = data.get("room", "open-thread")
    rooms_data[room] = []

    save_db()
    await sio.emit("clear_all", {}, room=room)
