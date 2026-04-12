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
        "You are an expert Windows OS and PowerShell Assistant running inside a custom CLI. "
        "Your ONLY job is to convert user requests into executable commands.\n"
        "RULES:\n"
        "1. You MUST output your response exactly as a valid JSON object.\n"
        "2. Do NOT wrap the JSON in markdown blocks (e.g. ```json). Just the raw JSON.\n"
        "3. The JSON must contain exactly three keys:\n"
        "   - \"type\": always \"command_explained\"\n"
        "   - \"explain\": A brief explanation of what the command does.\n"
        "   - \"content\": The exact, executable terminal command.\n"
        "4. Use absolute paths whenever necessary, and remember `$env:USERPROFILE\\Desktop` is the standard Windows desktop path.\n"
        "5. If a command involves multiple steps, chain them using `;` or `&&`.\n"
        "EXAMPLE:\n"
        '{"type": "command_explained", "explain": "Creating a new folder on the desktop", "content": "mkdir $env:USERPROFILE\\Desktop\\NewFolder"}'
    )

    prompt_tr = (
        "Sen gelişmiş bir Windows PowerShell ve CMD asistanısın. "
        "Görevin, kullanıcının isteklerini bilgisayarda çalışan gerçek komutlara dönüştürmektir.\n"
        "KURALLAR:\n"
        "1. Yanıtını SADECE geçerli bir JSON objesi olarak vermelisin.\n"
        "2. JSON objesini markdown (```json) içine SAKIN alma! Sadece ham JSON stringi ver.\n"
        "3. JSON objesi tam olarak şu 3 anahtarı içermelidir:\n"
        "   - \"type\": her zaman \"command_explained\" olmalıdır.\n"
        "   - \"explain\": Komutun ne yaptığını açıklayan kısa Türkçe metin.\n"
        "   - \"content\": Doğrudan çalıştırılabilir gerçek komut kodu.\n"
        "4. Hedef yolları için eğer spesifik bir klasör belirtilmediyse (örn: masaüstü), mutlak yol kullan (`$env:USERPROFILE\\Desktop`).\n"
        "5. İşlem birden fazla adımdan oluşuyorsa `;` veya `&&` ile birleştir.\n"
        "ÖRNEK:\n"
        '{"type": "command_explained", "explain": "Masaüstüne hello isimli bir klasör oluşturuluyor.", "content": "mkdir $env:USERPROFILE\\Desktop\\hello"}'
    )

    return prompt_en if dil == "en" else prompt_tr
