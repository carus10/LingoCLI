"""
══════════════════════════════════════════════════════════════
  AI TERMINAL ASSISTANT v2.1
  Local Qwen model (LM Studio) powered Windows terminal
  assistant. Real terminal look & feel. Bilingual: EN/TR.
══════════════════════════════════════════════════════════════
"""

import customtkinter as ctk
import requests
import subprocess
import threading
import re
import json
import os
import tkinter.messagebox as msgbox
import tkinter.colorchooser as colorchooser
import tkinter.filedialog as filedialog

# ── Our modules ────────────────────────────────
from komut_veritabani import (
    dinamik_prompt_olustur,
    TEHLIKELI_KALIPLAR,
)
from dil import t

# ──────────────────────────────────────────────
#  GLOBAL SETTINGS
# ──────────────────────────────────────────────
API_URL = "http://localhost:1234/v1/chat/completions"
MODEL   = "local-model"

import sys

if getattr(sys, 'frozen', False):
    # PyInstaller execution
    _APP_DIR = sys._MEIPASS                      # Temporary bundle dir (for icon)
else:
    # Python script execution
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Data files always go to %APPDATA%\LingoCLI\ (safe from exe copy issues)
_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "LingoCLI")
os.makedirs(_DATA_DIR, exist_ok=True)

# Migration: move old files from exe directory to AppData (one-time)
if getattr(sys, 'frozen', False):
    _OLD_DATA_DIR = os.path.dirname(sys.executable)
else:
    _OLD_DATA_DIR = _APP_DIR
for _old_file in ["terminal_ayarlar.json", "workspaces.json"]:
    _old_path = os.path.join(_OLD_DATA_DIR, _old_file)
    _new_path = os.path.join(_DATA_DIR, _old_file)
    if os.path.exists(_old_path) and not os.path.exists(_new_path):
        try:
            import shutil
            shutil.move(_old_path, _new_path)
        except Exception:
            pass

# Settings file path (persistent)
AYAR_DOSYASI = os.path.join(_DATA_DIR, "terminal_ayarlar.json")
WORKSPACES_DOSYASI = os.path.join(_DATA_DIR, "workspaces.json")
HISTORY_DOSYASI = os.path.join(_DATA_DIR, "komut_gecmisi.json")
TEMPLATES_DOSYASI = os.path.join(_DATA_DIR, "sablonlar.json")
ERROR_HISTORY_DOSYASI = os.path.join(_DATA_DIR, "hata_gecmisi.json")
SCRIPTS_DIR = os.path.join(_DATA_DIR, "Scripts")

# Ensure directories exist
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# App icon path (bundled)
ICON_PATH = os.path.join(_APP_DIR, "assest", "icon.ico")

# Terminal fixed colours
SIYAH       = "#0c0c0c"
KOYU_GRI    = "#1a1a1a"
GRI         = "#333333"
ACIK_GRI    = "#888888"
BEYAZ       = "#cccccc"
PARLAK_BEYAZ= "#ffffff"
SARI        = "#f9f1a5"
KIRMIZI     = "#e74856"
FONT        = "Consolas"

# Default customisable colours
VARSAYILAN_KULLANICI_RENK = "#c678dd"
VARSAYILAN_KOMUT_RENK     = "#16c60c"
VARSAYILAN_ACIKLAMA_RENK  = "#888888"
VARSAYILAN_PROMPT_RENK    = "#c678dd"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ──────────────────────────────────────────────
#  SETTINGS LOAD / SAVE
# ──────────────────────────────────────────────

def ayarlari_yukle() -> dict:
    varsayilan = {
        "kullanici_renk": VARSAYILAN_KULLANICI_RENK,
        "komut_renk":     VARSAYILAN_KOMUT_RENK,
        "aciklama_renk":  VARSAYILAN_ACIKLAMA_RENK,
        "prompt_renk":    VARSAYILAN_PROMPT_RENK,
        "dil":            "en",   # Default language: English
    }
    try:
        if os.path.exists(AYAR_DOSYASI):
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                varsayilan.update(kayitli)
    except Exception:
        pass
    return varsayilan

