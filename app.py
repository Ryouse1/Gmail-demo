from flask import Flask, render_template_string, session, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "demo_secret_key")

# ----------------------
# デモメールデータ
# ----------------------
DEMO_EMAILS = {
    "inbox": [
        {"subject": "受信トレイメール1", "from": "alice@gmail.com", "body": "これは受信トレイのデモメールです。全文を表示できます。"},
        {"subject": "受信トレイメール2", "from": "bob@gmail.com", "body": "もう一つの受信メールです。内容も長めです。"}
    ],
    "sent": [
        {"subject": "送信済みメール1", "from": "me@gmail.com", "body": "これは送信済みメールのデモです。"},
        {"subject": "送信済みメール2", "from": "me@gmail.com", "body": "別の送信メールです。"}
    ],
    "trash": [
        {"subject": "ゴミ箱メール1", "from": "spam@gmail.com", "body": "これはゴミ箱のメールです。"},
    ],
    "labels": {
        "重要": [
            {"subject": "重要メール1", "from": "boss@gmail.com", "body": "これは重要ラベルのメールです。"}
        ]
    }
}

FOLDERS = ["inbox", "sent", "trash"] + list(DEMO_EMAILS["labels"].keys())

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
                <a class="login-btn" href="{{ url_for('login') }}">Googleでログイン</a>
                <div class="links">
                    <a href="{{ url_for('privacy_policy') }}">プライバシーポリシー</a> |
                    <a href="{{ url_for('terms') }}">利用規約</a>
                </div>
            </div>
        </body>
        </html>
        """)
    return redirect(url_for("emails", folder="inbox"))

# ----------------------
# デモログイン
# ----------------------
@app.route("/login")
def login():
    session["logged_in"] = True
    return redirect(url_for("emails", folder="inbox"))

# ----------------------
# メール一覧（全文表示モーダル付き）
# ----------------------
@app.route("/emails/<folder>")
def emails(folder):
    if "logged_in" not in session:
        return redirect("/")

    # メール取得
    if folder in DEMO_EMAILS:
        folder_emails = DEMO_EMAILS[folder]
    elif folder in DEMO_EMAILS["labels"]:
        folder_emails = DEMO_EMAILS["labels"][folder]
    else:
        folder_emails = []

    return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gmail Viewer デモ</title>
<style>
body { font-family:"Roboto","Arial",sans-serif; margin:0; background:#f1f3f4; color:#202124;}
a { text-decoration:none; color:inherit; }
.header {display:flex; justify-content:space-between; align-items:center; background:#fff; border-bottom:1px solid #dadce0; height:56px; padding:0 16px;}
.logo {font-weight:500; color:#d93025; font-size:20px;}
.sidebar {width:200px; background:#f8f9fa; border-right:1px solid #dadce0; padding:12px 0; flex-shrink:0;}
.sidebar a {display:block; padding:10px 20px; color:#5f6368; margin-bottom:2px; border-radius:4px;}
.sidebar a.active {background:#e8f0fe; color:#1967d2; font-weight:500;}
.main {flex:1; padding:16px;}
.mail-item {background:#fff; margin-bottom:12px; padding:12px 16px; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.1); cursor:pointer;}
.mail-item .subject {font-weight:500;}
.mail-item .meta {font-size:13px; color:#5f6368; margin-bottom:8px;}
.modal-overlay {position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); display:none; justify-content:center; align-items:center; z-index:200;}
.modal {background:#fff; max-width:700px; width:90%; max-height:80vh; overflow-y:auto; padding:20px; border-radius:8px; position:relative;}
.modal-close {position:absolute; top:12px; right:12px; cursor:pointer; font-size:20px; color:#5f6368;}
</style>
</head>
<body>
<div class="header">
    <div class="logo">Gmail Viewer デモ</div>
    <div><a href="{{ url_for('logout') }}">ログアウト</a></div>
</div>
<div style="display:flex;">
    <div class="sidebar">
        {% for f in folders %}
        <a href="{{ url_for('emails', folder=f) }}" class="{{ 'active' if f==folder else '' }}">{{ f.capitalize() }}</a>
        {% endfor %}
    </div>
    <div class="main">
        {% for email in folder_emails %}
        <div class="mail-item" onclick="openModal({{ loop.index0 }})">
            <div class="meta">{{ email.from }} | {{ folder }}</div>
            <div class="subject">{{ email.subject }}</div>
            <pre>{{ email.body[:50] }}{% if email.body|length>50 %}...{% endif %}</pre>
        </div>
        {% endfor %}
        {% if folder_emails|length==0 %}<p>メールはありません。</p>{% endif %}
    </div>
</div>

<div class="modal-overlay" id="modalOverlay">
    <div class="modal">
        <span class="modal-close" onclick="closeModal()">×</span>
        <div id="modalContent"></div>
    </div>
</div>

<script>
const emails = {{ folder_emails|tojson }};
function openModal(idx){
    const modal = document.getElementById("modalOverlay");
    const content = document.getElementById("modalContent");
    const email = emails[idx];
    let html = "<h3>"+email.subject+"</h3>";
    html += "<p><strong>From:</strong> "+email.from+"</p>";
    html += "<pre>"+email.body+"</pre>";
    content.innerHTML = html;
    modal.style.display="flex";
}
function closeModal(){ document.getElementById("modalOverlay").style.display="none"; }
</script>

</body>
</html>
""", folder_emails=folder_emails, folders=FOLDERS, folder=folder)

# ----------------------
# ログアウト
# ----------------------
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")

# ----------------------
# プライバシーポリシー
# ----------------------
@app.route("/privacy-policy")
def privacy_policy():
    return render_template_string("""
<h1>プライバシーポリシー</h1>
<p>最終更新日：2025年11月1日</p>
<p>このアプリはデモ用です。個人情報は取得しません。</p>
""")

# ----------------------
# 利用規約
# ----------------------
@app.route("/terms")
def terms():
    return render_template_string("""
<h1>利用規約</h1>
<p>最終更新日：2025年11月1日</p>
<p>このデモアプリの利用に関して、開発者は一切責任を負いません。</p>
""")

# ----------------------
# メイン起動
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
