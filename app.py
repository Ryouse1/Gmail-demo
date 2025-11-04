from flask import Flask, render_template_string
import base64

app = Flask(__name__)

# ----------------------
# デモ用サンプルメール
# ----------------------
all_emails = [
    {
        "subject": "デモメール1",
        "body": "これはデモメールです。\nGmail Viewerのデザイン確認用。",
        "label": "受信トレイ",
        "from": "demo@example.com",
        "images": []
    },
    {
        "subject": "デモメール2",
        "body": "添付画像付きのサンプルメールです。",
        "label": "受信トレイ",
        "from": "test@example.com",
        "images": [
            # Base64でサンプル画像
            "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
        ]
    }
]

labels = [{"name":"受信トレイ"},{"name":"プロモーション"},{"name":"ソーシャル"}]

# ----------------------
# ルート
# ----------------------
@app.route("/")
def index():
    return render_template_string("""
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gmail Viewer Demo</title>
<style>
body { font-family:"Roboto","Arial",sans-serif; margin:0; background:#f1f3f4; color:#202124;}
a { text-decoration:none; color:inherit;}
.header {display:flex; justify-content:space-between; align-items:center; background:#fff; border-bottom:1px solid #dadce0; height:56px; padding:0 16px; position:sticky; top:0;}
.logo {font-weight:500; color:#d93025; font-size:20px;}
.sidebar {width:220px; background:#f8f9fa; border-right:1px solid #dadce0; padding:12px 0; flex-shrink:0;}
.sidebar .folder {padding:10px 24px; cursor:pointer; font-size:14px; color:#5f6368;}
.sidebar .folder.active {background:#e8f0fe; color:#1967d2; font-weight:500;}
.main {flex:1; display:flex; flex-direction:column;}
.inbox {flex:1; overflow-y:auto; background:#fff;}
.mail-item {padding:12px 16px; border-bottom:1px solid #f1f3f4; cursor:pointer; display:flex; flex-direction:column; transition:background 0.2s;}
.mail-item:hover {background:#f5f5f5;}
.mail-item .meta {display:flex; justify-content:space-between; font-size:13px; color:#5f6368;}
.mail-item .subject {font-weight:500; margin-top:4px;}
.mail-item .preview {font-size:13px; color:#5f6368; margin-top:4px;}
.modal-overlay {position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); display:none; justify-content:center; align-items:center; z-index:200;}
.modal {background:#fff; max-width:760px; width:90%; max-height:80vh; overflow-y:auto; padding:18px; border-radius:8px; position:relative;}
.modal-close {position:absolute; right:12px; top:12px; cursor:pointer; font-size:18px; color:#5f6368;}
.modal img {max-width:100%; margin-top:8px; border-radius:4px;}
</style>
</head>
<body>
<div class="header"><div class="logo">Gmail Viewer Demo</div></div>
<div style="display:flex;">
  <div class="sidebar">
    <div class="folder active">受信トレイ</div>
    {% for label in labels %}
    <div class="folder">{{ label.name }}</div>
    {% endfor %}
  </div>
  <div class="main">
    <div class="inbox">
      {% for email in emails %}
      <div class="mail-item" onclick="openModal({{ loop.index0 }})">
        <div class="meta"><span>{{ email.from }}</span><span>{{ email.label }}</span></div>
        <div class="subject">{{ email.subject }}</div>
        <div class="preview"><pre>{{ email.body[:100] }}{% if email.body|length > 100 %}...{% endif %}</pre></div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <span class="modal-close" onclick="closeModal()">×</span>
    <div id="modalContent"></div>
  </div>
</div>

<script>
const emails = {{ emails|tojson }};
function openModal(idx){
    const modal = document.getElementById("modalOverlay");
    const content = document.getElementById("modalContent");
    const email = emails[idx];
    let html = "<h3>"+email.subject+"</h3>";
    html += "<p><strong>From:</strong> "+email.from+"</p>";
    html += "<p><strong>Label:</strong> "+email.label+"</p>";
    html += "<pre>"+email.body+"</pre>";
    if(email.images.length>0){
        email.images.forEach(img=>{
            html += "<img src='data:image/*;base64,"+img+"'>";
        });
    }
    content.innerHTML = html;
    modal.style.display="flex";
}
function closeModal(){
    document.getElementById("modalOverlay").style.display="none";
}
</script>
</body>
</html>
    """, emails=all_emails, labels=labels)

# ----------------------
# メイン起動
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
