import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys
import json
import datetime
import shutil
import time
import re

# ─── فحص المكتبات الخارجية ───
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

# ══════════════════════════════════════════════════════════════
#  Constants & Theme (الألوان الهادئة والمريحة للعين)
# ══════════════════════════════════════════════════════════════
BG      = "#0d0d12"
SURFACE = "#13131c"
CARD    = "#1a1a28"
BORDER  = "#2a2a40"
SUCCESS = "#1a8c43" 
ERROR   = "#c42535" 
WARNING = "#f7d633"
TEXT    = "#e8e8f0"
SUBTEXT = "#8888aa"
WHITE   = "#ffffff"

ACCENTS = {
    "أصفر": "#c79f22",    
    "بنفسجي": "#5048b3",  
    "أزرق": "#1560bd",    
    "أخضر": "#1a8c43",    
    "أحمر": "#c42535"     
}

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "download_history.json")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.json")

BROWSERS = ["بدون (الوضع الافتراضي)", "chrome", "edge", "firefox", "brave", "opera"]
QUALITY_OPTIONS = [("تلقائي (أفضل جودة)", "auto"), ("🎬 1080p (Full HD)", "1080"), ("📺 720p (HD)", "720"), ("📱 480p (SD)", "480")]
FORMAT_OPTIONS = [("تلقائي (بدون تحويل)", "auto"), ("MP4 (الأكثر توافقاً)", "mp4"), ("MKV (جودة عالية)", "mkv"), ("MP3 (صوت فقط)", "mp3")]

# ══════════════════════════════════════════════════════════════
#  Helpers & Config
# ══════════════════════════════════════════════════════════════
def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except: pass

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)
    except: pass

def find_ytdlp():
    return next((p for p in ["yt-dlp.exe", "yt-dlp"] if shutil.which(p) or os.path.exists(p)), "yt-dlp")

def check_ffmpeg():
    return shutil.which("ffmpeg") is not None

def is_video_url(text):
    return text.startswith("http") and ("://" in text)

