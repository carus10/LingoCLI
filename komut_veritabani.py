"""
══════════════════════════════════════════════════════════════
  KOMUT VERİTABANI
  AI Terminal Asistanı için referans komut örnekleri,
  güvenlik kalıpları ve sistem promptu.
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
#  KOMUT ÖRNEKLERİ VERİTABANI
#  Her kategori: (kullanıcının yazacağı istek, doğru komut)
#  Model bu örneklerden öğrenerek doğru format üretir.
# ──────────────────────────────────────────────────────────
KOMUT_ORNEKLERI = {

    # ═══════════════════════════════════════════════════════
    #  1. DOSYA VE KLASÖR YÖNETİMİ
    # ═══════════════════════════════════════════════════════
    "Dosya ve Klasör Yönetimi": [
        ("masaüstünde proje adlı klasör oluştur",
         'New-Item -ItemType Directory -Path "$env:USERPROFILE\\Desktop\\proje"'),
        ("masaüstünde Eşek adlı klasör oluştur",
         'New-Item -ItemType Directory -Path "$env:USERPROFILE\\Desktop\\Eşek"'),
        ("masaüstünde Yeni Klasör adlı klasör oluştur",
         'New-Item -ItemType Directory -Path "$env:USERPROFILE\\Desktop\\Yeni Klasör"'),
        ("masaüstünde test.txt adlı dosya oluştur",
         'New-Item -ItemType File -Path "$env:USERPROFILE\\Desktop\\test.txt"'),
        ("masaüstündeki dosyaları listele",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop"'),
        ("masaüstündeki tüm txt dosyalarını listele",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -Filter "*.txt"'),
        ("masaüstündeki proje klasörünü sil",
         'Remove-Item -Path "$env:USERPROFILE\\Desktop\\proje" -Recurse -Force'),
        ("masaüstündeki test.txt dosyasını sil",
         'Remove-Item -Path "$env:USERPROFILE\\Desktop\\test.txt"'),
        ("masaüstündeki eski.txt dosyasını yeni.txt olarak yeniden adlandır",
         'Rename-Item -Path "$env:USERPROFILE\\Desktop\\eski.txt" -NewName "yeni.txt"'),
        ("masaüstündeki rapor.docx dosyasını belgelerime kopyala",
         'Copy-Item -Path "$env:USERPROFILE\\Desktop\\rapor.docx" -Destination "$env:USERPROFILE\\Documents"'),
        ("masaüstündeki foto.jpg dosyasını belgelerime taşı",
         'Move-Item -Path "$env:USERPROFILE\\Desktop\\foto.jpg" -Destination "$env:USERPROFILE\\Documents"'),
        ("masaüstündeki test.txt dosyasının içeriğini göster",
         'Get-Content -Path "$env:USERPROFILE\\Desktop\\test.txt"'),
        ("masaüstündeki test.txt dosyasına merhaba dünya yaz",
         'Set-Content -Path "$env:USERPROFILE\\Desktop\\test.txt" -Value "Merhaba Dünya"'),
        ("masaüstündeki test.txt dosyasının sonuna yeni satır ekle",
         'Add-Content -Path "$env:USERPROFILE\\Desktop\\test.txt" -Value "Yeni satır"'),
        ("C diskindeki tüm dosya ve klasörleri listele",
         'Get-ChildItem -Path "C:\\" -Force'),
        ("belgelerim klasöründeki dosyaları tarihe göre sırala",
         'Get-ChildItem -Path "$env:USERPROFILE\\Documents" | Sort-Object LastWriteTime -Descending'),
        ("masaüstündeki dosyaların toplam boyutunu göster",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -File | Measure-Object -Property Length -Sum'),
        ("masaüstünde 10 MB den büyük dosyaları bul",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -File | Where-Object { $_.Length -gt 10MB }'),
        ("belgelerim klasöründe alt klasörleriyle birlikte tüm pdf dosyalarını bul",
         'Get-ChildItem -Path "$env:USERPROFILE\\Documents" -Filter "*.pdf" -Recurse'),
        ("indirilenler klasörünü aç",
         'Invoke-Item "$env:USERPROFILE\\Downloads"'),
        ("masaüstündeki projem klasöründe src alt klasörü oluştur",
         'New-Item -ItemType Directory -Path "$env:USERPROFILE\\Desktop\\projem\\src"'),
        ("masaüstündeki boş klasörleri bul",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -Directory | Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 }'),
        ("masaüstündeki tüm dosyaları uzantısına göre grupla",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -File | Group-Object Extension'),
        ("son 7 günde değiştirilen dosyaları masaüstünde bul",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }'),
        ("masaüstündeki dosya sayısını göster",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop" -File | Measure-Object | Select-Object -ExpandProperty Count'),
    ],

    # ═══════════════════════════════════════════════════════
    #  2. SİSTEM BİLGİSİ
    # ═══════════════════════════════════════════════════════
    "Sistem Bilgisi": [
        ("bilgisayarımın adını göster",
         '$env:COMPUTERNAME'),
        ("kullanıcı adımı göster",
         '$env:USERNAME'),
        ("windows versiyonumu göster",
         'Get-ComputerInfo | Select-Object WindowsVersion, OsName, OsBuildNumber'),
        ("işlemcim hakkında bilgi ver",
         'Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, MaxClockSpeed'),
        ("RAM miktarımı göster",
         'Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum | ForEach-Object { "{0} GB" -f ($_.Sum / 1GB) }'),
        ("disk alanlarını göster",
         'Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N="Kullanılan(GB)";E={[math]::Round($_.Used/1GB,2)}}, @{N="Boş(GB)";E={[math]::Round($_.Free/1GB,2)}}'),
        ("sistemin ne zamandır açık olduğunu göster",
         '(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime'),
        ("ekran kartımı göster",
         'Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion'),
        ("anakartım hakkında bilgi ver",
         'Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, SerialNumber'),
        ("BIOS bilgilerimi göster",
         'Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate'),
        ("yüklü sürücüleri göster",
         'Get-CimInstance Win32_PnPSignedDriver | Select-Object DeviceName, DriverVersion | Where-Object {$_.DeviceName} | Format-Table'),
        ("pil durumunu göster",
         'Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus'),
        ("sistemdeki ortam değişkenlerini göster",
         'Get-ChildItem Env: | Format-Table Name, Value'),
        ("PATH değişkenini göster",
         '$env:PATH -split ";"'),
        ("yüklü programları listele",
         'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName'),
        ("bilgisayarın IP adresini göster",
         'Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback" } | Select-Object InterfaceAlias, IPAddress'),
        ("aktif ağ bağlantılarını göster",
         'Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed'),
    ],

    # ═══════════════════════════════════════════════════════
    #  3. AĞ VE İNTERNET
    # ═══════════════════════════════════════════════════════
    "Ağ ve İnternet": [
        ("google a ping at",
         'Test-Connection -ComputerName google.com -Count 4'),
        ("internet bağlantımı kontrol et",
         'Test-Connection -ComputerName 8.8.8.8 -Count 2 -Quiet'),
        ("DNS ayarlarımı göster",
         'Get-DnsClientServerAddress | Where-Object {$_.ServerAddresses} | Select-Object InterfaceAlias, ServerAddresses'),
        ("wifi ağlarını göster",
         'netsh wlan show networks mode=bssid'),
        ("bağlı olduğum wifi ağını göster",
         'netsh wlan show interfaces'),
        ("wifi şifremi göster",
         'netsh wlan show profile name="$(netsh wlan show interfaces | Select-String "Profile" | ForEach-Object { ($_ -split ":")[1].Trim() })" key=clear'),
        ("açık portları göster",
         'Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess'),
        ("şu anda hangi uygulamalar internet kullanıyor",
         'Get-NetTCPConnection -State Established | Select-Object @{N="Process";E={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}}, RemoteAddress, RemotePort | Sort-Object Process -Unique'),
        ("IP adresimi göster",
         '(Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content'),
        ("bir web sitesinin IP adresini bul",
         'Resolve-DnsName google.com | Select-Object Name, IPAddress'),
        ("ağ adaptörlerimi göster",
         'Get-NetAdapter | Select-Object Name, Status, MacAddress, LinkSpeed'),
        ("traceroute yap google a",
         'Test-NetConnection google.com -TraceRoute'),
        ("indirilenler klasöründen bir dosya indir",
         'Invoke-WebRequest -Uri "https://example.com/dosya.zip" -OutFile "$env:USERPROFILE\\Downloads\\dosya.zip"'),
        ("MAC adresimi göster",
         'Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object Name, MacAddress'),
        ("ağ istatistiklerini göster",
         'Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes'),
    ],

    # ═══════════════════════════════════════════════════════
    #  4. SÜREÇ (PROCESS) YÖNETİMİ
    # ═══════════════════════════════════════════════════════
    "Süreç Yönetimi": [
        ("çalışan tüm süreçleri listele",
         'Get-Process | Select-Object Name, Id, CPU, WorkingSet64 | Sort-Object CPU -Descending | Select-Object -First 20'),
        ("en çok CPU kullanan 10 süreci göster",
         'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, Id, CPU'),
        ("en çok RAM kullanan 10 süreci göster",
         'Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name, Id, @{N="RAM(MB)";E={[math]::Round($_.WorkingSet64/1MB,2)}}'),
        ("chrome sürecini kapat",
         'Stop-Process -Name "chrome" -Force'),
        ("notepad uygulamasını başlat",
         'Start-Process notepad'),
        ("hesap makinesi aç",
         'Start-Process calc'),
        ("belirli bir sürecin PID sini bul",
         'Get-Process | Where-Object { $_.ProcessName -like "*chrome*" } | Select-Object Name, Id'),
        ("şu anda çalışan servisları listele",
         'Get-Service | Where-Object Status -eq "Running" | Select-Object Name, DisplayName'),
        ("durmuş servisleri göster",
         'Get-Service | Where-Object Status -eq "Stopped" | Select-Object Name, DisplayName | Select-Object -First 20'),
        ("görev yöneticisini aç",
         'Start-Process taskmgr'),
        ("uygulamaları çalışma süresine göre listele",
         'Get-Process | Where-Object {$_.StartTime} | Select-Object Name, Id, @{N="Süre";E={(Get-Date) - $_.StartTime}} | Sort-Object Süre -Descending | Select-Object -First 15'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5. GIT — TEMEL KOMUTLAR
    # ═══════════════════════════════════════════════════════
    "Git Temel": [
        ("git versiyonumu göster",
         'git --version'),
        ("git durumunu göster",
         'git status'),
        ("git config kullanıcı adı ayarla",
         'git config --global user.name "Adınız"'),
        ("git config e-posta ayarla",
         'git config --global user.email "email@example.com"'),
        ("git ayarlarımı göster",
         'git config --global --list'),
        ("son 10 commit i göster",
         'git log --oneline -10'),
        ("detaylı commit geçmişini göster",
         'git log --oneline --graph --all -20'),
        ("mevcut branch i göster",
         'git branch'),
        ("tüm branch ları göster uzak dahil",
         'git branch -a'),
        ("uzak repoları göster",
         'git remote -v'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5b. GIT — İŞ AKIŞLARI (ÇOK ADIMLI)
    # ═══════════════════════════════════════════════════════
    "Git İş Akışları": [
        ("bu klasörde git başlat",
         'git init'),
        ("bu projeyi git ile başlat ve ilk commit yap",
         'git init; git add .; git commit -m "ilk commit"'),
        ("bu klasörü github a pushla",
         'git add .; git commit -m "Proje eklendi"; git push origin main'),
        ("bu klasörü ilk kez github a yükle",
         'git init; git add .; git commit -m "ilk commit"; git remote add origin https://github.com/KULLANICI/REPO.git; git branch -M main; git push -u origin main'),
        ("değişiklikleri kaydet ve pushla",
         'git add .; git commit -m "Güncelleme"; git push origin main'),
        ("tüm dosyaları ekle ve commit yap",
         'git add .; git commit -m "Değişiklikler kaydedildi"'),
        ("sadece belirli dosyayı commit et",
         'git add dosya.py; git commit -m "dosya.py güncellendi"'),
        ("commit mesajıyla pushla",
         'git add .; git commit -m "yeni özellik eklendi"; git push'),
        ("uzak repodan son değişiklikleri çek",
         'git pull origin main'),
        ("push öncesi pull yap çakışma olmasın",
         'git pull origin main; git push origin main'),
        ("repoyu klonla",
         'git clone https://github.com/kullanici/repo.git'),
        ("repoyu belirli klasöre klonla",
         'git clone https://github.com/kullanici/repo.git proje-klasoru'),
        ("sadece son commit i klonla hızlı",
         'git clone --depth 1 https://github.com/kullanici/repo.git'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5c. GIT — BRANCH YÖNETİMİ
    # ═══════════════════════════════════════════════════════
    "Git Branch": [
        ("yeni branch oluştur",
         'git checkout -b yeni-ozellik'),
        ("main branch ine geç",
         'git checkout main'),
        ("branch değiştir",
         'git checkout gelistirme'),
        ("branch i sil",
         'git branch -d eski-branch'),
        ("uzak branch i sil",
         'git push origin --delete eski-branch'),
        ("branch i main e birleştir",
         'git checkout main; git merge yeni-ozellik'),
        ("branch i pushla",
         'git push -u origin yeni-ozellik'),
        ("branch i rebase et",
         'git checkout yeni-ozellik; git rebase main'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5d. GIT — GERİ ALMA ve KURTARMA
    # ═══════════════════════════════════════════════════════
    "Git Geri Alma": [
        ("son commit i geri al dosyaları koru",
         'git reset --soft HEAD~1'),
        ("son commit i tamamen geri al",
         'git reset --hard HEAD~1'),
        ("son commit i güvenli geri al",
         'git revert HEAD'),
        ("commit edilmemiş değişiklikleri sıfırla",
         'git checkout -- .'),
        ("staged dosyaları unstage yap",
         'git reset HEAD .'),
        ("belirli dosyadaki değişiklikleri geri al",
         'git checkout -- dosya.py'),
        ("silinen dosyayı geri getir",
         'git checkout HEAD -- silinen_dosya.py'),
        ("değişiklikleri geçici sakla stash",
         'git stash'),
        ("stash i geri yükle",
         'git stash pop'),
        ("stash listesini göster",
         'git stash list'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5e. GIT — .GITIGNORE ŞABLONLARI
    # ═══════════════════════════════════════════════════════
    "Git Ignore": [
        ("python projesi için gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value "__pycache__/`n*.pyc`n*.pyo`n*.egg-info/`ndist/`nbuild/`n.eggs/`nvenv/`nenv/`n.env`n*.db`n.vscode/`n.idea/`n*.log"'),
        ("node projesi için gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value "node_modules/`ndist/`nbuild/`n.env`n.env.local`n*.log`nnpm-debug.log*`n.vscode/`n.idea/`ncoverage/`n.next/`n.nuxt/"'),
        ("csharp projesi için gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value "bin/`nobj/`n.vs/`n*.user`n*.suo`n*.cache`npackages/`n*.nupkg`n.idea/`n*.log`nTestResults/"'),
        ("java projesi için gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value "target/`n*.class`n*.jar`n*.war`n.idea/`n*.iml`n.gradle/`nbuild/`nout/`n.settings/"'),
        ("react projesi için gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value "node_modules/`nbuild/`ndist/`n.env`n.env.local`n.env.production`n*.log`n.vscode/`ncoverage/`n.cache/"'),
        ("genel gitignore oluştur",
         'Set-Content -Path ".gitignore" -Value ".env`n*.log`n.vscode/`n.idea/`n*.tmp`n*.bak`nThumbs.db`n.DS_Store`n*.swp"'),
        ("gitignore a yeni satır ekle",
         'Add-Content -Path ".gitignore" -Value "`nnode_modules/"'),
        ("gitignore dosyasını göster",
         'Get-Content ".gitignore"'),
        ("gitignore ı güncelle ve cache temizle",
         'git rm -r --cached .; git add .; git commit -m "gitignore guncellendi"'),
        ("node_modules u git ten çıkar",
         'git rm -r --cached node_modules; Add-Content -Path ".gitignore" -Value "`nnode_modules/"; git add .; git commit -m "node_modules gitignore a eklendi"'),
        ("pycache dosyalarını git ten çıkar",
         'git rm -r --cached __pycache__; Add-Content -Path ".gitignore" -Value "`n__pycache__/`n*.pyc"; git add .; git commit -m "pycache gitignore a eklendi"'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5f. GIT — SORUN GİDERME
    # ═══════════════════════════════════════════════════════
    "Git Sorun Giderme": [
        ("push rejected hatası çözümü",
         'git pull --rebase origin main; git push origin main'),
        ("merge conflict çözdükten sonra devam et",
         'git add .; git commit -m "Merge conflict cozuldu"'),
        ("detached HEAD durumundan kurtul",
         'git checkout main'),
        ("uzak repo URL sini değiştir",
         'git remote set-url origin https://github.com/KULLANICI/YENI-REPO.git'),
        ("uzak repo ekle",
         'git remote add origin https://github.com/KULLANICI/REPO.git'),
        ("tüm değişiklikleri sil temiz başla",
         'git clean -fd; git checkout -- .'),
        ("commit mesajını değiştir son commit",
         'git commit --amend -m "Düzeltilmiş mesaj"'),
        ("dosyadaki değişiklikleri göster",
         'git diff'),
        ("staged değişiklikleri göster",
         'git diff --staged'),
        ("hangi dosyalar değişmiş göster",
         'git diff --name-only'),
        ("belirli commit teki değişiklikleri göster",
         'git show HEAD'),
    ],

    # ═══════════════════════════════════════════════════════
    #  5g. GIT — TAG ve RELEASE
    # ═══════════════════════════════════════════════════════
    "Git Tag": [
        ("tag oluştur",
         'git tag -a v1.0 -m "Versiyon 1.0"'),
        ("tüm tag ları göster",
         'git tag -l'),
        ("tag i pushla",
         'git push origin v1.0'),
        ("tüm tag ları pushla",
         'git push origin --tags'),
        ("tag sil",
         'git tag -d v1.0'),
        ("uzak tag sil",
         'git push origin --delete v1.0'),
    ],

    # ═══════════════════════════════════════════════════════
    #  6. PYTHON
    # ═══════════════════════════════════════════════════════
    "Python": [
        ("python versiyonumu göster",
         'python --version'),
        ("pip versiyonumu göster",
         'pip --version'),
        ("pip ile requests kütüphanesini kur",
         'pip install requests'),
        ("pip ile birden fazla paket kur",
         'pip install flask django numpy'),
        ("yüklü pip paketlerini listele",
         'pip list'),
        ("pip paketini güncelle",
         'pip install --upgrade pip'),
        ("requirements.txt oluştur",
         'pip freeze > requirements.txt'),
        ("requirements.txt den paketleri kur",
         'pip install -r requirements.txt'),
        ("bir paketi kaldır",
         'pip uninstall requests -y'),
        ("sanal ortam oluştur",
         'python -m venv venv'),
        ("sanal ortamı aktif et",
         '.\\venv\\Scripts\\Activate'),
        ("python dosyasını çalıştır",
         'python script.py'),
        ("python ile basit http sunucu başlat",
         'python -m http.server 8000'),
        ("pip cache i temizle",
         'pip cache purge'),
        ("belirli versiyon kur",
         'pip install numpy==1.24.0'),
    ],

    # ═══════════════════════════════════════════════════════
    #  7. NODE.JS ve NPM
    # ═══════════════════════════════════════════════════════
    "Node.js ve NPM": [
        ("node versiyonumu göster",
         'node --version'),
        ("npm versiyonumu göster",
         'npm --version'),
        ("npm ile express paketini kur",
         'npm install express'),
        ("npm ile global paket kur",
         'npm install -g nodemon'),
        ("yeni node projesi başlat",
         'npm init -y'),
        ("node modules u sil ve yeniden kur",
         'Remove-Item -Path "node_modules" -Recurse -Force; npm install'),
        ("npm paketlerini güncelle",
         'npm update'),
        ("npm güvenlik taraması yap",
         'npm audit'),
        ("npx ile create-react-app çalıştır",
         'npx -y create-react-app my-app'),
        ("geliştirme sunucusunu başlat",
         'npm run dev'),
        ("projeyi build et",
         'npm run build'),
        ("yüklü global paketleri göster",
         'npm list -g --depth=0'),
        ("npm cache temizle",
         'npm cache clean --force'),
    ],

    # ═══════════════════════════════════════════════════════
    #  8. DOCKER
    # ═══════════════════════════════════════════════════════
    "Docker": [
        ("docker versiyonunu göster",
         'docker --version'),
        ("çalışan container ları göster",
         'docker ps'),
        ("tüm container ları göster",
         'docker ps -a'),
        ("docker image larını listele",
         'docker images'),
        ("nginx container ı başlat",
         'docker run -d -p 80:80 nginx'),
        ("container ı durdur",
         'docker stop container_id'),
        ("container ı sil",
         'docker rm container_id'),
        ("image sil",
         'docker rmi image_id'),
        ("docker compose başlat",
         'docker-compose up -d'),
        ("docker compose durdur",
         'docker-compose down'),
        ("container loglarını göster",
         'docker logs container_id'),
        ("container a bağlan",
         'docker exec -it container_id bash'),
        ("docker sistem bilgisini göster",
         'docker system info'),
        ("kullanılmayan docker objelerini temizle",
         'docker system prune -f'),
    ],

    # ═══════════════════════════════════════════════════════
    #  9. SIKIŞTURMA VE ARŞİVLEME
    # ═══════════════════════════════════════════════════════
    "Sıkıştırma ve Arşivleme": [
        ("masaüstündeki proje klasörünü zip le",
         'Compress-Archive -Path "$env:USERPROFILE\\Desktop\\proje" -DestinationPath "$env:USERPROFILE\\Desktop\\proje.zip"'),
        ("masaüstündeki arsiv.zip dosyasını aç",
         'Expand-Archive -Path "$env:USERPROFILE\\Desktop\\arsiv.zip" -DestinationPath "$env:USERPROFILE\\Desktop\\arsiv"'),
        ("birden fazla dosyayı zip le",
         'Compress-Archive -Path "$env:USERPROFILE\\Desktop\\dosya1.txt","$env:USERPROFILE\\Desktop\\dosya2.txt" -DestinationPath "$env:USERPROFILE\\Desktop\\dosyalar.zip"'),
        ("zip dosyasının içeriğini göster açmadan",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop\\arsiv.zip" | ForEach-Object { [IO.Compression.ZipFile]::OpenRead($_.FullName).Entries.Name }'),
        ("mevcut zip e dosya ekle",
         'Compress-Archive -Path "$env:USERPROFILE\\Desktop\\ekdosya.txt" -DestinationPath "$env:USERPROFILE\\Desktop\\arsiv.zip" -Update'),
    ],

    # ═══════════════════════════════════════════════════════
    #  10. METİN ARAMA VE İŞLEME
    # ═══════════════════════════════════════════════════════
    "Metin Arama ve İşleme": [
        ("masaüstündeki log.txt dosyasında hata kelimesini ara",
         'Select-String -Path "$env:USERPROFILE\\Desktop\\log.txt" -Pattern "hata"'),
        ("bir klasördeki tüm dosyalarda belirli metni ara",
         'Get-ChildItem -Path "$env:USERPROFILE\\Desktop\\proje" -Recurse -File | Select-String -Pattern "TODO"'),
        ("dosyadaki satır sayısını göster",
         'Get-Content "$env:USERPROFILE\\Desktop\\test.txt" | Measure-Object -Line'),
        ("dosyanın ilk 10 satırını göster",
         'Get-Content "$env:USERPROFILE\\Desktop\\test.txt" -Head 10'),
        ("dosyanın son 5 satırını göster",
         'Get-Content "$env:USERPROFILE\\Desktop\\test.txt" -Tail 5'),
        ("dosyada bir kelimeyi başka bir kelimeyle değiştir",
         '(Get-Content "$env:USERPROFILE\\Desktop\\test.txt") -replace "eski","yeni" | Set-Content "$env:USERPROFILE\\Desktop\\test.txt"'),
        ("dosyadaki boş satırları sil",
         'Get-Content "$env:USERPROFILE\\Desktop\\test.txt" | Where-Object { $_.Trim() -ne "" } | Set-Content "$env:USERPROFILE\\Desktop\\test_temiz.txt"'),
        ("iki dosyanın farkını göster",
         'Compare-Object (Get-Content "$env:USERPROFILE\\Desktop\\dosya1.txt") (Get-Content "$env:USERPROFILE\\Desktop\\dosya2.txt")'),
    ],

    # ═══════════════════════════════════════════════════════
    #  11. TARAYICI KOMUTLARI
    # ═══════════════════════════════════════════════════════
    "Tarayıcı Komutları": [
        ("google ı tarayıcıda aç",
         'Start-Process "https://www.google.com"'),
        ("github ı tarayıcıda aç",
         'Start-Process "https://www.github.com"'),
        ("youtube u tarayıcıda aç",
         'Start-Process "https://www.youtube.com"'),
        ("stackoverflow u aç",
         'Start-Process "https://www.stackoverflow.com"'),
        ("chatgpt yi aç",
         'Start-Process "https://chat.openai.com"'),
        ("belirli bir URL yi aç",
         'Start-Process "https://example.com"'),
        ("localhost 3000 i tarayıcıda aç",
         'Start-Process "http://localhost:3000"'),
    ],

    # ═══════════════════════════════════════════════════════
    #  12. GÜVENLİK VE KULLANICI YÖNETİMİ
    # ═══════════════════════════════════════════════════════
    "Güvenlik ve Kullanıcı": [
        ("yerel kullanıcıları listele",
         'Get-LocalUser | Select-Object Name, Enabled, LastLogon'),
        ("yerel grupları göster",
         'Get-LocalGroup'),
        ("yönetici grubundaki kullanıcıları göster",
         'Get-LocalGroupMember -Group "Administrators"'),
        ("güvenlik duvarı durumunu göster",
         'Get-NetFirewallProfile | Select-Object Name, Enabled'),
        ("güvenlik duvarı kurallarını göster",
         'Get-NetFirewallRule -Enabled True | Select-Object DisplayName, Direction, Action | Select-Object -First 20'),
        ("Windows Defender durumunu göster",
         'Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated'),
        ("hızlı virüs taraması başlat",
         'Start-MpScan -ScanType QuickScan'),
        ("execution policy yi göster",
         'Get-ExecutionPolicy -List'),
    ],

    # ═══════════════════════════════════════════════════════
    #  13. ZAMANLANMIŞ GÖREVLER
    # ═══════════════════════════════════════════════════════
    "Zamanlanmış Görevler": [
        ("zamanlanmış görevleri listele",
         'Get-ScheduledTask | Where-Object {$_.State -ne "Disabled"} | Select-Object TaskName, State | Select-Object -First 20'),
        ("belirli bir görevi göster",
         'Get-ScheduledTask -TaskName "GoogleUpdate*" | Select-Object TaskName, State, Description'),
        ("zamanlanmış görev oluştur",
         'Register-ScheduledTask -TaskName "Yedekleme" -Trigger (New-ScheduledTaskTrigger -Daily -At 9am) -Action (New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-Command Write-Host Yedekleme")'),
    ],

    # ═══════════════════════════════════════════════════════
    #  14. WİNDOWS SERVİSLERİ
    # ═══════════════════════════════════════════════════════
    "Windows Servisleri": [
        ("tüm servisleri listele",
         'Get-Service | Select-Object Name, DisplayName, Status | Sort-Object Status'),
        ("çalışan servisleri göster",
         'Get-Service | Where-Object Status -eq "Running" | Select-Object DisplayName, Status'),
        ("durmuş servisleri göster",
         'Get-Service | Where-Object Status -eq "Stopped" | Select-Object DisplayName | Select-Object -First 20'),
        ("belirli bir servisi ara",
         'Get-Service | Where-Object { $_.DisplayName -like "*print*" } | Select-Object Name, DisplayName, Status'),
        ("bir servisi başlat",
         'Start-Service -Name "Spooler"'),
        ("bir servisi durdur",
         'Stop-Service -Name "Spooler"'),
        ("bir servisi yeniden başlat",
         'Restart-Service -Name "Spooler"'),
    ],

    # ═══════════════════════════════════════════════════════
    #  15. DİSK VE DEPOLAMA
    # ═══════════════════════════════════════════════════════
    "Disk ve Depolama": [
        ("disk bilgilerini göster",
         'Get-PhysicalDisk | Select-Object MediaType, Model, Size, HealthStatus'),
        ("disk bölümlerini göster",
         'Get-Partition | Select-Object DiskNumber, PartitionNumber, DriveLetter, Size, Type'),
        ("disk kullanım yüzdelerini göster",
         'Get-Volume | Select-Object DriveLetter, FileSystemLabel, @{N="Boyut(GB)";E={[math]::Round($_.Size/1GB,2)}}, @{N="Boş(GB)";E={[math]::Round($_.SizeRemaining/1GB,2)}}'),
        ("geri dönüşüm kutusunu boşalt",
         'Clear-RecycleBin -Force'),
        ("geçici dosyaları temizle",
         'Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue'),
        ("en büyük 20 dosyayı bul C diskinde",
         'Get-ChildItem -Path "C:\\" -Recurse -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 20 FullName, @{N="MB";E={[math]::Round($_.Length/1MB,2)}}'),
    ],

    # ═══════════════════════════════════════════════════════
    #  16. ÇEVRE DEĞİŞKENLERİ
    # ═══════════════════════════════════════════════════════
    "Çevre Değişkenleri": [
        ("tüm ortam değişkenlerini göster",
         'Get-ChildItem Env: | Sort-Object Name'),
        ("PATH değişkenini güzel göster",
         '$env:PATH -split ";" | ForEach-Object { $_ }'),
        ("yeni ortam değişkeni oluştur geçici",
         '$env:MY_VAR = "değer"'),
        ("JAVA_HOME değişkenini göster",
         '$env:JAVA_HOME'),
        ("kullanıcı profil yolunu göster",
         '$env:USERPROFILE'),
        ("geçici dosya yolunu göster",
         '$env:TEMP'),
    ],

    # ═══════════════════════════════════════════════════════
    #  17. WINDOWS AYARLARI
    # ═══════════════════════════════════════════════════════
    "Windows Ayarları": [
        ("ses seviyesini göster",
         'Get-AudioDevice -PlaybackVolume'),
        ("ekran çözünürlüğünü göster",
         'Get-CimInstance Win32_VideoController | Select-Object CurrentHorizontalResolution, CurrentVerticalResolution'),
        ("saat dilimini göster",
         'Get-TimeZone'),
        ("sistem saatini göster",
         'Get-Date'),
        ("tarih ve saati formatla",
         'Get-Date -Format "dd.MM.yyyy HH:mm:ss"'),
        ("kontrol panelini aç",
         'Start-Process control'),
        ("ayarları aç",
         'Start-Process ms-settings:'),
        ("cihaz yöneticisini aç",
         'Start-Process devmgmt.msc'),
        ("disk yönetimini aç",
         'Start-Process diskmgmt.msc'),
        ("event viewer aç",
         'Start-Process eventvwr.msc'),
    ],

    # ═══════════════════════════════════════════════════════
    #  18. SSH VE UZAK BAĞLANTI
    # ═══════════════════════════════════════════════════════
    "SSH ve Uzak Bağlantı": [
        ("ssh yüklü mü kontrol et",
         'ssh -V'),
        ("ssh anahtar çifti oluştur",
         'ssh-keygen -t ed25519 -C "email@example.com"'),
        ("mevcut ssh anahtarlarını göster",
         'Get-ChildItem "$env:USERPROFILE\\.ssh"'),
        ("uzak sunucuya ssh ile bağlan",
         'ssh kullanici@sunucu-ip'),
        ("scp ile dosya gönder",
         'scp dosya.txt kullanici@sunucu-ip:/hedef/yol/'),
        ("scp ile dosya indir",
         'scp kullanici@sunucu-ip:/uzak/dosya.txt "$env:USERPROFILE\\Desktop"'),
    ],

    # ═══════════════════════════════════════════════════════
    #  19. PAKET YÖNETİCİLERİ (WINGET / CHOCO)
    # ═══════════════════════════════════════════════════════
    "Paket Yöneticileri": [
        ("winget ile uygulama ara",
         'winget search "Visual Studio Code"'),
        ("winget ile uygulama kur",
         'winget install "Microsoft.VisualStudioCode"'),
        ("winget ile uygulama güncelle",
         'winget upgrade --all'),
        ("winget ile yüklü uygulamaları göster",
         'winget list'),
        ("winget ile uygulama kaldır",
         'winget uninstall "Microsoft.VisualStudioCode"'),
        ("chocolatey ile paket kur",
         'choco install nodejs -y'),
        ("chocolatey ile paketleri güncelle",
         'choco upgrade all -y'),
        ("chocolatey yüklü paketleri göster",
         'choco list'),
    ],

    # ═══════════════════════════════════════════════════════
    #  20. PERFORMANS İZLEME
    # ═══════════════════════════════════════════════════════
    "Performans İzleme": [
        ("CPU kullanımını göster",
         'Get-CimInstance Win32_Processor | Select-Object LoadPercentage'),
        ("RAM kullanımını göster",
         'Get-CimInstance Win32_OperatingSystem | Select-Object @{N="Toplam(GB)";E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{N="Kullanılan(GB)";E={[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)/1MB,2)}}'),
        ("disk I/O istatistiklerini göster",
         'Get-Counter "\\PhysicalDisk(_Total)\\Disk Read Bytes/sec","\\PhysicalDisk(_Total)\\Disk Write Bytes/sec" -SampleInterval 1 -MaxSamples 1'),
        ("ağ trafiğini izle",
         'Get-Counter "\\Network Interface(*)\\Bytes Total/sec" -SampleInterval 1 -MaxSamples 3'),
        ("sistem event loglarını göster",
         'Get-EventLog -LogName System -Newest 10 | Select-Object TimeGenerated, EntryType, Message'),
        ("uygulama hatalarını göster",
         'Get-EventLog -LogName Application -EntryType Error -Newest 10 | Select-Object TimeGenerated, Source, Message'),
    ],

    # ═══════════════════════════════════════════════════════
    #  21. POWERSHELL İPUÇLARI
    # ═══════════════════════════════════════════════════════
    "PowerShell İpuçları": [
        ("komut geçmişini göster",
         'Get-History'),
        ("komutu alias ile bul",
         'Get-Alias | Where-Object { $_.Definition -like "*Item*" }'),
        ("bir komutun yardımını göster",
         'Get-Help Get-Process -Examples'),
        ("powershell profilini göster",
         '$PROFILE'),
        ("powershell versiyonunu göster",
         '$PSVersionTable'),
        ("clipboard a metin kopyala",
         '"Merhaba" | Set-Clipboard'),
        ("clipboard daki metni göster",
         'Get-Clipboard'),
        ("son çalıştırılan komutu tekrarla",
         'Invoke-History'),
    ],
}


def ilgili_ornekleri_sec(kullanici_istegi: str, max_ornek: int = 12) -> list[tuple[str, str]]:
    """
    Kullanıcının isteğine en uygun örnekleri seçer (basit RAG).
    Tüm 223 örneği göndermek yerine sadece en alakalı ~12 tanesini seçer.
    Bu sayede modelin token limiti aşılmaz ve 400 hatası alınmaz.
    
    Mantık: İstekteki kelimelerin kaç tanesi örneğin istek metninde geçiyor?
    En çok eşleşen örnekler seçilir.
    """
    istek_lower = kullanici_istegi.lower()
    # Türkçe stop-word'leri çıkar (anlamsız kelimeler)
    stop_words = {"bir", "ve", "ile", "bu", "şu", "o", "da", "de", "mi", "mı",
                  "ne", "için", "bana", "benim", "lütfen", "yap", "et", "ol",
                  "tüm", "tümü", "olan", "var", "yok", "nasıl", "kadar"}
    kelimeler = [k for k in istek_lower.split() if k not in stop_words and len(k) > 1]
    
    # Her örneği puan ile skorla
    skorlu_ornekler = []
    for kategori, ornekler in KOMUT_ORNEKLERI.items():
        for istek, komut in ornekler:
            istek_l = istek.lower()
            # Kaç anahtar kelime eşleşiyor?
            skor = sum(1 for k in kelimeler if k in istek_l)
            # Kategori adı eşleşiyorsa bonus puan
            if any(k in kategori.lower() for k in kelimeler):
                skor += 0.5
            if skor > 0:
                skorlu_ornekler.append((skor, istek, komut))
    
    # Skora göre sırala, en alakalıları al
    skorlu_ornekler.sort(key=lambda x: x[0], reverse=True)
    secilen = [(istek, komut) for _, istek, komut in skorlu_ornekler[:max_ornek]]
    
    # Eğer hiç eşleşme yoksa, her kategoriden 1 tane temel örnek al
    if not secilen:
        for kategori, ornekler in KOMUT_ORNEKLERI.items():
            if ornekler:
                secilen.append(ornekler[0])
            if len(secilen) >= max_ornek:
                break
    
    return secilen


# ──────────────────────────────────────────────────────────
#  TEMEL SİSTEM PROMPTU – TÜRKÇE
# ──────────────────────────────────────────────────────────
TEMEL_PROMPT_TR = """Sen bir Windows PowerShell terminal asistanısın.

