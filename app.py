from flask import Flask, render_template_string, session, redirect, url_for, request
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "demo_secret_key")

# ----------------------
# デモメールデータ（ブラウザで書き換え可能）
# ----------------------
DEMO_EMAILS = [
    {"id": 1, "subject": "デモメール 1", "from": "example1@gmail.com", "label": "受信トレイ", "body": "これはデモメールです。"},
    {"id": 2, "subject": "デモメール 2", "from": "example2@gmail.com", "label": "受信トレイ", "body": "もう一つのデモメールです。"},
    {"id": 3, "subject": "デモメール 3", "from": "example3@gmail.com", "label": "送信済み", "body": "送信済みメールのデモです。"}
]

# ----------------------
# ルート（ログイン判定）
# ----------------------
@app.route("/")
def index():
    if "logged_in" not in session:
        return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gmail Viewer デモ</title>
<style>
body { font-family:"Roboto","Arial",sans-serif; background:#f1f3f4; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
.login-box { background:#fff; padding:40px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1); text-align:center; width:320px; }
h1 { font-size:24px; color:#202124; margin-bottom:24px; }
a.login-btn { display:inline-block; background:#1a73e8; color:#fff; padding:12px 24px; border-radius:4px; text-decoration:none; font-weight:500; margin-bottom:16px; }
a.login-btn:hover { background:#1558b0; }
.links a { color:#5f6368; font-size:14px; margin:0 6px; text-decoration:none; }
.links a:hover { text-decoration:underline; }
</style>
</head>
<body>
<div class="login-box">
<h1>📧 Gmail Viewer デモ</h1>
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
    # セッション内にコピーして操作可能に
    session["emails"] = DEMO_EMAILS.copy()
    return redirect("/emails")

# ----------------------
# メール一覧
# ----------------------
@app.route("/emails")
def emails():
    if "logged_in" not in session:
        return redirect("/")

    emails_data = session.get("emails", [])
    labels = ["受信トレイ", "送信済み", "ゴミ箱"]
    return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gmail Viewer デモ</title>
<style>
body { font-family:"Roboto","Arial",sans-serif; margin:0; background:#f1f3f4; color:#202124;}
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
.mail-item .meta {font-size:12px; color:#555;}
.modal-overlay {position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); display:none; justify-content:center; align-items:center; z-index:200;}
.modal {background:#fff; max-width:760px; width:90%; max-height:80vh; overflow-y:auto; padding:18px; border-radius:8px; position:relative;}
.modal-close {position:absolute; right:12px; top:12px; cursor:pointer; font-size:18px; color:#5f6368;}
</style>
</head>
<body>
<div class="header">
  <div class="logo">Gmail Viewer デモ</div>
  <div><a href="{{ url_for('logout') }}" class="logout-link">ログアウト</a></div>
</div>
<div style="display:flex;">
  <div class="sidebar" id="sidebar">
    {% for label in labels %}
    <div class="folder{% if loop.first %} active{% endif %}" data-label="{{ label }}" onclick="selectLabel('{{ label }}')">{{ label }}</div>
    {% endfor %}
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
let currentLabel = '受信トレイ';
let currentEmailId = null;

function renderList(){
    const inbox = document.getElementById("inboxList");
    inbox.innerHTML = "";
    emails.filter(e=>e.label===currentLabel).forEach(email=>{
        const div = document.createElement("div");
        div.className="mail-item";
        div.draggable=true;
        div.dataset.id=email.id;
        div.innerHTML='<span class="subject">'+email.subject+'</span><br><span class="meta">'+email.from+' | '+email.label+'</span>';
        div.addEventListener("click", ()=>openModal(email.id));
        div.addEventListener("dragstart", e=>{
            e.dataTransfer.setData("text/plain", email.id);
        });
        inbox.appendChild(div);
    });
}

function openModal(id){
    currentEmailId=id;
    const email = emails.find(e=>e.id===id);
    const modal = document.getElementById("modalOverlay");
    const content = document.getElementById("modalContent");
    content.innerHTML="<h3>"+email.subject+"</h3><p><b>From:</b> "+email.from+"</p><pre>"+email.body+"</pre>";
    modal.style.display="flex";
}

function closeModal(){
    document.getElementById("modalOverlay").style.display="none";
}

function selectLabel(label){
    currentLabel=label;
    document.querySelectorAll(".sidebar .folder").forEach(d=>d.classList.remove("active"));
    document.querySelector('.sidebar .folder[data-label="'+label+'"]').classList.add("active");
    renderList();
}

function sendEmail(){
    alert("送信しました（デモ）");
    closeModal();
}

function moveTrash(){
    if(currentEmailId){
        const email = emails.find(e=>e.id===currentEmailId);
        email.label="ゴミ箱";
        renderList();
        closeModal();
    }
}

function deleteEmail(){
    if(currentEmailId){
        emails = emails.filter(e=>e.id!==currentEmailId);
        renderList();
        closeModal();
    }
}

// ドラッグ＆ドロップでラベル変更
document.querySelectorAll(".sidebar .folder").forEach(folder=>{
    folder.addEventListener("dragover", e=>e.preventDefault());
    folder.addEventListener("drop", e=>{
        e.preventDefault();
        const id=parseInt(e.dataTransfer.getData("text/plain"));
        const email = emails.find(em=>em.id===id);
        if(email){
            email.label=folder.dataset.label;
            renderList();
        }
    });
});

renderList();
</script>
</body>
</html>
    """, emails_data=emails_data, labels=labels)

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
    app.run(host="0.0.0.0", port=port)
