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
        mesajlar.append({"role": "system", "content": f"Current directory: {cwd_bilgisi}"})
    if ozet:
        mesajlar.append({"role": "system", "content": f"Context summary: {ozet}"})
    
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
        f"Aşağıdaki konuşmayı {('Türkçe' if dil=='tr' else 'English')} olarak çok kısa (3-4 cümle) özetle. "
        "Sadece teknik değişimleri (dosya/klasör işlemleri) belirt.\n\n" + konusma_metni
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
        tb.tag_configure("kullanici", foreground=self.ayarlar["kullanici_renk"])
        tb.tag_configure("komut",     foreground=self.ayarlar["komut_renk"])
        tb.tag_configure("aciklama",  foreground=self.ayarlar["aciklama_renk"])
        tb.tag_configure("prompt",    foreground=self.ayarlar["prompt_renk"])
        tb.tag_configure("sari",      foreground=SARI)
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
        self._terminale_yaz_satir(t(d, "welcome_memory"), ACIK_GRI)
        self._terminale_yaz_satir("─" * 70, GRI)
        self._terminale_yaz_satir(t(d, "welcome_hint"), ACIK_GRI)

    def _yeni_oturum(self, yaz=True):
        self._mevcut_oturumunu_kaydet()
        
        self.gecmis.clear()
        self.gecmis_ozet = ""
        self.toplam_mesaj = 0
        self.ozetleme_sayisi = 0
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
        ctk.CTkLabel(self, text="⚡ AI Terminal",
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

if __name__ == "__main__":
    boot = BootScreen()
    boot.mainloop()