═══════════════════════════════════════════
  MUTLAK YANIT FORMATI — BUNA %100 UYACAKSIN
═══════════════════════════════════════════

Yanıtını KESİNLİKLE ve SADECE şu iki satırdan oluştur:
AÇIKLAMA: [Yapılacak işlemin Türkçe kısa özeti]
KOMUT: [Sadece saf PowerShell komutu]

BAŞKA HİÇBİR ŞEY YAZMA. Markdown yok. Kod bloğu yok. Ek açıklama yok.

═══════════════════════════════════════════
  ZORUNLU TEKNİK KURALLAR
═══════════════════════════════════════════

KURAL 1 — YOL YAZIMI:
  ✅ DOĞRU: "$env:USERPROFILE\\Desktop\\klasör adı"
  ❌ YANLIŞ: "$env:USERPROFILE\\Desktop'klasör adı'"
  ❌ YANLIŞ: ~/Desktop/klasör
  Her zaman $env:USERPROFILE kullan. Yolları MUTLAKA çift tırnak içine al.

KURAL 2 — KOMUT SEÇİMİ:
  ✅ Klasör: New-Item -ItemType Directory -Path "yol"
  ✅ Dosya: New-Item -ItemType File -Path "yol"
  ✅ Silme: Remove-Item -Path "yol"
  ✅ Kopyalama: Copy-Item -Path "kaynak" -Destination "hedef"
  ✅ Taşıma: Move-Item -Path "kaynak" -Destination "hedef"
  ✅ Listeleme: Get-ChildItem -Path "yol"
  ❌ ASLA md, mkdir, rm, rmdir, del, dir, copy, move KULLANMA
  ❌ ASLA Linux/bash komutları kullanma (ls, cat, cp, mv, touch)

