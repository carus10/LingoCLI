"""
══════════════════════════════════════════════════════════════
  KOMUT VERİTABANI (SADELEŞTİRİLMİŞ - FINETUNED MODEL İÇİN)
  AI Terminal Asistanı için güvenlik kalıpları ve basit sistem promptu.
══════════════════════════════════════════════════════════════
"""

# ──────────────────────────────────────────────────────────
#  TEHLİKELİ KOMUT KALIPLARI (Python tarafında kontrol)
#  Bu kalıplardan biri eşleşirse "EXTRA ONAY" istenir.
# ──────────────────────────────────────────────────────────
TEHLIKELI_KALIPLAR = [
    # === SİSTEM SİLME / FORMATLAMA ===
    r"Remove-Item\s+.*-Recurse.*-Force",       # Toplu ve zorla silme
    r"Remove-Item\s+.*C:\\Windows",             # Windows klasörü silme
    r"Remove-Item\s+.*C:\\Program\s*Files",     # Program Files silme
    r"Remove-Item\s+.*\\\*",                    # Joker ile toplu silme
    r"rm\s+-r",                                 # Unix stili silme
    r"rmdir\s+/s",                              # CMD toplu klasör silme
    r"del\s+/[sfq]",                            # CMD toplu dosya silme
    r"Format-Volume",                           # Disk formatlama
    r"Clear-Disk",                              # Disk temizleme
    r"Initialize-Disk",                         # Disk sıfırlama
    r"format\s+[a-zA-Z]:",                      # CMD format
    r"diskpart",                                # Disk yönetimi aracı

    # === REGISTRY (Kayıt Defteri) ===
    r"Remove-ItemProperty.*HKLM",              # Sistem registry silme
    r"Remove-Item.*HKLM",                      # Sistem registry silme
    r"Set-ItemProperty.*HKLM",                 # Sistem registry değiştirme
    r"New-ItemProperty.*HKLM",                 # Sistem registry ekleme
    r"reg\s+delete",                           # CMD registry silme
    r"reg\s+add.*HKLM",                        # CMD registry ekleme
    r"regedit",                                # Registry editörü

    # === KULLANICI ve YETKİ ===
    r"Remove-LocalUser",                       # Kullanıcı silme
    r"Disable-LocalUser",                      # Kullanıcı devre dışı
    r"net\s+user\s+.*\s+/delete",              # CMD kullanıcı silme
    r"net\s+user\s+.*\s+/active:no",           # CMD kullanıcı devre dışı

    # === GÜVENLİK DUVARI ve DEFENDER ===
    r"Set-NetFirewallProfile.*-Enabled\s+False",  # Güvenlik duvarı kapatma
    r"Disable-NetFirewallRule",                    # Kural devre dışı
    r"Set-MpPreference.*-DisableRealtimeMonitoring.*True",  # Defender kapatma
    r"netsh\s+advfirewall\s+set.*state\s+off",    # CMD firewall kapatma

    # === SERVİS YÖNETİMİ (Kritik) ===
    r"Stop-Service\s+.*wuauserv",              # Windows Update servisi
    r"Stop-Service\s+.*WinDefend",             # Defender servisi
    r"Stop-Service\s+.*Spooler",               # Yazıcı servisi
    r"sc\s+delete",                            # Servis silme
    r"sc\s+stop",                              # Servis durdurma (CMD)

    # === SİSTEM DURUMU ===
    r"Restart-Computer",                       # Yeniden başlatma
    r"Stop-Computer",                          # Kapatma
    r"shutdown",                               # CMD kapatma
    r"bcdedit",                                # Boot ayarları
    r"sfc\s+/scannow",                         # Sistem dosyası tarama

    # === AĞDA RİSKLİ İŞLEMLER ===
    r"Invoke-WebRequest.*\|\s*Invoke-Expression",  # Uzaktan kod çalıştırma
    r"iex\s*\(",                                    # Invoke-Expression kısaltma
    r"IEX\s*\(",
    r"DownloadString",                              # Web'den indirip çalıştırma
    r"Start-Process.*-Verb\s+RunAs",                # Yönetici olarak çalıştır
    r"Set-ExecutionPolicy\s+Unrestricted",          # Script güvenliğini kaldır
]

# ──────────────────────────────────────────────────────────
#  SADELEŞTİRİLMİŞ SİSTEM PROMPTU
# ──────────────────────────────────────────────────────────

def dinamik_prompt_olustur(kullanici_istegi: str, dil: str = "tr") -> str:
    prompt_en = (
        "You are an expert Windows OS and PowerShell Assistant. "
        "Your task is to convert user requests into executable terminal commands.\n"
        "RULES:\n"
        "1. Output MUST be a valid JSON object. No markdown blocks, no conversational text.\n"
        "2. JSON Keys: \"type\" (command_explained), \"explain\" (brief text), \"content\" (the command).\n"
        "3. Use absolute paths when unsure. Use $env:USERPROFILE\\Desktop for desktop.\n"
        "4. Combine multiple steps with ';' or '&&'.\n"
        "5. Be concise and accurate. Do not apologize."
    )

    prompt_tr = (
        "Sen uzman bir Windows ve PowerShell asistanısın. "
        "Görevin, kullanıcı isteklerini çalıştırılabilir terminal komutlarına dönüştürmektir.\n"
        "KURALLAR:\n"
        "1. Yanıt SADECE geçerli bir JSON objesi olmalıdır. Markdown bloğu veya açıklama metni ekleme.\n"
        "2. JSON Anahtarları: \"type\" (command_explained), \"explain\" (kısa açıklama), \"content\" (komut).\n"
        "3. Masaüstü için $env:USERPROFILE\\Desktop gibi mutlak yollar kullan.\n"
        "4. Çoklu adımları ';' veya '&&' ile birleştir.\n"
        "5. Kısa ve net ol. Gereksiz özür veya giriş metni kullanma."
    )

    return prompt_en if dil == "en" else prompt_tr
