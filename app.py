from flask import Flask, render_template_string, session, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "demo_secret_key")

# ----------------------
# デモメールデータ
# ----------------------
DEMO_EMAILS = [
    {"subject": "デモメール 1", "from": "example1@gmail.com", "label": "受信トレイ", "body": "これはデモメールです。"},
    {"subject": "デモメール 2", "from": "example2@gmail.com", "label": "受信トレイ", "body": "もう一つのデモメールです。"},
    {"subject": "デモメール 3", "from": "example3@gmail.com", "label": "送信済み", "body": "送信済みメールのデモです。"}
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
            .login-box { background:#fff; padding:40px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1); text-align:center; width:360px; }
            h1 { font-size:28px; color:#202124; margin-bottom:24px; font-weight:500; }
            a.login-btn { display:inline-block; background:#1a73e8; color:#fff; padding:14px 28px; border-radius:4px; text-decoration:none; font-weight:500; font-size:16px; transition:background 0.2s; }
            a.login-btn:hover { background:#1558b0; }
            .links { margin-top:20px; font-size:12px; color:#5f6368; }
            .links a { color:#5f6368; text-decoration:none; margin:0 6px; }
            .links a:hover { text-decoration:underline; }
        </style>
        </head>
        <body>
            <div class="login-box">
                <h1>📧 Gmail Viewer</h1>
                <p>デモ用ログインです</p>
                <!-- ここをクリックしたら /login に遷移 -->
                <a class="login-btn" href="{{ url_for('login') }}">ログインしてメールを見る</a>
                <div class="links">
                    <a href="{{ url_for('privacy_policy') }}">プライバシーポリシー</a> |
                    <a href="{{ url_for('terms') }}">利用規約</a>
                </div>
            </div>
        </body>
        </html>
        """)
    # すでにログイン済みならメール画面へ
    return redirect("/emails")

# ----------------------
# デモログイン（クリックでメール画面へ遷移）
# ----------------------
@app.route("/login")
def login():
    session["logged_in"] = True
    return redirect("/emails")  # クリックで直接メール画面に遷移

# ----------------------
# メール一覧
# ----------------------
@app.route("/emails")
def emails():
    if "logged_in" not in session:
        return redirect("/")

    return render_template_string("""
    <!doctype html>
    <html lang="ja">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gmail Viewer デモ</title>
    <style>
        body { font-family:"Roboto","Arial",sans-serif; margin:0; background:#f1f3f4; color:#202124;}
        .header {display:flex; justify-content:space-between; align-items:center; background:#fff; border-bottom:1px solid #dadce0; height:64px; padding:0 24px; box-shadow:0 1px 3px rgba(0,0,0,0.08);}
        .logo {font-weight:500; color:#d93025; font-size:22px;}
        .header a.logout {color:#1a73e8; text-decoration:none; font-weight:500;}
        .sidebar {width:240px; background:#f8f9fa; border-right:1px solid #dadce0; padding-top:12px; position:fixed; top:64px; bottom:0; overflow-y:auto;}
        .sidebar .folder {padding:12px 24px; cursor:pointer; font-size:14px; color:#5f6368;}
        .sidebar .folder.active {background:#e8f0fe; color:#1967d2; font-weight:500;}
        .main {margin-left:240px; padding:16px; margin-top:64px;}
        .mail-item {background:#fff; margin-bottom:12px; padding:14px 18px; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.08);}
        .mail-item .subject {font-weight:500; font-size:16px; margin-bottom:4px;}
        .mail-item .meta {font-size:13px; color:#5f6368; margin-bottom:6px;}
    </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">Gmail Viewer デモ</div>
            <a class="logout" href="{{ url_for('logout') }}">ログアウト</a>
        </div>
        <div class="sidebar">
            <div class="folder active">受信トレイ</div>
            <div class="folder">送信済み</div>
            <div class="folder">下書き</div>
        </div>
        <div class="main">
            {% for email in emails %}
                <div class="mail-item">
                    <div class="meta">{{ email.from }} | {{ email.label }}</div>
                    <div class="subject">{{ email.subject }}</div>
                    <pre>{{ email.body }}</pre>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """, emails=DEMO_EMAILS)

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
    app.run(host="0.0.0.0", port=port)
