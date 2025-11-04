from flask import Flask, render_template_string, url_for
import os
from dotenv import load_dotenv

load_dotenv()  # Renderでは必要に応じて

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
# ルート（メール一覧）
# ----------------------
@app.route("/")
def index():
    return render_template_string("""
    <h1>📧 Gmail Viewer デモ（本番向け）</h1>
    <p>このデモは Gmail API を使わず、ダミーのメールを表示します。</p>
    <ul>
    {% for email in emails %}
        <li>
            <strong>件名:</strong> {{ email.subject }}<br>
            <strong>送信者:</strong> {{ email.from }}<br>
            <strong>ラベル:</strong> {{ email.label }}<br>
            <pre>{{ email.body }}</pre>
        </li>
    {% endfor %}
    </ul>
    <p><a href="/privacy-policy">プライバシーポリシー</a> | <a href="/terms">利用規約</a></p>
    """, emails=DEMO_EMAILS)

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

