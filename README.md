# ⚡ YT-DLP Pro Max GUI

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **🇬🇧 English Documentation below | 🇦🇪 الشرح باللغة العربية بالأسفل**

---

## 🇬🇧 English

A clean, modern, and blazingly fast Graphical User Interface (GUI) for the popular `yt-dlp` tool. It allows you to download videos and audio at maximum speed, supports high-quality merging, background execution, and smart clipboard monitoring.

### ✨ Features
- 🎨 **Eye-Comfort Design:** Modern dark mode with 5 distinct accent colors saved automatically.
- 🚀 **Turbo Speed:** Optimized UI thread that does not consume CPU during high-speed downloads.
- 📋 **Smart Clipboard:** Automatically detects supported video URLs and brings the app to the front.
- ✂️ **Video Trimming:** Download specific parts of a video (e.g., from 00:01:00 to 00:02:00) without downloading the whole file.
- 🔽 **System Tray:** Hide the application to the system tray while downloading in the background.
- ⚙️ **Auto-Startup:** Option to run the application silently in the background on Windows startup.
- 🔓 **Bypass Restrictions:** Use browser cookies (Chrome, Edge, Firefox, etc.) to download from restricted sites like X (Twitter) or Facebook.

### 🛠️ Prerequisites
To unlock the full potential of this app, you need two external tools placed in the same folder as the application:
1. **yt-dlp.exe:** The core downloader. Get it from [yt-dlp Releases](https://github.com/yt-dlp/yt-dlp/releases).
2. **ffmpeg.exe:** Required for merging audio and video into 1080p/4K MP4. Get it from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (extract the ZIP and copy `bin/ffmpeg.exe`).

### 🚀 Installation & Usage

**Option 1: Running from Python Script**
1. Install [Python](https://www.python.org/downloads/).
2. Clone this repository or download the ZIP.
3. Install required packages:
```bash
   pip install Pillow pystray
```
4. Place `yt-dlp.exe` and `ffmpeg.exe` in the same directory.
5. Run the script:

```bash
   python main.py

```

**Option 2: Compiling to a Standalone `.exe**`
If you want to create a single `.exe` file so you don't need Python installed:

1. Install PyInstaller:

```bash
   pip install pyinstaller

```

2. Build the executable:

```bash
   pyinstaller --noconsole --onefile main.py

```

3. You will find the final `.exe` inside the `dist/` folder. Move it to your desired location, place `yt-dlp.exe` and `ffmpeg.exe` next to it, and enjoy!

---

## 🇦🇪 العربية

واجهة رسومية (GUI) احترافية، سريعة، ومريحة للعين لأداة التحميل الشهيرة `yt-dlp`. تتيح لك تحميل الفيديوهات والصوتيات بأقصى سرعة مع دعم دمج الجودات العالية، العمل في الخلفية، والتقاط الروابط تلقائياً.

### ✨ المميزات

* 🎨 **تصميم مريح للعين (Dark Mode):** مع 5 ألوان (Themes) متغيرة تُحفظ تلقائياً.
* 🚀 **سرعة صاروخية:** واجهة خفيفة لا تستهلك موارد المعالج أثناء التحميل.
* 📋 **التقاط ذكي للروابط:** بمجرد نسخ أي رابط، سيقفز البرنامج للمقدمة جاهزاً للتحميل.
* ✂️ **قص الفيديو:** تحميل جزء معين من الفيديو (من الدقيقة كذا إلى الدقيقة كذا) بدون تحميل الفيديو كاملاً.
* 🔽 **العمل في الخلفية (System Tray):** إمكانية إخفاء البرنامج بجوار الساعة أثناء التحميل.
* ⚙️ **بدء التشغيل مع الويندوز:** خيار لتشغيل البرنامج بصمت مع بداية النظام.
* 🔓 **تخطي الحجب:** دعم سحب تسجيل الدخول من المتصفحات (Chrome, Edge, Firefox) للتحميل من المواقع المقيدة مثل X (Twitter) أو Facebook.

### 🛠️ متطلبات التشغيل

لكي يعمل البرنامج بكامل طاقته، يحتاج إلى أداتين مساعدتين يجب وضعهما في نفس مجلد البرنامج:

1. **أداة التحميل (yt-dlp):** قم بتحميل أحدث إصدار من [صفحة yt-dlp الرسمية](https://github.com/yt-dlp/yt-dlp/releases).
2. **أداة دمج الصوت والصورة (FFmpeg):** (مهمة جداً لتحميل جودات 1080p و 4K). قم بتحميلها من [موقع FFmpeg](https://www.gyan.dev/ffmpeg/builds/)، استخرج الملف المضغوط، وادخل لمجلد `bin`، وانسخ ملف `ffmpeg.exe` فقط.

### 🚀 طريقة التثبيت والاستخدام

**الخيار الأول: التشغيل المباشر عبر بايثون**

1. تأكد من تثبيت [Python](https://www.python.org/downloads/) على جهازك.
2. قم بتنزيل هذا المشروع (Clone or Download ZIP) واستخرجه في مجلد.
3. قم بتثبيت المكتبات المطلوبة بفتح موجه الأوامر (CMD) وكتابة:

```bash
   pip install Pillow pystray

```

4. ضع ملفي `yt-dlp.exe` و `ffmpeg.exe` داخل المجلد بجوار ملف الكود.
5. قم بتشغيل البرنامج:

```bash
   python main.py

```

**الخيار الثاني: تحويل البرنامج إلى ملف تنفيذي `.exe**`
إذا كنت ترغب في تحويل البرنامج لملف يعمل بضغطة زر بدون الحاجة لبرنامج بايثون مستقبلاً:

1. قم بتثبيت أداة التحويل:

```bash
   pip install pyinstaller

```

2. افتح موجه الأوامر (CMD) في نفس مسار ملف الكود، وقم بتشغيل أمر التحويل التالي:

```bash
   pyinstaller --noconsole --onefile main.py

```

3. ستجد برنامجك النهائي بداخل مجلد `dist/`. قم بنقله لأي مكان، وضع بجواره `yt-dlp.exe` و `ffmpeg.exe`، وابدأ الاستخدام مباشرة!

```

```