KURAL 3 — Türkçe karakterli yollar çift tırnak içinde olmalı.
KURAL 4 — Her zaman TEK komut satırı döndür. Çoklu komut: noktalı virgül (;) ile ayır.
KURAL 5 — Kullanıcı açıkça istemedikçe -Force ekleme.

KURAL 6 — GIT İŞ AKIŞLARI:
  Git işlemleri genelde çok adımlıdır, adımları noktalı virgül (;) ile zincirle.
  ✅ Push istendi: git add .; git commit -m "mesaj"; git push origin main
  ❌ ASLA tek başına "git push" deme — önce add ve commit OLMALI.
  ❌ ASLA .gitignore olmadan push önerme.
  Push/pull sorunlarında önce git pull --rebase origin main yap.
"""

# ──────────────────────────────────────────────────────────
#  TEMEL SİSTEM PROMPTU – ENGLISH
# ──────────────────────────────────────────────────────────
TEMEL_PROMPT_EN = """You are a Windows PowerShell terminal assistant.

═══════════════════════════════════════════
  ABSOLUTE RESPONSE FORMAT — YOU MUST FOLLOW THIS 100%
═══════════════════════════════════════════

Your response MUST consist of EXACTLY these two lines:
DESCRIPTION: [Short summary of what will be done, in English]
COMMAND: [Only the raw PowerShell command]

