from flask import Flask, render_template_string, session, redirect, url_for, request
import os
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "demo_secret_key")

# ----------------------
# デモメールデータ（初期）
# ----------------------
DEMO_EMAILS = [
    {"id": 1, "subject": "デモメール 1", "from": "alice@example.com", "label": "受信トレイ", "body": "これはデモメール1の本文です。", "images": [], "unread": True},
    {"id": 2, "subject": "デモメール 2", "from": "bob@example.com", "label": "受信トレイ", "body": "これはデモメール2の本文です。", "images": [], "unread": True},
    {"id": 3, "subject": "画像メール", "from": "carol@example.com", "label": "受信トレイ", "body": "これは画像付きメールです。", "images": [base64.b64encode(b"fakeimage").decode("utf-8")], "unread": False},
]

LABELS = ["受信トレイ", "送信済み", "ゴミ箱"]

# ----------------------
# ルート（ログイン）
# ----------------------
@app.route("/")
def index():
    if "logged_in" not in session:
        return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Gmail デモ</title>
<style>
body { font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; background:#f1f3f4;}
.login-box { background:#fff; padding:40px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1); text-align:center; width:320px;}
a.login-btn { display:inline-block; background:#1a73e8; color:#fff; padding:12px 24px; border-radius:4px; text-decoration:none; font-weight:500; margin-top:16px;}
a.login-btn:hover { background:#1558b0;}
.links a { color:#5f6368; font-size:14px; margin:0 6px; text-decoration:none;}
.links a:hover { text-decoration:underline;}
</style>
</head>
<body>
<div class="login-box">
<h1>📧 Gmail デモ</h1>
<a class="login-btn" href="{{ url_for('login') }}">ログイン（デモ用）</a>
<div class="links">
<a href="{{ url_for('privacy_policy') }}">プライバシーポリシー</a> |
<a href="{{ url_for('terms') }}">利用規約</a>
</div>
</div>
</body>
</html>
        """)
    return redirect("/emails")

# ----------------------
# デモログイン
# ----------------------
@app.route("/login")
def login():
    session["logged_in"] = True
    session["emails"] = DEMO_EMAILS.copy()
    return redirect("/emails")

# ----------------------
# 未読件数
# ----------------------
def unread_count(emails, folder):
    return sum(1 for e in emails if e["label"]==folder and e["unread"])

# ----------------------
# メール一覧
# ----------------------
@app.route("/emails")
def emails():
    if "logged_in" not in session:
        return redirect("/")
    emails_data = session.get("emails", [])
    return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Gmail デモ</title>
<style>
body { font-family:sans-serif; margin:0; background:#f1f3f4;}
.header {display:flex; justify-content:space-between; align-items:center; background:#fff; border-bottom:1px solid #dadce0; height:56px; padding:0 16px;}
.logo {font-weight:500; color:#d93025; font-size:20px;}
.logout-link {color:#1a73e8; font-size:14px;}
.sidebar {width:220px; background:#f8f9fa; border-right:1px solid #dadce0; padding:12px 0; flex-shrink:0;}
.sidebar .folder {padding:10px 24px; cursor:pointer; font-size:14px; color:#5f6368;}
.sidebar .folder.active {background:#e8f0fe; color:#1967d2; font-weight:500;}
.main {flex:1; display:flex; flex-direction:column;}
.inbox {flex:1; overflow-y:auto; background:#fff; padding:12px;}
.mail-item {padding:8px 12px; border:1px solid #ddd; margin-bottom:8px; border-radius:6px; background:#fff; cursor:pointer;}
.mail-item:hover {background:#f5f5f5;}
.modal-overlay {position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); display:none; justify-content:center; align-items:center; z-index:200;}
.modal {background:#fff; max-width:760px; width:90%; max-height:80vh; overflow-y:auto; padding:18px; border-radius:8px; position:relative;}
.modal-close {position:absolute; right:12px; top:12px; cursor:pointer; font-size:18px; color:#5f6368;}
.modal img{max-width:100%; margin-top:8px; border-radius:4px;}
button{margin:4px;}
</style>
</head>
<body>
<div class="header">
  <div class="logo">Gmail デモ</div>
  <div><a href="{{ url_for('logout') }}" class="logout-link">ログアウト</a></div>
</div>
<div style="display:flex;">
  <div class="sidebar" id="sidebar">
    {% for label in labels %}
    <div class="folder{% if loop.first %} active{% endif %}" data-label="{{ label }}" id="folder-{{ label }}" onclick="selectLabel('{{ label }}')">
      {{ label }} (<span id="count-{{ label }}">{{ unread_count(emails_data,label) }}</span>)
    </div>
    {% endfor %}
    <button onclick="composeEmail()">メール作成</button>
  </div>
  <div class="main">
    <div class="inbox" id="inboxList"></div>
  </div>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <span class="modal-close" onclick="closeModal()">×</span>
    <div id="modalContent"></div>
    <button onclick="sendEmail()">送信（デモ）</button>
    <button onclick="moveTrash()">ゴミ箱へ（デモ）</button>
    <button onclick="deleteEmail()">完全削除（デモ）</button>
  </div>
</div>

<script>
let emails = {{ emails_data|tojson }};
let labels = {{ labels|tojson }};
let currentLabel = '受信トレイ';
let currentEmailId = null;

function renderList(){
    const inbox = document.getElementById("inboxList");
    inbox.innerHTML="";
    emails.filter(e=>e.label===currentLabel).forEach(e=>{
        const div=document.createElement("div");
        div.className="mail-item";
        div.dataset.id=e.id;
        div.draggable=true;
        div.innerHTML="<b>"+e.subject+"</b><br>"+e.from+(e.unread?" <span style='color:red;'>(未読)</span>":"");
        div.onclick=()=>openModal(e.id);
        div.ondragstart=(ev)=>ev.dataTransfer.setData("text/plain",e.id);
        inbox.appendChild(div);
    });
    // 未読件数更新
    labels.forEach(l=>{
        document.getElementById("count-"+l).innerText=emails.filter(e=>e.label===l && e.unread).length;
    });
}

function selectLabel(label){
    currentLabel=label;
    document.querySelectorAll(".sidebar .folder").forEach(d=>d.classList.remove("active"));
    document.getElementById("folder-"+label).classList.add("active");
    renderList();
}

function openModal(id){
    currentEmailId=id;
    const e = emails.find(x=>x.id===id);
    e.unread=false;
    renderList();
    const modal = document.getElementById("modalOverlay");
    const content = document.getElementById("modalContent");
    let html="<h3>"+e.subject+"</h3><p><b>From:</b> "+e.from+"</p><pre>"+e.body+"</pre>";
    e.images.forEach(img=>{
        html+="<img src='data:image/*;base64,"+img+"'>";
    });
    content.innerHTML=html;
    modal.style.display="flex";
}

function closeModal(){ document.getElementById("modalOverlay").style.display="none"; }

function sendEmail(){
    const subject=prompt("件名を入力");
    const body=prompt("本文を入力");
    const id=emails.length?Math.max(...emails.map(e=>e.id))+1:1;
    emails.push({id:id,subject:subject,from:"you@example.com",label:"送信済み",body:body,images:[],unread:false});
    renderList();
    closeModal();
}

function moveTrash(){
    if(currentEmailId){
        const e=emails.find(x=>x.id===currentEmailId);
        e.label="ゴミ箱";
        renderList();
        closeModal();
    }
}

function deleteEmail(){
    if(currentEmailId){
        emails=emails.filter(x=>x.id!==currentEmailId);
        renderList();
        closeModal();
    }
}

function composeEmail(){ sendEmail(); }

// ドラッグ＆ドロップ
document.querySelectorAll(".sidebar .folder").forEach(f=>{
    f.ondragover=(e)=>e.preventDefault();
    f.ondrop=(e)=>{
        e.preventDefault();
        const id=parseInt(e.dataTransfer.getData("text/plain"));
        const em=emails.find(x=>x.id===id);
        if(em){ em.label=f.dataset.label; renderList(); }
    }
});

renderList();
</script>
</body>
</html>
    """, emails_data=emails_data, labels=LABELS, unread_count=unread_count)

# ----------------------
# ログアウト
# ----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ----------------------
# プライバシーポリシー
# ----------------------
@app.route("/privacy-policy")
def privacy_policy():
    return "<h1>プライバシーポリシー</h1><p>デモ用です。個人情報は取得しません。</p>"

# ----------------------
# 利用規約
# ----------------------
@app.route("/terms")
def terms():
    return "<h1>利用規約</h1><p>デモ用です。責任は負いません。</p>"

# ----------------------
# メイン起動
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