# ══════════════════════════════════════════════════════════════
#  Main App
# ══════════════════════════════════════════════════════════════
class YtDlpApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YT-DLP Pro Max  •  الإصدار المستقر النهائي")
        self.root.geometry("750x800") 
        self.root.minsize(700, 750)
        self.root.configure(bg=BG)

        self.has_ffmpeg = check_ffmpeg()
        
        self.config = load_config()
        saved_color = self.config.get("theme_color", ACCENTS["أصفر"])
        self.current_accent = saved_color if saved_color in ACCENTS.values() else ACCENTS["أصفر"]
        
        self.download_path  = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
        self.browser_var    = tk.StringVar(value=BROWSERS[0])
        self.quality_var    = tk.StringVar()
        self.format_var     = tk.StringVar()
        
        self.playlist_var   = tk.BooleanVar(value=False)
        self.subtitle_var   = tk.BooleanVar(value=False)
        self.trim_var       = tk.BooleanVar(value=False)
        self.startup_var    = tk.BooleanVar(value=self._check_startup())

        self.is_downloading   = False
        self.current_process  = None
        self._last_clipboard  = ""
        self._clipboard_watch = True

        self.history = load_history()

        self._build_ui()
        self._monitor_clipboard()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._change_color(self.current_accent, save=False)

        # 💡 [السر هنا] التأكد من طريقة تشغيل البرنامج: هل فتحه الويندوز أم المستخدم؟
        if "--startup" in sys.argv and TRAY_AVAILABLE and PIL_AVAILABLE:
            self.root.withdraw() # إخفاء الواجهة فوراً
            self._create_tray()  # تحويله لأيقونة بجوار الساعة

    # ──────────────────────────────────────
    #  UI Builder
    # ──────────────────────────────────────
    def _build_ui(self):
        self.hdr = tk.Frame(self.root, bg=self.current_accent, height=56)
        self.hdr.pack(fill="x")
        self.hdr.pack_propagate(False)

        self.hdr_title = tk.Label(self.hdr, text="⚡ YT-DLP Pro Max", font=("Segoe UI", 15, "bold"), bg=self.current_accent, fg=BG)
        self.hdr_title.pack(side="left", padx=18, pady=12)

        self.color_frame = tk.Frame(self.hdr, bg=self.current_accent)
        self.color_frame.pack(side="right", padx=15)
        
        self.color_canvases = []
        for name, hex_color in ACCENTS.items():
            c = tk.Canvas(self.color_frame, width=22, height=22, bg=self.current_accent, highlightthickness=0, cursor="hand2")
            c.pack(side="left", padx=4)
            c.create_oval(2, 2, 20, 20, fill=hex_color, outline=BG, width=1.5)
            c.bind("<Button-1>", lambda e, h=hex_color: self._change_color(h))
            self.color_canvases.append(c)

        self.watch_btn = tk.Button(self.hdr, text="🔗 التقاط الروابط: يعمل", font=("Segoe UI", 9, "bold"),
                                   bg="#333344", fg=WHITE, bd=0, padx=10, pady=5, cursor="hand2", command=self._toggle_watch)
        self.watch_btn.pack(side="right", padx=10)

        self.tray_btn = tk.Button(self.hdr, text="🔽 إخفاء", font=("Segoe UI", 9, "bold"),
                                  bg="#333344", fg=WHITE, bd=0, padx=10, pady=5, cursor="hand2", command=self._hide_to_tray)
        self.tray_btn.pack(side="right", padx=5)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        self.style.configure("Dark.TNotebook.Tab", background=CARD, foreground=SUBTEXT, padding=[14, 6], font=("Segoe UI", 10, "bold"))
        self.style.map("Dark.TNotebook.Tab", background=[("selected", self.current_accent)], foreground=[("selected", BG)])
        self.style.configure("Green.Horizontal.TProgressbar", troughcolor=CARD, background=SUCCESS, thickness=12)
        
        self.nb = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_dl   = tk.Frame(self.nb, bg=BG)
        self.tab_set  = tk.Frame(self.nb, bg=BG)

        self.nb.add(self.tab_dl,   text="  📥 لوحة التحميل الذكية  ")
        self.nb.add(self.tab_set,  text="  ⚙️ الإعدادات والسجل  ")

        self._build_download_tab()
        self._build_settings_tab()

    def _build_download_tab(self):
        p = tk.Frame(self.tab_dl, bg=BG, padx=20, pady=10)
        p.pack(fill="both", expand=True)

        self._label(p, "🔗 رابط الفيديو أو البلايليست:")
        url_row = tk.Frame(p, bg=BG)
        url_row.pack(fill="x", pady=(4, 15)) 
        
        url_box = tk.Frame(url_row, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        url_box.pack(side="left", fill="x", expand=True)
        self.url_entry = tk.Entry(url_box, font=("Segoe UI", 11), bg=CARD, fg=TEXT, insertbackground=TEXT, bd=0)
        self.url_entry.pack(fill="x", padx=12, pady=12, expand=True)

        self.paste_btn = self._btn(url_row, "📋 لصق", self.current_accent, self._paste_url, side="right", px=(6,0))
        self.clear_btn = self._btn(url_row, "✖ مسح", BORDER, self._clear_url, side="right", px=(6,0))

        qf_row = tk.Frame(p, bg=BG)
        qf_row.pack(fill="x", pady=(0, 10))

        q_frame = tk.Frame(qf_row, bg=BG)
        q_frame.pack(side="right", fill="both", expand=True, padx=(10, 0)) 
        self._label(q_frame, "🎬 الجودة:")
        self.quality_cb = ttk.Combobox(q_frame, textvariable=self.quality_var, state="readonly", values=[q[0] for q in QUALITY_OPTIONS])
        self.quality_cb.current(0) 
        self.quality_cb.pack(fill="x", pady=4)

        f_frame = tk.Frame(qf_row, bg=BG)
        f_frame.pack(side="left", fill="both", expand=True, padx=(0, 10)) 
        self._label(f_frame, "🎞️ الصيغة:")
        self.format_cb = ttk.Combobox(f_frame, textvariable=self.format_var, state="readonly", values=[f[0] for f in FORMAT_OPTIONS] if self.has_ffmpeg else [FORMAT_OPTIONS[0][0]])
        self.format_cb.current(0)
        self.format_cb.pack(fill="x", pady=4)
        if not self.has_ffmpeg: self.format_cb.config(state="disabled")

        trim_row = tk.Frame(p, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        trim_row.pack(fill="x", pady=(0, 10))
        self._check(trim_row, "✂️ قص الفيديو", self.trim_var).pack(side="right", padx=10, pady=8)
        
        tk.Label(trim_row, text="من:", bg=CARD, fg=TEXT).pack(side="right")
        self.trim_start = tk.Entry(trim_row, width=8, bg=SURFACE, fg=TEXT, bd=0, justify="center")
        self.trim_start.insert(0, "00:00:00")
        self.trim_start.pack(side="right", padx=5)
        
        tk.Label(trim_row, text="إلى:", bg=CARD, fg=TEXT).pack(side="right")
        self.trim_end = tk.Entry(trim_row, width=8, bg=SURFACE, fg=TEXT, bd=0, justify="center")
        self.trim_end.insert(0, "00:01:00")
        self.trim_end.pack(side="right", padx=5)

        path_row = tk.Frame(p, bg=BG)
        path_row.pack(fill="x", pady=(0, 10))
        tk.Entry(path_row, textvariable=self.download_path, font=("Segoe UI", 10), bg=CARD, fg=TEXT, bd=0).pack(side="left", fill="x", expand=True, padx=(0,10), ipady=5)
        self.browse_btn = self._btn(path_row, "📁 تصفح", self.current_accent, self._browse, side="right", px=0)
        self.browse_btn.config(fg=BG) 

        opts_row = tk.Frame(p, bg=BG)
        opts_row.pack(fill="x", pady=(0, 10))
        self._check(opts_row, "📂 تحميل بلايليست (ترقيم تلقائي)", self.playlist_var).pack(side="right", padx=10)
        self._check(opts_row, "💬 تحميل الترجمة", self.subtitle_var).pack(side="right", padx=10)

        self.download_btn = tk.Button(p, text="⬇  بدء التحميل", font=("Segoe UI", 13, "bold"), bg=self.current_accent, fg=BG, bd=0, pady=10, cursor="hand2", command=self._start_download)
        self.download_btn.pack(fill="x", pady=(0, 5))
        
        self.stop_btn = tk.Button(p, text="⏹ إيقاف التحميل", font=("Segoe UI", 10, "bold"), bg=ERROR, fg="black", bd=0, pady=5, cursor="hand2", state="disabled", command=self._stop_download)
        self.stop_btn.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(p, style="Green.Horizontal.TProgressbar", mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 5))
        
        self.status_lbl = tk.Label(p, text="مستعد للتحميل...", bg=BG, fg=SUBTEXT, font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(fill="x", pady=(0, 5))

        self.log_text = tk.Text(p, height=6, font=("Consolas", 9), bg=CARD, fg=TEXT, bd=0, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _build_settings_tab(self):
        p = tk.Frame(self.tab_set, bg=BG, padx=24, pady=20)
        p.pack(fill="both", expand=True)

        self.upd_btn = self._btn(p, "🔄 تحديث الأداة (yt-dlp)", self.current_accent, self._update_ytdlp, side=None, fill="x", pady=5)
        self.upd_btn.config(fg=BG)
        self._btn(p, "📂 فتح المجلد", "#333355", lambda: os.startfile(self.download_path.get()), side=None, fill="x", pady=5)
        
        self._label(p, "\n🔐 سحب تسجيل الدخول (فيسبوك / إكس):")
        self.browser_cb = ttk.Combobox(p, textvariable=self.browser_var, state="readonly", values=BROWSERS)
        self.browser_cb.current(0)
        self.browser_cb.pack(fill="x", pady=5)

        self._label(p, "\n⚙️ إعدادات النظام المتقدمة:")
        cb_startup = tk.Checkbutton(p, text="🚀 تشغيل البرنامج تلقائياً مخفياً مع بداية الويندوز", variable=self.startup_var, 
                                    font=("Segoe UI", 10, "bold"), bg=BG, fg=TEXT, selectcolor=BG, 
                                    activebackground=BG, activeforeground=TEXT, highlightthickness=0, 
                                    command=self._toggle_startup)
        cb_startup.pack(anchor="w", pady=(10, 0))

    # ──────────────────────────────────────
    #  UI & Color Helpers
    # ──────────────────────────────────────
    def _change_color(self, hex_color, save=True):
        self.current_accent = hex_color
        
        if save:
            self.config["theme_color"] = hex_color
            save_config(self.config)

        self.hdr.config(bg=self.current_accent)
        self.hdr_title.config(bg=self.current_accent)
        self.color_frame.config(bg=self.current_accent)
        for c in self.color_canvases:
            c.config(bg=self.current_accent)
            
        text_col = BG if hex_color == ACCENTS["أصفر"] else WHITE
        
        self.hdr_title.config(fg=text_col)
        self.style.map("Dark.TNotebook.Tab", background=[("selected", self.current_accent)], foreground=[("selected", text_col)])
        
        if hasattr(self, 'download_btn'): self.download_btn.config(bg=self.current_accent, fg=text_col)
        if hasattr(self, 'browse_btn'): self.browse_btn.config(bg=self.current_accent, fg=text_col)
        if hasattr(self, 'upd_btn'): self.upd_btn.config(bg=self.current_accent, fg=text_col)
        if hasattr(self, 'paste_btn'): self.paste_btn.config(bg=self.current_accent, fg=text_col)

    def _label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"), bg=BG, fg=SUBTEXT, anchor="e").pack(fill="x")

    def _btn(self, parent, text, color, cmd, side="left", px=(6,0), fill=None, pady=0):
        b = tk.Button(parent, text=text, font=("Segoe UI", 9, "bold"), bg=color, fg=WHITE, bd=0, padx=12, pady=7, cursor="hand2", command=cmd)
        if side: b.pack(side=side, padx=px)
        else: b.pack(fill=fill or "none", pady=pady)
        return b

    def _check(self, parent, text, var):
        return tk.Checkbutton(parent, text=text, variable=var, font=("Segoe UI", 9, "bold"), bg=CARD, fg=TEXT, selectcolor=CARD, activebackground=CARD, activeforeground=TEXT, highlightthickness=0)

    # ──────────────────────────────────────
    #  Clipboard & Windows Startup
    # ──────────────────────────────────────
    def _check_startup(self):
        if not WINREG_AVAILABLE: return False
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "YTDLP_Pro_Max")
            winreg.CloseKey(key)
            return True
        except:
            return False

    def _toggle_startup(self):
        if not WINREG_AVAILABLE: 
            messagebox.showerror("خطأ", "خاصية بدء التشغيل غير مدعومة على نظامك.", parent=self.root)
            self.startup_var.set(False)
            return
            
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            if self.startup_var.get(): 
                exe_path = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                
                # 💡 تم إضافة --startup ليفتح البرنامج مخفياً
                if script_path.lower().endswith('.py') or script_path.lower().endswith('.pyw'):
                    cmd = f'"{exe_path}" "{script_path}" --startup'
                else:
                    cmd = f'"{script_path}" --startup'
                    
                winreg.SetValueEx(key, "YTDLP_Pro_Max", 0, winreg.REG_SZ, cmd)
            else: 
                try: winreg.DeleteValue(key, "YTDLP_Pro_Max")
                except: pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تعديل إعدادات بدء التشغيل:\n{e}", parent=self.root)
            self.startup_var.set(not self.startup_var.get())

    def _bring_to_front(self):
        self.root.deiconify() 
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True) 
        self.root.after(2000, lambda: self.root.attributes("-topmost", False))

    def _monitor_clipboard(self):
        if not self._clipboard_watch: return
        try:
            cur = self.root.clipboard_get().strip()
            if cur != self._last_clipboard and is_video_url(cur):
                self._last_clipboard = cur
                self._clear_url()
                self.url_entry.insert(0, cur)
                self._bring_to_front() 
        except: pass
        self.root.after(1500, self._monitor_clipboard)

    def _toggle_watch(self):
        self._clipboard_watch = not self._clipboard_watch
        if self._clipboard_watch:
            self.watch_btn.config(text="🔗 التقاط الروابط: يعمل", bg="#333344")
        else:
            self.watch_btn.config(text="🔗 التقاط الروابط: متوقف", bg=BORDER)

    def _clear_url(self):
        self.url_entry.delete(0, "end")

    def _paste_url(self):
        try:
            t = self.root.clipboard_get().strip()
            if t:
                self._clear_url()
                self.url_entry.insert(0, t)
        except: pass

    def _browse(self):
        f = filedialog.askdirectory()
        if f: self.download_path.set(f)

    # ──────────────────────────────────────
    #  Download Core 
    # ──────────────────────────────────────
    def _start_download(self):
        if self.is_downloading: return
        url = self.url_entry.get().strip()
        if not url: return

        if self.trim_var.get() and not self.has_ffmpeg:
            messagebox.showerror("خطأ", "خاصية قص الفيديو تتطلب وجود ملف ffmpeg.exe بجوار البرنامج.", parent=self.root)
            return

        self.is_downloading = True
        self.download_btn.config(text="⏳ جاري التحميل...", state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.start(15) 
        self.status_lbl.config(text="⏳ جاري التحميل بأقصى سرعة...", fg=WARNING)

        save_path = self.download_path.get().strip()
        browser_choice = self.browser_var.get()
        
        q_val = next((q[1] for q in QUALITY_OPTIONS if q[0] == self.quality_var.get()), "auto")
        f_val = next((f[1] for f in FORMAT_OPTIONS if f[0] == self.format_var.get()), "auto")
        
        threading.Thread(target=self._dl_thread, args=(url, save_path, browser_choice, q_val, f_val), daemon=True).start()

    def _dl_thread(self, url, save_path, browser_choice, q_val, f_val):
        self.root.after(0, self._log, f"\n{'='*30}\n🔗 جاري تحميل: {url}")
        
        cmd = [find_ytdlp(), url, "--newline", "--force-ipv4"]
        
        if self.playlist_var.get():
            cmd.extend(["-o", os.path.join(save_path, "%(playlist_index)02d - %(title)s.%(ext)s"), "--yes-playlist"])
        else:
            cmd.extend(["-o", os.path.join(save_path, "%(title)s.%(ext)s"), "--no-playlist"])

        if self.trim_var.get():
            st = self.trim_start.get().strip()
            en = self.trim_end.get().strip()
            cmd.extend(["--download-sections", f"*{st}-{en}", "--force-keyframes-at-cuts"])

        if not self.has_ffmpeg:
            if q_val != "auto": 
                cmd.extend(["-f", f"best[height<={q_val}]"])
        else:
            if f_val == "mp3": 
                cmd.extend(["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3"])
            else:
                if q_val != "auto":
                    cmd.extend(["-f", f"bestvideo[height<={q_val}]+bestaudio/best[height<={q_val}]"])
                if f_val != "auto": 
                    cmd.extend(["--merge-output-format", f_val])

        if self.subtitle_var.get(): cmd.extend(["--write-subs", "--sub-lang", "ar,en"])
        if browser_choice != "بدون (الوضع الافتراضي)": cmd.extend(["--cookies-from-browser", browser_choice])

        ok, downloaded_file = False, ""
        
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.current_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, 
                text=True, encoding="utf-8", errors="replace", startupinfo=si)

            for line in iter(self.current_process.stdout.readline, ''):
                if not line: break
                clean_line = line.strip()
                if not clean_line: continue

                if "Destination:" in clean_line: 
                    downloaded_file = clean_line.split("Destination:", 1)[-1].strip().strip('"')
                elif "Merging formats into" in clean_line: 
                    downloaded_file = clean_line.split("Merging formats into", 1)[-1].strip().strip('"')
                elif "has already been downloaded" in clean_line:
                    downloaded_file = clean_line.split("has already been downloaded")[0].replace("[download]", "").strip().strip('"')

                if ("Deleting original file" in clean_line) or ("[download]" in clean_line and "%" in clean_line):
                    continue

                self.root.after(0, self._log, clean_line)

            self.current_process.wait()
            ok = self.current_process.returncode == 0
        except Exception as ex:
            self.root.after(0, self._log, f"❌ خطأ داخلي: {ex}")
        finally:
            self.current_process = None
            
        self.root.after(0, self._finish_dl, ok, save_path, downloaded_file, url)

    def _stop_download(self):
        self.is_downloading = False
        if self.current_process: self.current_process.terminate()
        self._log("⏹ تم إيقاف التحميل.")

    def _finish_dl(self, ok, save_path, downloaded_file, url):
        try:
            self.is_downloading = False
            self.progress.stop()
            self.download_btn.config(text="⬇  بدء التحميل", state="normal")
            self.stop_btn.config(state="disabled")
            
            file_exists = False
            if downloaded_file:
                try: file_exists = os.path.exists(downloaded_file)
                except: pass

            is_success = ok or file_exists
            
            self.history.append({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "url": url, "status": "✅ اكتمل" if is_success else "❌ فشل"})
            save_history(self.history)
            
            if is_success:
                self.status_lbl.config(text="✅ تم الانتهاء من التحميل بنجاح!", fg=SUCCESS)
                if messagebox.askyesno("نجاح", "تم الانتهاء من التحميل، هل تريد الذهاب لموقع الملف؟", parent=self.root):
                    try:
                        if file_exists: 
                            subprocess.run(['explorer', '/select,', os.path.normpath(downloaded_file)])
                        else: 
                            os.startfile(save_path)
                    except:
                        os.startfile(save_path)
            else:
                self.status_lbl.config(text="❌ فشل التحميل (راجع صندوق السجل لمعرفة السبب).", fg=ERROR)
        except Exception as e:
            self._log(f"❌ خطأ أثناء الإنهاء: {e}")

    # ──────────────────────────────────────
    #  System Tray (خيار الإغلاق الذكي)
    # ──────────────────────────────────────
    def _hide_to_tray(self):
        if TRAY_AVAILABLE and PIL_AVAILABLE:
            self.root.withdraw() 
            self._create_tray()
        else:
            messagebox.showerror("خطأ", "هذه الميزة تتطلب تثبيت مكتبتي pystray و Pillow.\nاكتب في التيرمينال:\npip install pystray pillow")

    def _on_close(self):
        if TRAY_AVAILABLE and PIL_AVAILABLE:
            msg = "هل تريد إخفاء البرنامج بجوار الساعة في الخلفية بدلاً من إغلاقه؟\n\n• (نعم / Yes) : إخفاء البرنامج.\n• (لا / No) : إغلاق نهائي للخروج."
            if self.is_downloading:
                msg = "⚠️ التحميل يعمل حالياً! الإغلاق النهائي سيلغي التحميل.\n\n" + msg
                
            choice = messagebox.askyesnocancel("إغلاق أم إخفاء؟", msg, parent=self.root)
            
            if choice is True:    
                self.root.withdraw() 
                self._create_tray()
            elif choice is False: 
                if self.is_downloading and self.current_process:
                    self.current_process.terminate()
                self.root.destroy()
            else:                 
                return
        else:
            if self.is_downloading:
                if not messagebox.askyesno("تأكيد", "التحميل يعمل.. هل أنت متأكد من الإغلاق؟", parent=self.root):
                    return
            self.root.destroy()

    def _create_tray(self):
        image = Image.new('RGB', (64, 64), color=self.current_accent) 
        menu = (item('إظهار البرنامج', self._show_window), item('إغلاق نهائي', self._quit_tray))
        self.icon = pystray.Icon("ytdlp", image, "YT-DLP Pro Max", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def _show_window(self):
        self.icon.stop()
        self.root.after(0, self.root.deiconify)

    def _quit_tray(self):
        self.icon.stop()
        self.root.after(0, self.root.destroy)

    # ──────────────────────────────────────
    #  General
    # ──────────────────────────────────────
    def _log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_ytdlp(self):
        self._log("🔄 جاري التحديث...")
        threading.Thread(target=lambda: subprocess.run([find_ytdlp(), "-U"], startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW)), daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    YtDlpApp().run()