WRITE NOTHING ELSE. No markdown. No code blocks. No extra explanation.

═══════════════════════════════════════════
  MANDATORY TECHNICAL RULES
═══════════════════════════════════════════

RULE 1 — PATH FORMAT:
  ✅ CORRECT: "$env:USERPROFILE\\Desktop\\folder name"
  ❌ WRONG: "$env:USERPROFILE\\Desktop'folder name'"
  ❌ WRONG: ~/Desktop/folder
  Always use $env:USERPROFILE. ALWAYS wrap paths in double quotes.

RULE 2 — COMMAND SELECTION:
  ✅ Folder: New-Item -ItemType Directory -Path "path"
  ✅ File: New-Item -ItemType File -Path "path"
  ✅ Delete: Remove-Item -Path "path"
  ✅ Copy: Copy-Item -Path "source" -Destination "dest"
  ✅ Move: Move-Item -Path "source" -Destination "dest"
  ✅ List: Get-ChildItem -Path "path"
  ❌ NEVER use md, mkdir, rm, rmdir, del, dir, copy, move
  ❌ NEVER use Linux/bash commands (ls, cat, cp, mv, touch)

RULE 3 — Special characters in paths must be inside double quotes.
RULE 4 — Always return a SINGLE command line. Multiple commands: separate with semicolons (;).
RULE 5 — Never add -Force unless the user explicitly asks for it.