def ayarlari_kaydet(ayarlar: dict):
    try:
        with open(AYAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(ayarlar, f, indent=2)
    except Exception:
        pass

def workspaces_yukle() -> dict:
    varsayilan = {
        "slots": [None, None, None]
    }
    try:
        if os.path.exists(WORKSPACES_DOSYASI):
            with open(WORKSPACES_DOSYASI, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                slots = kayitli.get("slots", [None, None, None])
                if len(slots) < 3:
                     slots.extend([None] * (3 - len(slots)))
                varsayilan["slots"] = slots[:3]
    except Exception:
        pass
    return varsayilan

def workspaces_kaydet(veriler: dict):
    try:
        with open(WORKSPACES_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, indent=2)
    except Exception:
        pass

def gecmis_yukle() -> dict:
    varsayilan = {
        "komutlar": [],  # [{"komut": "...", "zaman": "...", "favori": false}]
        "index": 0
    }
    try:
        if os.path.exists(HISTORY_DOSYASI):
            with open(HISTORY_DOSYASI, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                varsayilan.update(kayitli)
    except Exception:
        pass
    return varsayilan

def gecmis_kaydet(veriler: dict):
    try:
        with open(HISTORY_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, indent=2)
    except Exception:
        pass

def sablonlar_yukle() -> list:
    varsayilan = [
        {"ad": "Git: Setup New Repo", "komut": 'git init; git add .; git commit -m "initial commit"; git branch -M main; git remote add origin {repo_url}; git push -u origin main', "aciklama": "Initialize git and push to a new repo for the first time"},
        {"ad": "Git: Smart Push", "komut": 'git add .; git commit -m "{mesaj}"; git push', "aciklama": "Add, commit and push changes in one go"},
        {"ad": "Git: Undo Last Commit", "komut": "git reset --soft HEAD~1", "aciklama": "Undo last commit but keep changes"},
        {"ad": "Templates: List Files", "komut": 'Get-ChildItem -Path "{yol}" | Select-Object Name, Length, LastWriteTime', "aciklama": "Dosyalari listele"},
    ]
    try:
        if os.path.exists(TEMPLATES_DOSYASI):
            with open(TEMPLATES_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return varsayilan

def sablonlar_kaydet(veriler: list):
    try:
        with open(TEMPLATES_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, indent=2)
    except Exception:
        pass

def hata_gecmisi_yukle() -> list:
    try:
        if os.path.exists(ERROR_HISTORY_DOSYASI):
            with open(ERROR_HISTORY_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def hata_gecmisi_kaydet(veriler: list):
    try:
        with open(ERROR_HISTORY_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, indent=2)
    except Exception:
        pass

# ──────────────────────────────────────────────
#  SECURITY
# ──────────────────────────────────────────────

def tehlike_kontrolu(komut: str) -> tuple[bool, str]:
    for kalip in TEHLIKELI_KALIPLAR:
        if re.search(kalip, komut, re.IGNORECASE):
            return (True, kalip)
    return (False, "")

def tehlike_aciklamasi(kalip: str) -> str:
    aciklamalar = {
        "Remove-Item.*-Recurse.*-Force":  "Bulk force delete",
        "Remove-Item.*C:\\\\Windows":      "Delete Windows system folder",
        "Remove-Item.*C:\\\\Program":      "Delete Program Files",
        "Format-Volume":                   "Disk formatting",
        "Clear-Disk":                      "Disk wipe",
        "diskpart":                        "Disk partitioning tool",
        "Remove-ItemProperty.*HKLM":       "Delete system registry",
        "Set-ItemProperty.*HKLM":          "Modify system registry",
        "reg\\s+delete":                    "Delete registry entry",
        "Remove-LocalUser":                "Delete user account",
        "Disable-LocalUser":               "Disable user account",
        "Set-NetFirewallProfile.*False":    "Disable firewall",
        "Set-MpPreference.*True":           "Disable Windows Defender",
        "Restart-Computer":                 "Restart computer",
        "Stop-Computer":                    "Shut down computer",
        "shutdown":                         "Shut down computer",
        "bcdedit":                          "Boot configuration",
        "Invoke-WebRequest.*Invoke-Expression": "Remote code execution",
        "iex\\s*\\(":                       "Remote code execution",
        "DownloadString":                   "Download code from web",
        "Set-ExecutionPolicy.*Unrestricted": "Remove script security",
    }
    for anahtar, aciklama in aciklamalar.items():
        if re.search(anahtar, kalip, re.IGNORECASE):
            return aciklama
    return "Potentially dangerous operation"

# ──────────────────────────────────────────────
#  TOKEN ESTIMATION SYSTEM
# ──────────────────────────────────────────────
MODEL_CONTEXT     = 4096
SISTEM_BUTCE      = 150
YANIT_BUTCE       = 1024
GUVENLIK_MARJI    = 300
GECMIS_BUTCE      = MODEL_CONTEXT - SISTEM_BUTCE - YANIT_BUTCE - GUVENLIK_MARJI
OZET_TETIK_ESIGI  = int(GECMIS_BUTCE * 0.7)
HAM_KORUMA_SAYISI = 3

def token_tahmin(metin: str) -> int:
    if not metin:
        return 0
    byte_uzunluk = len(metin.encode("utf-8", errors="replace"))
    return int(byte_uzunluk / 3.5)

def gecmis_token_sayisi(gecmis: list) -> int:
    return sum(token_tahmin(m.get("content", "")) for m in gecmis)

# ──────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────

def log_mesaj(mesaj: str, seviye: str = "INFO"):
    """Terminal asistanı için basit loglama."""
    print(f"[{seviye}] {mesaj}")

def modele_sor(kullanici_mesaji: str, gecmis: list = None, ozet: str = "", dil: str = "en", cwd_bilgisi: str = "", active_model: str = None) -> dict:
    target_model = active_model if active_model else MODEL
    prompt = dinamik_prompt_olustur(kullanici_istegi=kullanici_mesaji, dil=dil)
    
    mesajlar = [{"role": "system", "content": prompt}]
    if cwd_bilgisi:
        mesajlar.append({"role": "system", "content": t(dil, "sys_current_dir", d=cwd_bilgisi)})
    if ozet:
        mesajlar.append({"role": "system", "content": t(dil, "sys_context_sum", s=ozet)})
    
    if gecmis:
        mesajlar.extend(gecmis)
    
    mesajlar.append({"role": "user", "content": kullanici_mesaji})
    
    payload = {
        "model": target_model,
        "messages": mesajlar,
        "temperature": 0.1,
        "max_tokens": YANIT_BUTCE,
    }
    
    try:
        yanit = requests.post(API_URL, json=payload, timeout=60)
        yanit.raise_for_status()
        data = yanit.json()
        icerik = data["choices"][0]["message"]["content"]
        return {"durum": "ok", "icerik": icerik}
    except requests.exceptions.ConnectionError:
        log_mesaj("API Connection Error", "ERROR")
        return {"durum": "hata", "mesaj": "connection"}
    except requests.exceptions.Timeout:
        log_mesaj("API Timeout", "ERROR")
        return {"durum": "hata", "mesaj": "timeout"}
    except Exception as e:
        log_mesaj(f"API Unexpected Error: {e}", "ERROR")
        return {"durum": "hata", "mesaj": f"unexpected:{e}"}


def gecmisi_ozetle(mesajlar: list, dil: str = "en", active_model: str = None) -> str:
    target_model = active_model if active_model else MODEL
    satirlar = []
    for m in mesajlar:
        rol = "User" if m["role"] == "user" else "Assistant"
        satirlar.append(f"{rol}: {m['content']}")
    konusma_metni = "\n".join(satirlar)

    prompt = (
        t(dil, "sys_summarize") + 
        " Sadece teknik değişimleri (dosya/klasör işlemleri) belirt.\n\n" + konusma_metni
    )
    
    payload = {
        "model": target_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 150,
    }
    try:
        yanit = requests.post(API_URL, json=payload, timeout=30)
        yanit.raise_for_status()
        return yanit.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log_mesaj(f"Summary failed: {e}", "WARNING")
        basit = [m["content"][:60] for m in mesajlar if m["role"] == "user"]
        return "History: " + "; ".join(basit[-5:])


def yaniti_ayristir(ham_metin: str) -> tuple[str, str]:
    """AI yanıtını JSON olarak ayıklar, hata varsa fallback mekanizmasını kullanır."""
    metin = ham_metin.strip()
    
    # 1. JSON bloğunu bul (Markdown blokları içindeyse bile)
    try:
        # Önce tüm metni deniyoruz (saf JSON gelmiş olabilir)
        data = json.loads(metin)
        return data.get("explain", ""), data.get("content", "")
    except json.JSONDecodeError:
        # Markdown blokları arasındaysa ayıkla
        match = re.search(r"\{.*\}", metin, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data.get("explain", ""), data.get("content", "")
            except:
                pass

    # 2. Fallback: Satır bazlı manuel ayıklama (Etiket bazlı modeller için)
    aciklama = ""
    komut = ""
    metin_temiz = re.sub(r"```[a-zA-Z]*", "", ham_metin).replace("```", "")
    
    current_key = None
    for line in metin_temiz.split("\n"):
        line_upper = line.strip().upper()
        if "AÇIKLAMA:" in line_upper or "DESCRIPTION:" in line_upper:
            current_key = "a"
            aciklama += line.split(":", 1)[-1].strip() + " "
        elif "KOMUT:" in line_upper or "COMMAND:" in line_upper:
            current_key = "k"
            komut += line.split(":", 1)[-1].strip() + " "
        elif current_key == "a":
            aciklama += line.strip() + " "
        elif current_key == "k":
            komut += line.strip() + " "
            
    return aciklama.strip(), komut.strip()


def hatayi_analiz_et(hata_mesaji, basarisiz_komut, dil="en", active_model=None):
    """AI ile hatayı analiz eder ve çözüm önerisi sunar."""
    target_model = active_model if active_model else MODEL
    prompt = (
        f"Sen bir terminal uzmanısın. Kullanıcı şu komutu çalıştırdı: '{basarisiz_komut}' "
        f"ve şu hatayı aldı: '{hata_mesaji}'.\n\n"
        f"Lütfen hatayı {('Türkçe' if dil=='tr' else 'English')} olarak çok kısa açıkla ve "
        f"eğer mümkünse düzeltilmiş komutu 'FIX: [komut]' formatında ver."
    )
    
    payload = {
        "model": target_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    try:
        yanit = requests.post(API_URL, json=payload, timeout=30)
        yanit.raise_for_status()
        return yanit.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log_mesaj(f"Analyze failed: {e}", "WARNING")
        return None


def komutu_calistir(komut: str, hedef_dizin: str = None) -> tuple[bool, str]:
    utf8_on = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        "$OutputEncoding = [System.Text.Encoding]::UTF8; "
    )
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        sonuc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", utf8_on + komut],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30, cwd=hedef_dizin,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        cikti = (sonuc.stdout or "") + (sonuc.stderr or "")
        return (sonuc.returncode == 0, cikti.strip())
    except subprocess.TimeoutExpired:
        return (False, "Command timed out (30s).")
    except Exception as e:
        return (False, f"Command execution failed: {e}")


def hatayi_analiz_et(hata_mesaji: str, basarisiz_komut: str, dil: str = "en", active_model: str = None) -> str:
    """AI kullanarak hatayı analiz et ve öneri sun."""
    target_model = active_model if active_model else MODEL
    
    prompt_en = (
        f"A PowerShell command failed with an error.\n"
        f"Command: {basarisiz_komut}\n"
        f"Error: {hata_mesaji}\n\n"
        f"Provide a BRIEF explanation of the error and ONE concrete fix command.\n"
        f"Format: First line = explanation, Second line = fix command (prefix with FIX:)"
    )
    
    prompt_tr = (
        f"Bir PowerShell komutu hata verdi.\n"
        f"Komut: {basarisiz_komut}\n"
        f"Hata: {hata_mesaji}\n\n"
        f"Hatanın nedenini ve düzeltme komutunu ver.\n"
        f"Format: İlk satır = açıklama, İkinci satır = düzeltme komutu (FIX: ile başla)"
    )
    
    payload = {
        "model": target_model,
        "messages": [{"role": "user", "content": prompt_tr if dil == "tr" else prompt_en}],
        "temperature": 0.1,
        "max_tokens": 200,
    }
    try:
        yanit = requests.post(API_URL, json=payload, timeout=30)
        yanit.raise_for_status()
        return yanit.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log_mesaj(f"Error analysis failed: {e}", "WARNING")
        return ""


# ══════════════════════════════════════════════
#  SETTINGS WINDOW
# ══════════════════════════════════════════════

class KoyuRenkSecici(ctk.CTkToplevel):
    def __init__(self, parent, mevcut_renk, title="Renk Seç"):
        super().__init__(parent)
        self.title(title)
        self.geometry("380x280")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()
        
        self.secilen_renk = mevcut_renk
        
        renkler = [
            "#e74856", "#16c60c", "#f9f1a5", "#3b78ff", "#c678dd", "#00b9d6", 
            "#cccccc", "#888888", "#ff9900", "#ff007f", "#00ffcc", "#8a2be2",
            "#ffffff", "#333333", "#4caf50", "#ff5722"
        ]
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        for i, renk in enumerate(renkler):
            satir = i // 4
            sutun = i % 4
            btn = ctk.CTkButton(frame, text="", width=60, height=40,
                fg_color=renk, hover_color=renk, corner_radius=6,
                command=lambda r=renk: self._renk_secildi(r))
            btn.grid(row=satir, column=sutun, padx=8, pady=8)
            
    def _renk_secildi(self, renk):
        self.secilen_renk = renk
        self.destroy()

class AyarlarPenceresi(ctk.CTkToplevel):

    def __init__(self, parent, ayarlar: dict, kaydet_callback, dil: str = "en"):
        super().__init__(parent)
        self.dil = dil
        self.title(t(dil, "settings_title"))
        self.geometry("450x520")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()

        self.ayarlar = ayarlar.copy()
        self.kaydet_callback = kaydet_callback

        # Title
        ctk.CTkLabel(self, text=t(dil, "settings_colors"),
            font=ctk.CTkFont(family=FONT, size=16, weight="bold"),
            text_color="#cccccc").pack(pady=(20, 16))

        # Colour rows
        self.butonlar = {}
        self._renk_satiri("kullanici_renk", t(dil, "color_user"), t(dil, "color_user_desc"))
        self._renk_satiri("komut_renk",     t(dil, "color_cmd"),  t(dil, "color_cmd_desc"))
        self._renk_satiri("aciklama_renk",  t(dil, "color_desc"), t(dil, "color_desc_desc"))
        self._renk_satiri("prompt_renk",    t(dil, "color_prompt"), t(dil, "color_prompt_desc"))

        # Language selector
        dil_frame = ctk.CTkFrame(self, fg_color="transparent")
        dil_frame.pack(fill="x", padx=24, pady=(16, 4))

        sol = ctk.CTkFrame(dil_frame, fg_color="transparent")
        sol.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(sol, text=t(dil, "lang_label"),
            font=ctk.CTkFont(family=FONT, size=13),
            text_color="#cccccc", anchor="w").pack(anchor="w")
        ctk.CTkLabel(sol, text=t(dil, "lang_desc"),
            font=ctk.CTkFont(family=FONT, size=11),
            text_color="#555555", anchor="w").pack(anchor="w")

        self.dil_var = ctk.StringVar(value=self.ayarlar.get("dil", "en"))
        self.dil_menu = ctk.CTkSegmentedButton(dil_frame,
            values=["English", "Türkçe"],
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#2a2a2a",
            selected_color="#3a3a5a",
            selected_hover_color="#4a4a6a",
            unselected_color="#2a2a2a",
            unselected_hover_color="#3a3a3a",
            text_color="#cccccc",
            corner_radius=4)
        self.dil_menu.set("English" if self.dil_var.get() == "en" else "Türkçe")
        self.dil_menu.pack(side="right", padx=(8, 0))

        # Bottom buttons
        alt = ctk.CTkFrame(self, fg_color="transparent")
        alt.pack(fill="x", padx=24, pady=(24, 16))

        ctk.CTkButton(alt, text=t(dil, "btn_save"),
            font=ctk.CTkFont(family=FONT, size=13),
            width=100, height=36,
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            text_color="#16c60c", corner_radius=4,
            command=self._kaydet).pack(side="left", padx=(0, 8))

        ctk.CTkButton(alt, text=t(dil, "btn_reset"),
            font=ctk.CTkFont(family=FONT, size=13),
            width=100, height=36,
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            text_color="#888888", corner_radius=4,
            command=self._sifirla).pack(side="left", padx=(0, 8))

        ctk.CTkButton(alt, text=t(dil, "btn_cancel_set"),
            font=ctk.CTkFont(family=FONT, size=13),
            width=80, height=36,
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            text_color="#e74856", corner_radius=4,
            command=self.destroy).pack(side="left")

    def _renk_satiri(self, anahtar: str, baslik: str, aciklama: str):
        satir = ctk.CTkFrame(self, fg_color="transparent")
        satir.pack(fill="x", padx=24, pady=4)
        sol = ctk.CTkFrame(satir, fg_color="transparent")
        sol.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(sol, text=baslik,
            font=ctk.CTkFont(family=FONT, size=13),
            text_color="#cccccc", anchor="w").pack(anchor="w")
        ctk.CTkLabel(sol, text=aciklama,
            font=ctk.CTkFont(family=FONT, size=11),
            text_color="#555555", anchor="w").pack(anchor="w")
        renk_btn = ctk.CTkButton(satir, text="  ████  ", width=80, height=28,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color=self.ayarlar[anahtar],
            hover_color=self.ayarlar[anahtar],
            text_color=self.ayarlar[anahtar],
            corner_radius=4, border_width=1, border_color="#444444",
            command=lambda k=anahtar: self._renk_sec(k))
        renk_btn.pack(side="right", padx=(8, 0))
        self.butonlar[anahtar] = renk_btn

    def _renk_sec(self, anahtar: str):
        secici = KoyuRenkSecici(
            self, 
            self.ayarlar[anahtar], 
            "Select Color" if self.dil == "en" else "Renk Seç"
        )
        self.wait_window(secici)
        
        renk = secici.secilen_renk
        if renk:
            self.ayarlar[anahtar] = renk
            btn = self.butonlar[anahtar]
            btn.configure(fg_color=renk, hover_color=renk, text_color=renk)

    def _kaydet(self):
        # Save language selection
        sec = self.dil_menu.get()
        self.ayarlar["dil"] = "en" if sec == "English" else "tr"
        self.kaydet_callback(self.ayarlar)
        self.destroy()

    def _sifirla(self):
        self.ayarlar.update({
            "kullanici_renk": VARSAYILAN_KULLANICI_RENK,
            "komut_renk":     VARSAYILAN_KOMUT_RENK,
            "aciklama_renk":  VARSAYILAN_ACIKLAMA_RENK,
            "prompt_renk":    VARSAYILAN_PROMPT_RENK,
        })
        for anahtar, btn in self.butonlar.items():
            renk = self.ayarlar[anahtar]
            btn.configure(fg_color=renk, hover_color=renk, text_color=renk)

class WorkspacePenceresi(ctk.CTkToplevel):

    def __init__(self, parent, workspaces_data, aktif_index, secim_callback, sil_callback, cikis_callback, dil="en"):
        super().__init__(parent)
        self.title(t(dil, "ws_select"))
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()

        # Title
        ctk.CTkLabel(self, text=t(dil, "ws_btn"),
            font=ctk.CTkFont(family=FONT, size=16, weight="bold"),
            text_color="#cccccc").pack(pady=(16, 12))

        # Slots
        slots = workspaces_data.get("slots", [None, None, None])
        if len(slots) < 3: slots.extend([None]*(3-len(slots)))

        for i in range(3):
            slot = slots[i]
            frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=6)
            frame.pack(fill="x", padx=20, pady=8)

            eski_font = ctk.CTkFont(family=FONT, size=13)
            if slot is None:
                ctk.CTkLabel(frame, text=t(dil, "ws_empty"), font=eski_font, text_color="#555555").pack(side="left", padx=12, pady=12)
                ctk.CTkButton(frame, text=t(dil, "ws_new"), font=eski_font,
                    width=90, height=28, fg_color="#1a3a1a", hover_color="#2a5a2a", text_color="#16c60c",
                    command=lambda idx=i: [self.destroy(), secim_callback(idx)]).pack(side="right", padx=12, pady=12)
            else:
                sol = ctk.CTkFrame(frame, fg_color="transparent")
                sol.pack(side="left", fill="both", expand=True, padx=12, pady=8)
                ek = " [Aktif]" if i == aktif_index else ""
                ctk.CTkLabel(sol, text=f"📂 {slot['isim']}{ek}", font=ctk.CTkFont(family=FONT, size=13, weight="bold"), text_color="#c678dd", anchor="w").pack(anchor="w")
                ctk.CTkLabel(sol, text=slot['yol'], font=ctk.CTkFont(family=FONT, size=10), text_color="#888888", anchor="w").pack(anchor="w")
                
                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(side="right", padx=12)

                ctk.CTkButton(btn_frame, text="Seç" if dil=="tr" else "Select", font=eski_font,
                    width=60, height=28, fg_color="#3b78ff", hover_color="#4b88ff", text_color="#ffffff",
                    command=lambda idx=i: [self.destroy(), secim_callback(idx, mevcut=True)]).pack(side="left", padx=(0, 6))

                ctk.CTkButton(btn_frame, text=t(dil, "ws_clear_btn"), font=ctk.CTkFont(family=FONT, size=11),
                    width=40, height=28, fg_color="#3a1a1a", hover_color="#5a2a2a", text_color="#e74856",
                    command=lambda idx=i: [self.destroy(), sil_callback(idx)]).pack(side="left")

        # Bottom buttons
        alt_frame = ctk.CTkFrame(self, fg_color="transparent")
        alt_frame.pack(pady=16)

        if aktif_index is not None:
            ctk.CTkButton(alt_frame, text=t(dil, "ws_exit"),
                font=ctk.CTkFont(family=FONT, size=12, weight="bold"), width=140, height=32,
                fg_color="#2a2a3a", hover_color="#3a3a5a", text_color="#c678dd", corner_radius=4,
                command=lambda: [self.destroy(), cikis_callback()]).pack(side="left", padx=6)

        ctk.CTkButton(alt_frame, text=t(dil, "btn_cancel_set"),
            font=ctk.CTkFont(family=FONT, size=13), width=80, height=32,
            fg_color="#2a2a2a", hover_color="#3a3a3a", text_color="#cccccc",
            command=self.destroy).pack(side="left", padx=6)


# ══════════════════════════════════════════════
#  MAIN APPLICATION — TERMINAL UI
# ══════════════════════════════════════════════

class AITerminalAsistani(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.ayarlar = ayarlari_yukle()
        self.dil = self.ayarlar.get("dil", "en")

        # Workspace
        self.workspaces_data = workspaces_yukle()
        self.aktif_ws_index = None

        # Dinamik Model Tespiti
        self.model_adi = "..."
        self.model_id = MODEL  # Başlangıçta varsayılan model

        # Command History
        self.komut_gecmisi_data = gecmis_yukle()
        self.komut_gecmisi = self.komut_gecmisi_data.get("komutlar", [])
        self.history_index = -1
        self.history_active = False

        # Templates
        self.sablonlar = sablonlar_yukle()

        # Error History
        self.hata_gecmisi = hata_gecmisi_yukle()

        # Session commands (for script export)
        self.oturum_komutlari = []

        self.title(t(self.dil, "app_title"))
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(fg_color=SIYAH)
        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)
            self.after(200, lambda: self.iconbitmap(ICON_PATH))

        # Smart memory system
        self.gecmis = []
        self.gecmis_ozet = ""
        self.toplam_mesaj = 0
        self.ozetleme_sayisi = 0

        # UI
        self._baslik_cubugu()
        self._terminal_alani()
        self._giris_satiri()
        self._ortala()

        # Dinamik Model Tespiti başlat
        self.after(500, self._dinamik_model_tespit_et)

        self._hosgeldin_yaz()

        # Kapanırken workspace hafızasını kaydet
        self.protocol("WM_DELETE_WINDOW", self._uygulama_kapat)

    def _ortala(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ──────────────────────────────────────────
    #  UI LAYOUT
    # ──────────────────────────────────────────

    def _baslik_cubugu(self):
        bar = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=0, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text=t(self.dil, "bar_title"),
            font=ctk.CTkFont(family=FONT, size=12),
            text_color=ACIK_GRI).pack(side="left", padx=8)

        # Workspace button
        self.ws_btn = ctk.CTkButton(bar, text=t(self.dil, "ws_btn"),
            width=100, height=24,
            font=ctk.CTkFont(family=FONT, size=11, weight="bold"),
            fg_color="#1a1e3a", hover_color="#2a2e4a",
            text_color="#c678dd", corner_radius=4,
            command=self._workspace_menusu_ac)
        self.ws_btn.pack(side="left", padx=4)

        # Templates button
        self.templates_btn = ctk.CTkButton(bar, text=t(self.dil, "templates_btn"),
            width=100, height=24,
            font=ctk.CTkFont(family=FONT, size=11),
            fg_color="#1a2a1a", hover_color="#2a3a2a",
            text_color="#16c60c", corner_radius=4,
            command=self._sablonlar_penceresi_ac)
        self.templates_btn.pack(side="left", padx=4)

        self.script_btn = ctk.CTkButton(bar, text=t(self.dil, "script_save"),
            width=100, height=24,
            font=ctk.CTkFont(family=FONT, size=10),
            fg_color="#2a2a1a", hover_color="#3a3a2a",
            text_color=SARI, corner_radius=4,
            command=self._script_olarak_kaydet)
        self.script_btn.pack(side="left", padx=2)

        # Script Run button
        self.script_run_btn = ctk.CTkButton(bar, text=t(self.dil, "script_run"),
            width=100, height=24,
            font=ctk.CTkFont(family=FONT, size=10),
            fg_color="#1a2a3a", hover_color="#2a3a4a",
            text_color="#61afef", corner_radius=4,
            command=self._script_dosyasi_yukle)
        self.script_run_btn.pack(side="left", padx=2)

        # Memory progress bar
        hafiza_frame = ctk.CTkFrame(bar, fg_color="transparent", width=180)
        hafiza_frame.pack(side="left", padx=(12, 0))
        hafiza_frame.pack_propagate(False)

        self.hafiza_lbl = ctk.CTkLabel(hafiza_frame,
            text=f"{t(self.dil, 'memory')}: 0%",
            font=ctk.CTkFont(family=FONT, size=10),
            text_color=ACIK_GRI)
        self.hafiza_lbl.pack(side="left", padx=(0, 6))

        self.hafiza_bar = ctk.CTkProgressBar(hafiza_frame,
            width=90, height=8, corner_radius=4,
            fg_color="#2a2a2a", progress_color="#16c60c", border_width=0)
        self.hafiza_bar.pack(side="left", pady=0)
        self.hafiza_bar.set(0)

        # Settings button
        ctk.CTkButton(bar, text="⚙",
            width=28, height=24,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent", hover_color="#333333",
            text_color=ACIK_GRI, corner_radius=4,
            command=self._ayarlari_ac).pack(side="right", padx=4)

        # Info button
        ctk.CTkButton(bar, text="ⓘ",
            width=28, height=24,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent", hover_color="#333333",
            text_color=ACIK_GRI, corner_radius=4,
            command=self._bilgi_goster).pack(side="right", padx=0)

        # New Session button
        self.yeni_oturum_btn = ctk.CTkButton(bar, text=t(self.dil, "new_session"),
            width=100, height=24,
            font=ctk.CTkFont(family=FONT, size=11),
            fg_color="transparent", hover_color="#333333",
            text_color=ACIK_GRI, corner_radius=4,
            command=self._yeni_oturum)
        self.yeni_oturum_btn.pack(side="right", padx=4)

        self.durum_lbl = ctk.CTkLabel(bar, text=t(self.dil, "ready"),
            font=ctk.CTkFont(family=FONT, size=11),
            text_color=self.ayarlar["komut_renk"])
        self.durum_lbl.pack(side="right", padx=8)

        # Model & Context info label
        self.model_bilgi_lbl = ctk.CTkLabel(bar,
            text=f"[{self.model_adi}] {MODEL_CONTEXT}",
            font=ctk.CTkFont(family=FONT, size=11, weight="bold"),
            text_color="#c678dd")
        self.model_bilgi_lbl.pack(side="right", padx=(0, 12))

    def _terminal_alani(self):
        self.terminal = ctk.CTkTextbox(self,
            font=ctk.CTkFont(family=FONT, size=13),
            fg_color=SIYAH, text_color=BEYAZ,
            corner_radius=0, border_width=0,
            state="disabled", wrap="word",
            activate_scrollbars=True)
        self.terminal.pack(fill="both", expand=True, padx=0, pady=0)
        self._renk_tagleri_guncelle()

    def _renk_tagleri_guncelle(self):
        tb = self.terminal._textbox
        tb.tag_configure("sari",      foreground=SARI)


    # ──────────────────────────────────────────
    #  NEW FEATURE METHODS
    # ──────────────────────────────────────────

    def _history_onceki(self, event=None):
        """Ok tuşu ile önceki komutlara git."""
        if not self.komut_gecmisi:
            return
        if self.history_index == -1:
            self.history_index = 0
        elif self.history_index < len(self.komut_gecmisi) - 1:
            self.history_index += 1
        
        self.giris.delete(0, "end")
        self.giris.insert(0, self.komut_gecmisi[self.history_index]["komut"])
        self.history_active = True

    def _history_sonraki(self, event=None):
        """Ok tuşu ile sonraki komutlara git."""
        if not self.history_active or self.history_index == -1:
            return
        
        if self.history_index > 0:
            self.history_index -= 1
            self.giris.delete(0, "end")
            self.giris.insert(0, self.komut_gecmisi[self.history_index]["komut"])
        else:
            self.history_index = -1
            self.history_active = False
            self.giris.delete(0, "end")

    def _history_arama_ac(self):
        """Komut geçmişinde arama penceresi aç."""
        HistoryPenceresi(self, self.komut_gecmisi, self._history_komut_kullan, self.dil)

    def _history_komut_kullan(self, komut):
        """Geçmişten seçilen komutu kullan."""
        self.giris.delete(0, "end")
        self.giris.insert(0, komut)
        self.giris.focus_set()

    def _sablonlar_penceresi_ac(self):
        """Şablonlar penceresini aç."""
        SablonPenceresi(self, self.sablonlar, self._sablon_kullan, self._sablon_kaydet, self.dil)

    def _sablon_kullan(self, sablon):
        """Şablonu kullan. Eğer {parametre} içeriyorsa pencere aç."""
        komut = sablon["komut"]
        parametreler = re.findall(r"\{(.*?)\}", komut)
        
        if parametreler:
            TemplateParameterPenceresi(self, sablon, self._sablon_uygula, self.dil)
        else:
            self._sablon_uygula(komut, sablon.get("ad", "Template"))

    def _sablon_uygula(self, final_komut, ad):
        self.giris.focus_set()
        
        # Check for multi-step script
        if ";" in final_komut:
            komutlar = [c.strip() for c in final_komut.split(";") if c.strip()]
            self._terminale_yaz_satir(t(self.dil, "flow_multi_step", n=ad), "gri")
            self._script_modu_baslat(komutlar)
        else:
            self.giris.delete(0, "end")
            self.giris.insert(0, final_komut)
            self._terminale_yaz_satir(f"  Template loaded: {ad}", "gri")

    def _sablon_kaydet(self, sablon):
        """Yeni şablon kaydet."""
        self.sablonlar.append(sablon)
        sablonlar_kaydet(self.sablonlar)

    def _hata_analiz_butonu_goster(self, hata_mesaji):
        """Hata analizi için buton göster."""
        # Son komutu bul
        if not self.oturum_komutlari:
            return
        son_komut = self.oturum_komutlari[-1]
        
        self.terminal.configure(state="normal")
        analiz_frame = ctk.CTkFrame(self.terminal._textbox, fg_color="transparent", height=34)
        
        ctk.CTkButton(analiz_frame, text=t(self.dil, "error_analyze"),
            width=140, height=26,
            font=ctk.CTkFont(family=FONT, size=11),
            fg_color="#2a2a3a", hover_color="#3a3a5a",
            text_color="#c678dd", corner_radius=4,
            border_width=1, border_color="#3a3a5a",
            command=lambda: self._hata_analiz_et(hata_mesaji, son_komut)).pack(side="left")
        
        self.terminal._textbox.window_create("end", window=analiz_frame)
        self.terminal._textbox.insert("end", "\n")
        self.terminal.configure(state="disabled")
        self.terminal._textbox.see("end")

    def _hata_analiz_et(self, hata_mesaji, basarisiz_komut):
        """AI ile hatayı analiz et."""
        self._terminale_yaz_satir(t(self.dil, "error_analyzing"), "gri")
        self._yukleniyor(True)
        
        threading.Thread(target=self._hata_analiz_arkaplan,
                        args=(hata_mesaji, basarisiz_komut), daemon=True).start()

    def _hata_analiz_arkaplan(self, hata_mesaji, basarisiz_komut):
        analiz = hatayi_analiz_et(hata_mesaji, basarisiz_komut, self.dil, self.model_id)
        self.after(0, self._hata_analiz_goster, analiz, basarisiz_komut)

    def _hata_analiz_goster(self, analiz, basarisiz_komut):
        self._yukleniyor(False)
        
        if not analiz:
            self._terminale_yaz_satir(t(self.dil, "error_no_fix"), "kirmizi")
            return
        
        # Parse analysis
        satirlar = analiz.split("\n")
        aciklama = satirlar[0] if satirlar else ""
        fix_cmd = ""
        
        for satir in satirlar:
            if satir.upper().startswith("FIX:"):
                fix_cmd = satir[4:].strip()
                break
        
        self._terminale_yaz_satir(f"{t(self.dil, 'error_suggestion')} {aciklama}", "sari")
        if fix_cmd:
            self._terminale_yaz_satir(f"{t(self.dil, 'error_fix')} {fix_cmd}", "komut")
            # Save to error history
            self.hata_gecmisi.append({
                "komut": basarisiz_komut,
                "hata": "Error occurred",
                "cozum": fix_cmd,
                "zaman": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self.hata_gecmisi = self.hata_gecmisi[-50:]
            hata_gecmisi_kaydet(self.hata_gecmisi)

    def _script_olarak_kaydet(self):
        """Oturumu PowerShell script olarak kaydet."""
        if not self.oturum_komutlari:
            self._terminale_yaz_satir("  No commands to export", "gri")
            return
        
        # Basit file dialog
        dosya_yolu = filedialog.asksaveasfilename(
            title=t(self.dil, "script_save"),
            defaultextension=".ps1",
            initialdir=SCRIPTS_DIR,
            filetypes=[("PowerShell Script", "*.ps1"), ("All Files", "*.*")],
            initialfile=f"lingocli_session_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.ps1"
        )
        
        if not dosya_yolu:
            return
        
        try:
            with open(dosya_yolu, "w", encoding="utf-8") as f:
                f.write("# LingoCLI Generated Script\n")
                f.write(f"# Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*60 + "\n\n")
                
                # Fixed: Chronological order (first to last)
                for i, komut in enumerate(self.oturum_komutlari, 1):
                    f.write(f"# Step {i}\n")
                    f.write(f"{komut}\n\n")
            
            self._terminale_yaz_satir(t(self.dil, "script_saved", f=dosya_yolu), "komut")
        except Exception as e:
            self._terminale_yaz_satir(f"  Failed to save script: {e}", "kirmizi")

    def _script_dosyasi_yukle(self):
        """Bir .ps1 dosyası yükler ve script modunu başlatır."""
        dosya_yolu = filedialog.askopenfilename(
            title="Select PowerShell Script",
            initialdir=SCRIPTS_DIR,
            filetypes=[("PowerShell Script", "*.ps1"), ("All Files", "*.*")]
        )
        if not dosya_yolu: return
        
        try:
            komutlar = []
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#"):
                        komutlar.append(satir)
            
            if komutlar:
                self._script_modu_baslat(komutlar)
            else:
                self._terminale_yaz_satir("  Selected script contains no commands.", "sari")
        except Exception as e:
            self._terminale_yaz_satir(f"  Error loading script: {e}", "kirmizi")
    #  SCRIPT MODE RUNNER
    # ──────────────────────────────────────────

    def _script_modu_baslat(self, komutlar):
        """Birden fazla komutu sırayla ve onaylı çalıştırır."""
        if not komutlar: return
        self._terminale_yaz_satir("\n" + "═"*20 + f" {t(self.dil, 'script_mode_title')} " + "═"*20, "sari")
        self._script_index = 0
        self._script_komutlar = komutlar
        self._script_siradaki_adim()

    def _script_siradaki_adim(self):
        if self._script_index >= len(self._script_komutlar):
            self._terminale_yaz_satir("═"*20 + f" {t(self.dil, 'script_mode_finished')} " + "═"*20 + "\n", "sari")
            return

        komut = self._script_komutlar[self._script_index]
        self._terminale_yaz(f"\n[{self._script_index+1}/{len(self._script_komutlar)}] ", "gri")
        self._terminale_yaz(t(self.dil, "script_mode_next", c=komut), "komut")
        
        # Onay butonu terminalin içine
        self.terminal.configure(state="normal")
        cmd_frame = ctk.CTkFrame(self.terminal._textbox, fg_color="transparent", height=34)
        
        def run_it():
            cmd_frame.destroy()
            self._history_ekle(komut)
            self._yukleniyor(True)
            threading.Thread(target=self._komut_calistir_arkaplan, args=(komut,), daemon=True).start()
            self._script_callback = self._script_bitti
            
        def skip_it():
            cmd_frame.destroy()
            self._script_index += 1
            self._script_siradaki_adim()

        def stop_it():
            cmd_frame.destroy()
            self._terminale_yaz_satir("\n  " + t(self.dil, "script_mode_aborted"), "kirmizi")

        ctk.CTkButton(cmd_frame, text=t(self.dil, "script_mode_run"), width=70, height=24, fg_color="#1a3a1a", command=run_it).pack(side="left", padx=4)
        ctk.CTkButton(cmd_frame, text=t(self.dil, "script_mode_skip"), width=70, height=24, fg_color="#2a2a2a", command=skip_it).pack(side="left", padx=4)
        ctk.CTkButton(cmd_frame, text=t(self.dil, "script_mode_stop"), width=70, height=24, fg_color="#3a1a1a", command=stop_it).pack(side="left", padx=4)
        
        self.terminal._textbox.window_create("end", window=cmd_frame)
        self.terminal._textbox.insert("end", "\n")
        self.terminal.configure(state="disabled")
        self.terminal._textbox.see("end")

    def _script_bitti(self, success):
        if not success:
            self._terminale_yaz_satir("  " + t(self.dil, "script_mode_step_failed"), "kirmizi")
            # Extra option for AI fix within script mode
            self.terminal.configure(state="normal")
            fix_frame = ctk.CTkFrame(self.terminal._textbox, fg_color="transparent", height=34)
            
            def continue_anyway():
                fix_frame.destroy()
                self._script_index += 1
                self._script_siradaki_adim()
                
            def ai_fix_script():
                fix_frame.destroy()
                # Get last failure output
                if not self.oturum_komutlari: return
                last_cmd = self.oturum_komutlari[-1]
                self._terminale_yaz_satir(t(self.dil, "error_analyzing"), "gri")
                self._yukleniyor(True)
                
                def _callback(analiz):
                    self._yukleniyor(False)
                    if not analiz: return
                    
                    fix_cmd = ""
                    for satir in analiz.split("\n"):
                        if satir.upper().startswith("FIX:"):
                            fix_cmd = satir[4:].strip()
                            break
                    
                    if fix_cmd:
                        self._terminale_yaz_satir(f"  AI Suggestion found. Updating step...", "sari")
                        self._script_komutlar[self._script_index] = fix_cmd
                        self._script_siradaki_adim()
                    else:
                        self._terminale_yaz_satir("  AI couldn't find a fix.", "kirmizi")

                threading.Thread(target=lambda: _callback(hatayi_analiz_et("Command failed", last_cmd, self.dil, self.model_id)), daemon=True).start()

            ctk.CTkButton(fix_frame, text="Ask AI to Fix & Retry", fg_color="#c678dd", command=ai_fix_script).pack(side="left", padx=4)
            ctk.CTkButton(fix_frame, text="Continue anyway", fg_color="#2a2a2a", command=continue_anyway).pack(side="left", padx=4)
            
            self.terminal._textbox.window_create("end", window=fix_frame)
            self.terminal._textbox.insert("end", "\n")
            self.terminal.configure(state="disabled")
            self.terminal._textbox.see("end")
        else:
            self._script_index += 1
            self.after(500, self._script_siradaki_adim)

    def _script_dosyasi_yukle(self):
        """Kaydedilmiş bir script dosyasını açar ve çalıştırır."""
        dosya_yolu = filedialog.askopenfilename(
            title="Load Terminal Script",
            initialdir=SCRIPTS_DIR,
            filetypes=[("PowerShell Script", "*.ps1"), ("All Files", "*.*")]
        )
        if not dosya_yolu: return
        
        try:
            komutlar = []
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#"):
                        komutlar.append(satir)
            
            if komutlar:
                self._script_modu_baslat(komutlar)
            else:
                self._terminale_yaz_satir("  Selected script contains no commands.", "sari")
        except Exception as e:
            self._terminale_yaz_satir(f"  Error loading script: {e}", "kirmizi")
        tb.tag_configure("kirmizi",   foreground=KIRMIZI)
        tb.tag_configure("gri",       foreground=ACIK_GRI)
        tb.tag_configure("beyaz",     foreground=BEYAZ)
        tb.tag_configure("pbeyaz",    foreground=PARLAK_BEYAZ)
        tb.tag_configure("koyu_gri",  foreground=GRI)

    def _giris_satiri(self):
        alt = ctk.CTkFrame(self, fg_color=KOYU_GRI, corner_radius=0, height=44)
        alt.pack(fill="x")
        alt.pack_propagate(False)

        self.prompt_lbl = ctk.CTkLabel(alt, text=self._prompt_metni_al(),
            font=ctk.CTkFont(family=FONT, size=14, weight="bold"),
            text_color=self.ayarlar["prompt_renk"])
        self.prompt_lbl.pack(side="left", padx=(12, 4))

        self.giris = ctk.CTkEntry(alt,
            font=ctk.CTkFont(family=FONT, size=14),
            fg_color=KOYU_GRI, text_color=PARLAK_BEYAZ,
            border_width=0, corner_radius=0,
            placeholder_text=t(self.dil, "placeholder"),
            placeholder_text_color=GRI)
        self.giris.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.giris.bind("<Return>", lambda e: self._gonder())
        self.giris.bind("<Up>", self._history_onceki)
        self.giris.bind("<Down>", self._history_sonraki)
        self.giris.bind("<Control-k>", lambda e: self._history_arama_ac())
        self.giris.bind("<Control-t>", lambda e: self._sablonlar_penceresi_ac())
        self.giris.focus_set()

    # ──────────────────────────────────────────
    #  TERMINAL WRITE HELPERS
    # ──────────────────────────────────────────

    def _terminale_yaz_satir(self, metin: str, renk_veya_tag: str = "beyaz"):
        tag = self._tag_cozumle(renk_veya_tag)
        self.terminal.configure(state="normal")
        self.terminal._textbox.insert("end", metin + "\n", tag)
        self.terminal.configure(state="disabled")
        self.terminal._textbox.see("end")

    def _terminale_yaz(self, metin: str, renk_veya_tag: str = "beyaz"):
        tag = self._tag_cozumle(renk_veya_tag)
        self.terminal.configure(state="normal")
        self.terminal._textbox.insert("end", metin, tag)
        self.terminal.configure(state="disabled")
        self.terminal._textbox.see("end")

    def _tag_cozumle(self, renk: str) -> str:
        bilinen = {"kullanici","komut","aciklama","prompt","sari","kirmizi","gri","beyaz","pbeyaz","koyu_gri"}
        if renk in bilinen:
            return renk
        hex_map = {
            SARI: "sari", KIRMIZI: "kirmizi", ACIK_GRI: "gri",
            BEYAZ: "beyaz", PARLAK_BEYAZ: "pbeyaz", GRI: "koyu_gri",
        }
        if renk in hex_map:
            return hex_map[renk]
        if renk == self.ayarlar["kullanici_renk"]: return "kullanici"
        if renk == self.ayarlar["komut_renk"]:     return "komut"
        if renk == self.ayarlar["aciklama_renk"]:  return "aciklama"
        if renk == self.ayarlar["prompt_renk"]:    return "prompt"
        return "beyaz"

    # ──────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────

    def _gonder(self):
        istek = self.giris.get().strip()
        if not istek:
            return
        self._terminale_yaz(self._prompt_metni_al() + " ", "prompt")
        self._terminale_yaz_satir(istek, "kullanici")
        self.giris.delete(0, "end")
        
        # Add to command history
        import datetime
        yeni_komut = {
            "komut": istek,
            "zaman": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "favori": False
        }
        self.komut_gecmisi.insert(0, yeni_komut)
        self.komut_gecmisi = self.komut_gecmisi[:100]  # Keep only last 100
        self.komut_gecmisi_data["komutlar"] = self.komut_gecmisi
        gecmis_kaydet(self.komut_gecmisi_data)
        self.history_index = -1
        
        self._yukleniyor(True)
        gecmis_kopya = self.gecmis.copy()
        ozet_kopya = self.gecmis_ozet
        threading.Thread(target=self._api_sor, args=(istek, gecmis_kopya, ozet_kopya),
                         daemon=True).start()

    def _api_sor(self, istek: str, gecmis: list, ozet: str):
        # Workspace cwd bilgisini modele ilet
        cwd_bilgisi = ""
        if self.aktif_ws_index is not None:
            slot = self.workspaces_data["slots"][self.aktif_ws_index]
            if slot and "yol" in slot:
                cwd_bilgisi = slot["yol"]
        
        sonuc = modele_sor(istek, gecmis, ozet, dil=self.dil, cwd_bilgisi=cwd_bilgisi, active_model=self.model_id)
        self.after(0, self._yanit_geldi, sonuc, istek)

    def _yanit_geldi(self, sonuc: dict, kullanici_istegi: str = ""):
        self._yukleniyor(False)

        if sonuc["durum"] == "hata":
            hata_key = sonuc["mesaj"]
            if hata_key == "connection":
                msg = t(self.dil, "err_connection")
            elif hata_key == "timeout":
                msg = t(self.dil, "err_timeout")
            else:
                msg = t(self.dil, "err_unexpected") + " " + hata_key.replace("unexpected:", "")
            self._terminale_yaz_satir(f"{t(self.dil, 'err_prefix')} {msg}", "kirmizi")
            self._terminale_yaz_satir("", "beyaz")
            return

        aciklama, komut = yaniti_ayristir(sonuc["icerik"])

        # Smart memory management
        if kullanici_istegi:
            self.gecmis.append({"role": "user", "content": kullanici_istegi})
            self.gecmis.append({"role": "assistant", "content": sonuc["icerik"]})
            self.toplam_mesaj += 1

            ham_tokenlar = gecmis_token_sayisi(self.gecmis)
            ozet_tokenlar = token_tahmin(self.gecmis_ozet)
            toplam = ham_tokenlar + ozet_tokenlar

            if toplam > OZET_TETIK_ESIGI and len(self.gecmis) > HAM_KORUMA_SAYISI * 2:
                koruma = HAM_KORUMA_SAYISI * 2
                ozetlenecek = self.gecmis[:-koruma]
                korunan = self.gecmis[-koruma:]

                self._terminale_yaz_satir(
                    t(self.dil, "mem_optimizing", n=len(ozetlenecek)//2), "gri")

                if self.gecmis_ozet:
                    ozet_mesaj = {"role": "assistant",
                                 "content": f"Previous summary: {self.gecmis_ozet}"}
                    ozetlenecek = [ozet_mesaj] + ozetlenecek

                threading.Thread(
                    target=self._ozetleme_yap,
                    args=(ozetlenecek, korunan),
                    daemon=True).start()

            self._hafiza_guncelle()

        if aciklama:
            self._terminale_yaz_satir(f"  # {aciklama}", "aciklama")

        if komut:
            self._terminale_yaz_satir(f"  > {komut}", "komut")
            tehlikeli, kalip = tehlike_kontrolu(komut)
            if tehlikeli:
                self._terminale_yaz_satir(
                    f"{t(self.dil, 'danger_prefix')} {tehlike_aciklamasi(kalip)}", "sari")
            self._onay_goster(komut)
        else:
            self._terminale_yaz_satir(t(self.dil, "cmd_not_generated"), "kirmizi")
            self._terminale_yaz_satir("", "beyaz")

    # ──────────────────────────────────────────
    #  COMMAND EXECUTION
    # ──────────────────────────────────────────

    def _onay_goster(self, komut: str):
        self.terminal.configure(state="normal")
        self._onay_frame = ctk.CTkFrame(self.terminal._textbox,
            fg_color="transparent", height=34)

        ctk.CTkButton(self._onay_frame, text=t(self.dil, "btn_run"),
            width=90, height=26,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            text_color="#16c60c", corner_radius=4,
            border_width=1, border_color="#2a5a2a",
            command=lambda: self._onayla(komut)).pack(side="left", padx=(0, 8))

        ctk.CTkButton(self._onay_frame, text=t(self.dil, "btn_cancel"),
            width=70, height=26,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            text_color=KIRMIZI, corner_radius=4,
            border_width=1, border_color="#5a2a2a",
            command=self._iptal).pack(side="left")

        self.terminal._textbox.window_create("end", window=self._onay_frame)
        self.terminal._textbox.insert("end", "\n")
        self.terminal.configure(state="disabled")
        self.terminal._textbox.see("end")

    def _onayla(self, komut: str):
        if hasattr(self, '_onay_frame') and self._onay_frame.winfo_exists():
            self._onay_frame.destroy()

        tehlikeli, kalip = tehlike_kontrolu(komut)
        if tehlikeli:
            cevap = msgbox.askyesno(
                t(self.dil, "danger_title"),
                t(self.dil, "danger_body", d=tehlike_aciklamasi(kalip), c=komut),
                icon="warning"
            )
            if not cevap:
                self._terminale_yaz_satir(t(self.dil, "security_cancel"), "sari")
                self._terminale_yaz_satir("", "beyaz")
                return

        # Add to session commands for script export
        self.oturum_komutlari.append(komut)

        self._terminale_yaz_satir(t(self.dil, "running"), "gri")
        self._yukleniyor(True)

        threading.Thread(target=self._komut_calistir_arkaplan, args=(komut,), daemon=True).start()

    def _komut_calistir_arkaplan(self, komut: str):
        # Cwd belirleme
        hedef_klasor = None
        if self.aktif_ws_index is not None:
            slot = self.workspaces_data["slots"][self.aktif_ws_index]
            if slot and "yol" in slot:
                hedef_klasor = slot["yol"]
                
        basarili, cikti = komutu_calistir(komut, hedef_dizin=hedef_klasor)
        self.after(0, self._komut_tamamlandi, basarili, cikti)

    def _komut_tamamlandi(self, basarili: bool, cikti: str):
        self._yukleniyor(False)
        if cikti:
            satirlar = cikti.split("\n")
            max_satir = 20
            for s in satirlar[:max_satir]:
                self._terminale_yaz_satir(f"  {s}", "pbeyaz")
            if len(satirlar) > max_satir:
                self._terminale_yaz_satir(
                    t(self.dil, "lines_more", n=len(satirlar) - max_satir), "gri")

        if basarili:
            self._terminale_yaz_satir(t(self.dil, "success"), "komut")
        else:
            self._terminale_yaz_satir(t(self.dil, "cmd_error"), "kirmizi")
            # Auto-detect error and show analysis
            self._hata_analiz_butonu_goster(cikti)
            
        if hasattr(self, "_script_callback") and self._script_callback:
            tmp = self._script_callback
            self._script_callback = None
            tmp(basarili)
            
        self._terminale_yaz_satir("", "beyaz")

    def _iptal(self):
        if hasattr(self, '_onay_frame') and self._onay_frame.winfo_exists():
            self._onay_frame.destroy()
        self._terminale_yaz_satir(t(self.dil, "cancelled"), "kirmizi")
        self._terminale_yaz_satir("", "beyaz")

    # ──────────────────────────────────────────
    #  SETTINGS
    # ──────────────────────────────────────────

    def _ayarlari_ac(self):
        AyarlarPenceresi(self, self.ayarlar, self._ayarlar_kaydedildi, self.dil)

    def _ayarlar_kaydedildi(self, yeni_ayarlar: dict):
        eski_dil = self.dil
        self.ayarlar = yeni_ayarlar
        self.dil = yeni_ayarlar.get("dil", "en")
        ayarlari_kaydet(yeni_ayarlar)

        self._renk_tagleri_guncelle()
        self.prompt_lbl.configure(text_color=self.ayarlar["prompt_renk"])
        self.durum_lbl.configure(text_color=self.ayarlar["komut_renk"])

        # If language changed, refresh all UI text
        if eski_dil != self.dil:
            self._dil_degistir()

        self._terminale_yaz_satir(t(self.dil, "settings_saved"), "komut")

    def _dil_degistir(self):
        """Refresh all UI labels when language changes."""
        self.title(t(self.dil, "app_title"))
        self.durum_lbl.configure(text=t(self.dil, "ready"))
        self.yeni_oturum_btn.configure(text=t(self.dil, "new_session"))
        self.ws_btn.configure(text=t(self.dil, "ws_btn"))
        self.prompt_lbl.configure(text=self._prompt_metni_al())
        self.giris.configure(placeholder_text=t(self.dil, "placeholder"))
        self._hafiza_guncelle()

    def _uygulama_kapat(self):
        """Uygulama kapanırken workspace hafızasını kaydet."""
        self._mevcut_oturumunu_kaydet()
        self.destroy()

    # ──────────────────────────────────────────
    #  SESSION & INFO
    # ──────────────────────────────────────────

    def _hosgeldin_yaz(self):
        d = self.dil
        self._terminale_yaz_satir(t(d, "welcome_title"), self.ayarlar["komut_renk"])
        self._terminale_yaz_satir(t(d, "welcome_model", ctx=MODEL_CONTEXT, model=getattr(self, 'model_id', 'Qwen 2.5')), ACIK_GRI)
        self._terminale_yaz_satir(t(d, "welcome_memory"), ACIK_GRI)
        self._terminale_yaz_satir("─" * 70, GRI)
        self._terminale_yaz_satir(t(d, "welcome_hint"), ACIK_GRI)

    def _yeni_oturum(self, yaz=True):
        self._mevcut_oturumunu_kaydet()

        self.gecmis.clear()
        self.gecmis_ozet = ""
        self.toplam_mesaj = 0
        self.ozetleme_sayisi = 0
        self.oturum_komutlari.clear()  # Clear session commands
        self.terminal.configure(state="normal")
        self.terminal._textbox.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self._hosgeldin_yaz()
        if yaz:
            self._terminale_yaz_satir(t(self.dil, "session_started"), "komut")
        self._hafiza_guncelle()

    def _prompt_metni_al(self):
        if hasattr(self, "aktif_ws_index") and self.aktif_ws_index is not None:
            slot = self.workspaces_data["slots"][self.aktif_ws_index]
            if slot:
                return f"{slot['isim']} >"
        return t(self.dil, "prompt_prefix")

    def _workspace_menusu_ac(self):
        WorkspacePenceresi(self, self.workspaces_data, self.aktif_ws_index, self._workspace_secildi, self._workspace_sil, self._workspace_cikis, self.dil)

    def _workspace_cikis(self):
        """Aktif workspace'ten çıkıp varsayılan moda dön."""
        self._mevcut_oturumunu_kaydet()
        self.aktif_ws_index = None
        self.gecmis.clear()
        self.gecmis_ozet = ""
        self.toplam_mesaj = 0
        self.ozetleme_sayisi = 0
        self.terminal.configure(state="normal")
        self.terminal._textbox.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self._hosgeldin_yaz()
        self._terminale_yaz_satir(t(self.dil, "ws_default"), "komut")
        self.prompt_lbl.configure(text=self._prompt_metni_al())
        self._hafiza_guncelle()

    def _workspace_secildi(self, index: int, mevcut=False):
        if not mevcut:
            klasor = filedialog.askdirectory(title=t(self.dil, "ws_select"))
            if not klasor: return
            # Normalize path separators for Windows
            klasor = os.path.normpath(klasor)
            isim = os.path.basename(klasor) or klasor
            self.workspaces_data["slots"][index] = {
                "isim": isim,
                "yol": klasor,
                "gecmis": [],
                "gecmis_ozet": "",
                "toplam_mesaj": 0,
                "ozetleme_sayisi": 0
            }
            workspaces_kaydet(self.workspaces_data)

        # Dizin hala var mı kontrol et
        secili = self.workspaces_data["slots"][index]
        if secili and not os.path.isdir(secili.get("yol", "")):
            self._terminale_yaz_satir(t(self.dil, "ws_err_dir", d=secili.get("yol", "?")), "kirmizi")
            return

        self._mevcut_oturumunu_kaydet()

        self.aktif_ws_index = index
        
        # Load memory (KOPYA al, referans değil — JSON verisini korumak için)
        self.gecmis = list(secili.get("gecmis", []))
        self.gecmis_ozet = secili.get("gecmis_ozet", "")
        self.toplam_mesaj = secili.get("toplam_mesaj", 0)
        self.ozetleme_sayisi = secili.get("ozetleme_sayisi", 0)
        
        self.terminal.configure(state="normal")
        self.terminal._textbox.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        self._hosgeldin_yaz()
        self._terminale_yaz_satir(t(self.dil, "ws_active", n=secili['isim']), "komut")
        if self.gecmis_ozet:
            self._terminale_yaz_satir(t(self.dil, "ws_mem_summary", s=self.gecmis_ozet[:80] + "..."), "gri")
        
        self.prompt_lbl.configure(text=self._prompt_metni_al())
        self._hafiza_guncelle()

    def _workspace_sil(self, index: int):
        self.workspaces_data["slots"][index] = None
        workspaces_kaydet(self.workspaces_data)
        if self.aktif_ws_index == index:
            self.aktif_ws_index = None
            self._yeni_oturum(yaz=False)
            self._terminale_yaz_satir(t(self.dil, "ws_default"), "komut")
            self.prompt_lbl.configure(text=self._prompt_metni_al())
        self._terminale_yaz_satir(t(self.dil, "ws_cleared"), "aciklama")

    def _mevcut_oturumunu_kaydet(self):
        if hasattr(self, "aktif_ws_index") and self.aktif_ws_index is not None:
            self._terminale_yaz_satir(t(self.dil, "ws_saving"), "gri")
            slot = self.workspaces_data["slots"][self.aktif_ws_index]
            if slot:
                slot["gecmis"] = self.gecmis.copy()
                slot["gecmis_ozet"] = self.gecmis_ozet
                slot["toplam_mesaj"] = self.toplam_mesaj
                slot["ozetleme_sayisi"] = self.ozetleme_sayisi
            workspaces_kaydet(self.workspaces_data)

    def _ozetleme_yap(self, ozetlenecek: list, korunan: list):
        yeni_ozet = gecmisi_ozetle(ozetlenecek, dil=self.dil, active_model=self.model_id)
        self.after(0, self._ozetleme_tamamlandi, yeni_ozet, korunan)

    def _ozetleme_tamamlandi(self, yeni_ozet: str, korunan: list):
        eski_token = gecmis_token_sayisi(self.gecmis) + token_tahmin(self.gecmis_ozet)
        self.gecmis_ozet = yeni_ozet
        self.gecmis = korunan
        self.ozetleme_sayisi += 1
        yeni_token = gecmis_token_sayisi(self.gecmis) + token_tahmin(self.gecmis_ozet)
        self._terminale_yaz_satir(
            t(self.dil, "mem_done", old=eski_token, new=yeni_token, num=self.ozetleme_sayisi), "gri")
        self._hafiza_guncelle()

    def _bilgi_goster(self):
        d = self.dil
        ham_token = gecmis_token_sayisi(self.gecmis)
        ozet_token = token_tahmin(self.gecmis_ozet)
        toplam_token = ham_token + ozet_token
        ham_mesaj = len(self.gecmis) // 2
        kalan_token = GECMIS_BUTCE - toplam_token
        doluluk = min(100, int((toplam_token / GECMIS_BUTCE) * 100))

        dolu = int(doluluk / 5)
        cubuk = "█" * dolu + "░" * (20 - dolu)

        ozet_str = ("Yes" if d == "en" else "Var") if self.gecmis_ozet else ("No" if d == "en" else "Yok")

        bilgi = (
            f"═══ {t(d, 'welcome_title')} ═══\n\n"
            f"{t(d, 'info_memory')}\n"
            f"{t(d, 'info_bar', bar=cubuk, pct=doluluk)}\n"
            f"{t(d, 'info_raw', n=ham_mesaj, t=ham_token)}\n"
            f"{t(d, 'info_summary', s=ozet_str, t=ozet_token)}\n"
            f"{t(d, 'info_total', t=toplam_token, b=GECMIS_BUTCE)}\n"
            f"{t(d, 'info_remaining', r=max(0, kalan_token))}\n"
            f"{t(d, 'info_summaries', n=self.ozetleme_sayisi)}\n"
            f"{t(d, 'info_total_msg', n=self.toplam_mesaj)}\n\n"
            f"⚙️ {t(d, 'info_budget_hdr', ctx=MODEL_CONTEXT).replace('Qwen 2.5 3B', self.model_adi)}\n"
            f"{t(d, 'info_sys_budget', n=SISTEM_BUTCE)}\n"
            f"{t(d, 'info_hist_budget', n=GECMIS_BUTCE)}\n"
            f"{t(d, 'info_resp_budget', n=YANIT_BUTCE)}\n"
            f"{t(d, 'info_safety', n=GUVENLIK_MARJI)}\n\n"
            f"{t(d, 'info_db_hdr')}\n"
            f"{t(d, 'info_db_danger', n=len(TEHLIKELI_KALIPLAR))}\n"
        )

        # Workspace info
        kullanilan_slot = sum(1 for s in self.workspaces_data.get("slots", []) if s is not None)
        bilgi += f"{t(d, 'info_ws_hdr')}\n"
        if self.aktif_ws_index is not None:
            slot = self.workspaces_data["slots"][self.aktif_ws_index]
            if slot:
                bilgi += f"{t(d, 'info_ws_active', n=slot['isim'])}\n"
                bilgi += f"{t(d, 'info_ws_dir', d=slot['yol'])}\n"
        else:
            bilgi += f"{t(d, 'info_ws_none')}\n"
        bilgi += f"{t(d, 'info_ws_slots', u=kullanilan_slot)}\n"
        bilgi += f"{t(d, 'info_ws_how')}\n\n"

        bilgi += (
            f"{t(d, 'info_how_hdr')}\n"
            f"{t(d, 'info_how_body', n=HAM_KORUMA_SAYISI)}"
        )
        
        info_win = ctk.CTkToplevel(self)
        info_win.title(t(d, "info_title"))
        info_win.geometry("480x620")
        info_win.resizable(False, False)
        info_win.configure(fg_color="#111111")
        info_win.transient(self)
        info_win.grab_set()

        txt = ctk.CTkTextbox(info_win,
            font=ctk.CTkFont(family=FONT, size=13),
            fg_color="#111111", text_color="#cccccc",
            corner_radius=0, border_width=0,
            wrap="word")
        txt.pack(fill="both", expand=True, padx=20, pady=(20, 4))
        txt.insert("1.0", bilgi)
        txt.configure(state="disabled")

        ctk.CTkButton(info_win, text="OK",
            font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
            width=120, height=36,
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            text_color="#cccccc", corner_radius=4,
            command=info_win.destroy).pack(pady=(0, 20))

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────

    def _hafiza_guncelle(self):
        ham_token = gecmis_token_sayisi(self.gecmis)
        ozet_token = token_tahmin(self.gecmis_ozet)
        toplam = ham_token + ozet_token
        oran = min(1.0, toplam / GECMIS_BUTCE)
        yuzde = int(oran * 100)

        if yuzde < 50:
            renk = "#16c60c"
        elif yuzde < 80:
            renk = "#f9f1a5"
        else:
            renk = "#e74856"

        self.hafiza_bar.set(oran)
        self.hafiza_bar.configure(progress_color=renk)
        self.hafiza_lbl.configure(
            text=f"{t(self.dil, 'memory')}: {yuzde}%", text_color=renk)

    def _dinamik_model_tespit_et(self):
        """LM Studio'daki aktif modeli algılar ve hem ismi hem de tam ID'yi kaydeder."""
        try:
            r = requests.get(LMS_CHECK_URL, timeout=2)
            if r.status_code == 200:
                data = r.json()
                if "data" in data and len(data["data"]) > 0:
                    model_id = data["data"][0]["id"]
                    self.model_id = model_id  # API için tam ID
                    # Kullanıcı dostu isim
                    self.model_adi = model_id.split("/")[-1].replace(".gguf", "").replace("-", " ").title()
                    if hasattr(self, "model_bilgi_lbl"):
                        self.model_bilgi_lbl.configure(text=f"[{self.model_adi}] {MODEL_CONTEXT}")
                    return
        except Exception as e:
            log_mesaj(f"Model detection error: {e}", "WARNING")
            
        self.model_adi = "Local AI"
        self.model_id = MODEL
        if hasattr(self, "model_bilgi_lbl"):
            self.model_bilgi_lbl.configure(text=f"[{self.model_adi}] {MODEL_CONTEXT}")

    def _yukleniyor(self, aktif: bool):
        if aktif:
            self.giris.configure(state="disabled")
            self.durum_lbl.configure(text=t(self.dil, "thinking"), text_color=SARI)
        else:
            self.giris.configure(state="normal")
            self.durum_lbl.configure(text=t(self.dil, "ready"),
                                    text_color=self.ayarlar["komut_renk"])
            self.giris.focus_set()


# ══════════════════════════════════════════════
#  BOOT SCREEN — LM Studio Auto-Launch
# ══════════════════════════════════════════════

# Known LM Studio paths (checked in order)
LMS_PATHS = [
    r"C:\Program Files\LM Studio\LM Studio.exe",
    r"C:\Program Files (x86)\LM Studio\LM Studio.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\LM Studio\LM Studio.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\LM Studio\LM Studio.exe"),
    os.path.expandvars(r"%APPDATA%\LM Studio\LM Studio.exe"),
]

LMS_CHECK_URL = "http://localhost:1234/v1/models"
LMS_TIMEOUT   = 90  # Max seconds to wait for server


def sunucu_aktif_mi() -> bool:
    """Check if LM Studio server is running on port 1234."""
    try:
        r = requests.get(LMS_CHECK_URL, timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def lm_studio_yolunu_bul() -> str:
    """Find LM Studio executable path."""
    for yol in LMS_PATHS:
        if os.path.exists(yol):
            return yol
    # Fallback: search running process
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             'Get-Process -Name "LM Studio" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Path'],
            capture_output=True, text=True, timeout=5
        )
        yol = result.stdout.strip()
        if yol and os.path.exists(yol):
            return yol
    except Exception:
        pass
    return ""


class BootScreen(ctk.CTk):
    """Startup screen: checks LM Studio, auto-launches if needed."""

    def __init__(self):
        super().__init__()

        ayarlar = ayarlari_yukle()
        self.dil = ayarlar.get("dil", "en")

        self.title(t(self.dil, "boot_title"))
        self.geometry("480x260")
        self.resizable(False, False)
        self.configure(fg_color="#0c0c0c")
        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)
            self.after(200, lambda: self.iconbitmap(ICON_PATH))

        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 130
        self.geometry(f"480x260+{x}+{y}")

        # Header
        ctk.CTkLabel(self, text=t(self.dil, "bar_title").strip(),
            font=ctk.CTkFont(family=FONT, size=24, weight="bold"),
            text_color="#c678dd").pack(pady=(30, 8))

        # Status label
        self.status_lbl = ctk.CTkLabel(self,
            text=t(self.dil, "boot_checking"),
            font=ctk.CTkFont(family=FONT, size=13),
            text_color=ACIK_GRI)
        self.status_lbl.pack(pady=(0, 16))

        # Progress bar
        self.progress = ctk.CTkProgressBar(self,
            width=360, height=10, corner_radius=5,
            fg_color="#2a2a2a", progress_color="#c678dd",
            border_width=0, mode="indeterminate")
        self.progress.pack(pady=(0, 16))
        self.progress.start()

        # Detail label
        self.detail_lbl = ctk.CTkLabel(self, text="",
            font=ctk.CTkFont(family=FONT, size=11),
            text_color=GRI)
        self.detail_lbl.pack(pady=(0, 8))

        # Button frame (hidden initially)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._cancelled = False
        self.after(500, self._start_check)

    def _start_check(self):
        threading.Thread(target=self._check_and_launch, daemon=True).start()

    def _check_and_launch(self):
        # Step 1: Is server already running?
        if sunucu_aktif_mi():
            self.after(0, self._update_status, t(self.dil, "boot_found"), "#16c60c")
            self.after(800, self._boot_success)
            return

        # Step 2: Find LM Studio
        self.after(0, self._update_status, t(self.dil, "boot_not_found"), SARI)
        lms_path = lm_studio_yolunu_bul()

        if not lms_path:
            self.after(0, self._show_not_installed)
            return

        # Step 3: Launch LM Studio
        self.after(0, self._update_status, t(self.dil, "boot_launching"), "#c678dd")
        try:
            subprocess.Popen([lms_path], shell=False,
                             creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)
        except Exception:
            # Try with shell
            try:
                os.startfile(lms_path)
            except Exception:
                self.after(0, self._show_not_installed)
                return

        # Step 4: Wait for server to come online
        import time
        waited = 0
        while waited < LMS_TIMEOUT and not self._cancelled:
            time.sleep(2)
            waited += 2
            self.after(0, self._update_detail,
                       t(self.dil, "boot_waiting", s=waited))
            if sunucu_aktif_mi():
                self.after(0, self._update_status, t(self.dil, "boot_ready"), "#16c60c")
                self.after(1000, self._boot_success)
                return

        if not self._cancelled:
            self.after(0, self._show_failed)

    def _update_status(self, text, color):
        self.status_lbl.configure(text=text, text_color=color)

    def _update_detail(self, text):
        self.detail_lbl.configure(text=text)

    def _boot_success(self):
        self.progress.stop()
        self.destroy()
        uygulama = AITerminalAsistani()
        uygulama.mainloop()

    def _show_not_installed(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        self._update_status(t(self.dil, "boot_lms_not_installed"), KIRMIZI)
        self._show_buttons()

    def _show_failed(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        self._update_status(
            t(self.dil, "boot_failed", s=LMS_TIMEOUT).split("\n")[0], KIRMIZI)
        self._update_detail(
            t(self.dil, "boot_failed", s=LMS_TIMEOUT).split("\n")[-1])
        self._show_buttons()

    def _show_buttons(self):
        self.btn_frame.pack(pady=(8, 0))

        ctk.CTkButton(self.btn_frame, text=t(self.dil, "boot_manual"),
            width=120, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            text_color="#16c60c", corner_radius=4,
            command=self._manual_start).pack(side="left", padx=6)

        ctk.CTkButton(self.btn_frame, text=t(self.dil, "boot_retry"),
            width=100, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#2a2a3a", hover_color="#3a3a5a",
            text_color="#c678dd", corner_radius=4,
            command=self._retry).pack(side="left", padx=6)

        ctk.CTkButton(self.btn_frame, text=t(self.dil, "boot_quit"),
            width=80, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            text_color=KIRMIZI, corner_radius=4,
            command=self._quit).pack(side="left", padx=6)

    def _manual_start(self):
        """Skip check, go directly to main app."""
        self._cancelled = True
        self.destroy()
        uygulama = AITerminalAsistani()
        uygulama.mainloop()

    def _retry(self):
        """Restart the check process."""
        self._cancelled = True
        self.btn_frame.pack_forget()
        for w in self.btn_frame.winfo_children():
            w.destroy()
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self._update_status(t(self.dil, "boot_checking"), ACIK_GRI)
        self._update_detail("")
        self._cancelled = False
        self.after(500, self._start_check)

    def _quit(self):
        self._cancelled = True
        self.destroy()

# ══════════════════════════════════════════════


# ══════════════════════════════════════════════
#  HISTORY WINDOW
# ══════════════════════════════════════════════

class HistoryPenceresi(ctk.CTkToplevel):
    """Komut geçmişi penceresi."""
    
    def __init__(self, parent, gecmis, secim_callback, dil="en"):
        super().__init__(parent)
        self.title(t(dil, "history_title"))
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()
        
        self.gecmis = gecmis
        self.secim_callback = secim_callback
        self.dil = dil
        
        # Search box
        arama_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        arama_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(arama_frame, text="🔍", font=ctk.CTkFont(size=14), text_color=ACIK_GRI).pack(side="left", padx=(10, 5))
        
        self.arama_giris = ctk.CTkEntry(arama_frame,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#1a1a1a", text_color=PARLAK_BEYAZ,
            border_width=0, placeholder_text=t(dil, "history_search"))
        self.arama_giris.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.arama_giris.bind("<KeyRelease>", self._arama_yap)
        
        # History list
        self.liste_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.favori_sadece = False
        self._liste_guncelle(gecmis)
        
        # Bottom bar
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=20, pady=(0, 20))

        self.fav_filter_btn = ctk.CTkButton(bot, text=t(self.dil, "history_show_favorites"), 
            width=140, height=32, font=ctk.CTkFont(size=11),
            fg_color="#1a1a1a", border_width=1, command=self._toggle_filter)
        self.fav_filter_btn.pack(side="left")

        ctk.CTkButton(bot, text=t(self.dil, "common_close"),
            width=100, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            text_color="#cccccc", corner_radius=4,
            command=self.destroy).pack(side="right")
    
    def _toggle_filter(self):
        self.favori_sadece = not self.favori_sadece
        self.fav_filter_btn.configure(fg_color="#3a3a1a" if self.favori_sadece else "#1a1a1a")
        self._liste_guncelle(self.gecmis)

    def _liste_guncelle(self, gecmis):
        # Clear existing
        for widget in self.liste_frame.winfo_children():
            widget.destroy()
        
        if not gecmis:
            ctk.CTkLabel(self.liste_frame, text=t(self.dil, "history_empty"),
                font=ctk.CTkFont(family=FONT, size=13), text_color=ACIK_GRI).pack(pady=40)
            return
        
        for item in gecmis[:50]:  # Show max 50
            satir = ctk.CTkFrame(self.liste_frame, fg_color="#1a1a1a", corner_radius=4)
            satir.pack(fill="x", pady=2)
            
            sol = ctk.CTkFrame(satir, fg_color="transparent")
            sol.pack(side="left", fill="x", expand=True, padx=10, pady=6)
            
            fav_icon = "★ " if item.get("favori", False) else "  "
            ctk.CTkLabel(sol, text=f"{fav_icon}{item['komut'][:60]}",
                font=ctk.CTkFont(family=FONT, size=12), text_color=PARLAK_BEYAZ,
                anchor="w").pack(anchor="w")
            ctk.CTkLabel(sol, text=item.get("zaman", ""),
                font=ctk.CTkFont(family=FONT, size=10), text_color=ACIK_GRI,
                anchor="w").pack(anchor="w")
            
            
            fav_status = item.get("favori", False)
            fav_color = "#f9f1a5" if fav_status else "#444444"
            
            ctk.CTkButton(satir, text="★", width=24, height=24, 
                fg_color="transparent", text_color=fav_color,
                command=lambda i=item: self._fav_degistir(i)).pack(side="right", padx=5)

            ctk.CTkButton(satir, text=t(self.dil, "history_use"),
                width=60, height=24,
                font=ctk.CTkFont(family=FONT, size=11),
                fg_color="#1a3a1a", hover_color="#2a5a2a",
                text_color="#16c60c", corner_radius=4,
                command=lambda k=item['komut']: self._sec(k)).pack(side="right", padx=5)
    
    def _fav_degistir(self, item):
        item["favori"] = not item.get("favori", False)
        # Update persistence
        gecmis_kaydet({"komutlar": self.gecmis, "index": 0})
        self._liste_guncelle(self.gecmis)

    def _arama_yap(self, event=None):
        arama_metni = self.arama_giris.get().lower()
        datalist = self.gecmis
        if self.favori_sadece:
            datalist = [i for i in datalist if i.get("favori")]
            
        if not arama_metni:
            self._liste_guncelle(datalist)
            return
        
        filtrelenmis = [item for item in datalist if arama_metni in item["komut"].lower()]
        self._liste_guncelle(filtrelenmis)
    
    def _sec(self, komut):
        self.destroy()
        self.secim_callback(komut)


# ══════════════════════════════════════════════
#  TEMPLATES WINDOW
# ══════════════════════════════════════════════

class SablonPenceresi(ctk.CTkToplevel):
    """Şablonlar penceresi."""
    
    def __init__(self, parent, sablonlar, kullan_callback, kaydet_callback, dil="en"):
        super().__init__(parent)
        self.title(t(dil, "templates_title"))
        self.geometry("650x550")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()
        
        self.sablonlar = sablonlar
        self.kullan_callback = kullan_callback
        self.kaydet_callback = kaydet_callback
        self.dil = dil
        
        # Title
        ctk.CTkLabel(self, text=t(dil, "templates_title"),
            font=ctk.CTkFont(family=FONT, size=16, weight="bold"),
            text_color="#cccccc").pack(pady=(20, 10))
        
        # Hint
        ctk.CTkLabel(self, text=t(dil, "templates_hint"),
            font=ctk.CTkFont(family=FONT, size=11), text_color=ACIK_GRI).pack(pady=(0, 10))
        
        # Templates list
        self.liste_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.liste_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._liste_guncelle()
        
        # Bottom buttons
        alt_frame = ctk.CTkFrame(self, fg_color="transparent")
        alt_frame.pack(pady=10)
        
        ctk.CTkButton(alt_frame, text=t(dil, "templates_new"),
            width=140, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            text_color="#16c60c", corner_radius=4,
            command=self._yeni_sablon_ekle).pack(side="left", padx=6)
        
        ctk.CTkButton(alt_frame, text=t(self.dil, "common_close"),
            width=100, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            text_color="#cccccc", corner_radius=4,
            command=self.destroy).pack(side="left", padx=6)
    
    def _liste_guncelle(self):
        for widget in self.liste_frame.winfo_children():
            widget.destroy()
        
        if not self.sablonlar:
            ctk.CTkLabel(self.liste_frame, text=t(self.dil, "templates_empty"),
                font=ctk.CTkFont(family=FONT, size=13), text_color=ACIK_GRI).pack(pady=40)
            return
        
        for i, sablon in enumerate(self.sablonlar):
            satir = ctk.CTkFrame(self.liste_frame, fg_color="#1a1a1a", corner_radius=4)
            satir.pack(fill="x", pady=3)
            
            sol = ctk.CTkFrame(satir, fg_color="transparent")
            sol.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            ctk.CTkLabel(sol, text=f"📋 {sablon['ad']}",
                font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
                text_color="#16c60c", anchor="w").pack(anchor="w")
            ctk.CTkLabel(sol, text=sablon.get("aciklama", ""),
                font=ctk.CTkFont(family=FONT, size=11), text_color=ACIK_GRI,
                anchor="w").pack(anchor="w")
            ctk.CTkLabel(sol, text=sablon['komut'][:70] + ("..." if len(sablon['komut']) > 70 else ""),
                font=ctk.CTkFont(family=FONT, size=10), text_color=GRI,
                anchor="w").pack(anchor="w")
            
            ctk.CTkButton(satir, text=t(self.dil, "templates_use"),
                width=60, height=24,
                font=ctk.CTkFont(family=FONT, size=11),
                fg_color="#1a3a1a", hover_color="#2a5a2a",
                text_color="#16c60c", corner_radius=4,
                command=lambda s=sablon: self._kullan(s)).pack(side="right", padx=(0, 6))
            
            ctk.CTkButton(satir, text="🗑️",
                width=40, height=24,
                font=ctk.CTkFont(family=FONT, size=11),
                fg_color="#3a1a1a", hover_color="#5a2a2a",
                text_color=KIRMIZI, corner_radius=4,
                command=lambda idx=i: self._sil(idx)).pack(side="right")
    
    def _kullan(self, sablon):
        self.destroy()
        self.kullan_callback(sablon)
    
    def _sil(self, index):
        if 0 <= index < len(self.sablonlar):
            self.sablonlar.pop(index)
            sablonlar_kaydet(self.sablonlar)
            self._liste_guncelle()
    
    def _yeni_sablon_ekle(self):
        """Yeni şablon ekleme formu."""
        form = ctk.CTkToplevel(self)
        form.title(t(self.dil, "templates_new"))
        form.geometry("500x350")
        form.resizable(False, False)
        form.configure(fg_color="#111111")
        form.transient(self)
        form.grab_set()
        
        ctk.CTkLabel(form, text=t(self.dil, "templates_name"),
            font=ctk.CTkFont(family=FONT, size=12), text_color="#cccccc").pack(anchor="w", padx=20, pady=(20, 5))
        ad_giris = ctk.CTkEntry(form, font=ctk.CTkFont(family=FONT, size=12), fg_color="#1a1a1a", text_color=PARLAK_BEYAZ)
        ad_giris.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form, text=t(self.dil, "templates_cmd"),
            font=ctk.CTkFont(family=FONT, size=12), text_color="#cccccc").pack(anchor="w", padx=20, pady=(10, 5))
        cmd_giris = ctk.CTkTextbox(form, font=ctk.CTkFont(family=FONT, size=12), fg_color="#1a1a1a", text_color=PARLAK_BEYAZ, height=80)
        cmd_giris.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(form, text=t(self.dil, "templates_desc"),
            font=ctk.CTkFont(family=FONT, size=12), text_color="#cccccc").pack(anchor="w", padx=20, pady=(10, 5))
        desc_giris = ctk.CTkEntry(form, font=ctk.CTkFont(family=FONT, size=12), fg_color="#1a1a1a", text_color=PARLAK_BEYAZ)
        desc_giris.pack(fill="x", padx=20, pady=(0, 20))
        
        def kaydet():
            ad = ad_giris.get().strip()
            cmd = cmd_giris.get("1.0", "end").strip()
            desc = desc_giris.get().strip()
            
            if not ad or not cmd:
                return
            
            yeni_sablon = {"ad": ad, "komut": cmd, "aciklama": desc}
            self.kaydet_callback(yeni_sablon)
            self._liste_guncelle()
            form.destroy()
        
        ctk.CTkButton(form, text=t(self.dil, "templates_save"),
            width=120, height=32,
            font=ctk.CTkFont(family=FONT, size=12),
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            text_color="#16c60c", corner_radius=4,
            command=kaydet).pack(pady=(0, 20))


# ══════════════════════════════════════════════
#  TEMPLATE PARAMETER WINDOW
# ══════════════════════════════════════════════

class TemplateParameterPenceresi(ctk.CTkToplevel):
    def __init__(self, parent, sablon, callback, dil="en"):
        super().__init__(parent)
        self.dil = dil
        self.title(t(dil, "template_param_title"))
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(fg_color="#111111")
        self.transient(parent)
        self.grab_set()
        
        self.sablon = sablon
        self.callback = callback
        self.inputs = {}
        
        ctk.CTkLabel(self, text=t(dil, "template_param_label", n=sablon['ad']), 
            font=ctk.CTkFont(family=FONT, size=15, weight="bold"), text_color="#16c60c").pack(pady=20)
        
        komut = sablon["komut"]
        param_names = re.findall(r"\{(.*?)\}", komut)
        
        container = ctk.CTkScrollableFrame(self, fg_color="transparent", height=200)
        container.pack(fill="both", expand=True, padx=20)
        
        for name in param_names:
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            ctk.CTkLabel(frame, text=name.capitalize() + ":", font=ctk.CTkFont(family=FONT, size=12)).pack(anchor="w")
            ent = ctk.CTkEntry(frame, fg_color="#1a1a1a", border_width=1)
            ent.pack(fill="x", pady=2)
            self.inputs[name] = ent
            
        def apply():
            res = komut
            for name, ent in self.inputs.items():
                val = ent.get().strip() or f"[{name}]"
                res = res.replace("{" + name + "}", val)
            self.destroy()
            self.callback(res, sablon["ad"])
            
        ctk.CTkButton(self, text=t(dil, "template_param_prepare"), fg_color="#1a3a1a", hover_color="#2a5a2a",
            command=apply).pack(pady=20)


if __name__ == "__main__":

    boot = BootScreen()
    boot.mainloop()