RULE 6 — GIT WORKFLOWS:
  Git operations are usually multi-step; chain them with semicolons (;).
  ✅ Push requested: git add .; git commit -m "message"; git push origin main
  ❌ NEVER just "git push" alone — add and commit MUST come first.
  ❌ NEVER suggest push without .gitignore.
  On push/pull issues, use git pull --rebase origin main first.
"""

# Geriye uyumluluk
TEMEL_PROMPT = TEMEL_PROMPT_TR


def dinamik_prompt_olustur(kullanici_istegi: str, dil: str = "tr") -> str:
    """
    Kullanıcının isteğine göre dinamik prompt oluşturur.
    dil: "tr" veya "en" — AI'ın yanıt dilini belirler.
    """
    # Dile göre temel prompt seç
    if dil == "en":
        temel = TEMEL_PROMPT_EN
        desc_key = "DESCRIPTION"
        cmd_key = "COMMAND"
        req_key = "REQUEST"
    else:
        temel = TEMEL_PROMPT_TR
        desc_key = "AÇIKLAMA"
        cmd_key = "KOMUT"
        req_key = "İSTEK"

    ornekler = ilgili_ornekleri_sec(kullanici_istegi)

    ornek_metni = "\n═══════════════════════════════════════════\n  REFERANS ÖRNEKLER\n═══════════════════════════════════════════\n"
    for istek, komut in ornekler:
        ornek_metni += f"{req_key}: {istek}\n{desc_key}: {istek.capitalize()}\n{cmd_key}: {komut}\n\n"

    return temel + ornek_metni


# Eski fonksiyon — geriye uyumluluk
def sistem_promptu_olustur() -> str:
    return TEMEL_PROMPT_TR


# Toplam örnek sayısını hesapla
def toplam_ornek_sayisi() -> int:
    return sum(len(v) for v in KOMUT_ORNEKLERI.values())

