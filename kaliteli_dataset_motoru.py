import json
import random
import re

# 🔥 COMMAND VALIDATOR (V7 Pro Regex)
def validate_command(cmd):
    patterns = [
        r"rm\s+-rf\s+[/\\]",
        r"format\s+[a-z]:",
        r"del\s+.*c:\\",
        r"rd\s+/s\s+/q\s+c:\\",
        r"remove-item.*c:\\(windows|system32)",
        r"powershell\s+-command\s+remove-item\s+c:\\"
    ]
    cmd_lower = cmd.lower()
    for p in patterns:
        if re.search(p, cmd_lower):
            return False
    return True

# 🧠 SYSTEM PROMPTS (V7 Direct Buyrugan Token Format)
def get_system_prompt(dil="tr", only_cmd=True):
    if dil == "tr":
        return "Sen bir Windows Terminal yapay zekasısın. SADECE type ve content değerlerini içeren bir JSON objesi döndür. Markdown veya ekstra açıklama kullanma."
    else:
        return "You are a Windows terminal AI. Output strictly a JSON object with keys: type, content. No extra text, no markdown."

def json_build(cevap_tipi, icerik, aciklama=None):
    if cevap_tipi == "command" and aciklama:
        data = {"type": "command_explained", "explain": aciklama, "content": icerik}
    else:
        data = {"type": cevap_tipi, "content": icerik}
    return json.dumps(data, ensure_ascii=False)

# 🌌 DEVASA DEĞİŞKEN HAVUZU
KLASORLER = ["frontend", "backend", "api", "src", "public", "scripts", "build", "core", "docker", "utils", "components", "pages", "assets", "styles", "middleware", "controllers", "models", "routes", "config", "tests", "lib", "static", "views", "helpers", "services", "hooks", "store", "reducers", "constants", "locales", ".github", ".vscode", "certs", "db", "logs"]
DOSYALAR = ["app.py", "index.html", "main.js", "style.css", "server.js", "docker-compose.yml", "requirements.txt", ".env", "package.json", "tsconfig.json", "webpack.config.js", "vite.config.js", "manage.py", "db.sqlite3", "Dockerfile", ".gitignore", "README.md", "setup.py", "pytest.ini", "jest.config.js", "tailwind.config.js", "babel.config.json", "prettierrc.json", "nodemon.json", ".eslintrc", "yarn.lock", "pom.xml"]
BRANCHLER = ["main", "master", "dev", "feature/login", "bugfix/header", "hotfix/urgent", "release/v1", "feature/payment", "refactor/api", "test/e2e", "chore/deps", "hotfix/auth", "feature/cart"]
PAKETLER = ["express", "react", "django", "numpy", "pandas", "axios", "typescript", "tailwindcss", "flask", "mongoose", "lodash", "pytest", "webpack", "vite", "jest", "cypress", "prettier", "eslint", "bcrypt", "dotenv", "socket.io", "cors", "helmet"]
PORTLAR = ["80", "443", "8000", "8080", "3000", "5000", "4200", "3306", "5432", "27017", "6379", "9200", "5173", "8888", "1433", "6543", "9090"]

NOISE_TR = ["la", "abi", "kanki", "kanka", "pls", "çabuk", "bi zahmet", "yaa", "acilen", "hemen", "bro"]
NOISE_EN = ["bro", "pls", "quickly", "man", "asap", "mate", "dude", "fr", "cmon", "fast", "urgent", "yo"]

# 🗑️ EDGE CASE (Real Edge Cases: Typos, White spaces, Mixing, Halfs)
EDGE_CASE_INPUT = ["git res", "gti clone", "npm isnyall", "abi delete file pls", "şu dosyayı rm f yap", "   ", "rm maybe?", "docker ps -", "del f -", "cls pls abi", "cd.. abi"]
EDGE_CEVAP = "ERROR: invalid input"

# 🛡️ NEGATİF (HACKER) VE SELF-CORRECTION
NEGATIVE_TR = ["sistem klasörünü formatla", "sistem32 dizinini sil at", "Remove-Item C:\\Windows -Force -Recurse", "del C:\\ /s /q /f", "rm -rf /", "rd /s /q c:\\]"]
NEGATIVE_EN = ["format system drive", "delete system32", "rm -rf /", "destroy the windows folder", "del /s /q c:\\]"]
REFUSAL_TR = "REFUSED: unsafe system operation detected"
REFUSAL_EN = "BLOCKED: destructive command"

# 🔥 CONTRAST / SELF-CORRECTION PAIRS
CONTRAST_PAIRS_TR = [
    {"bad": "sistemi sil yok et", "good": "sadece tmp klasörünü sil", "c": "Remove-Item -Recurse -Force C:\\Temp\\*"},
    {"bad": "tum diski formatla c yi falan", "good": "sadece build klasörünü sıfırla", "c": "Remove-Item -Recurse -Force build\\*"},
]
CONTRAST_PAIRS_EN = [
    {"bad": "rm -rf /", "good": "delete only the dist folder", "c": "Remove-Item -Recurse -Force dist"},
    {"bad": "format the c drive cleanly", "good": "clean the temp folder completely", "c": "Remove-Item -Recurse -Force $env:TEMP\\*"},
]

REAL_KNOWLEDGE_TR = [
    {"u": "{port} kullanan süreci bul ve öldür", "c": "Stop-Process -Id (Get-NetTCPConnection -LocalPort {port}).OwningProcess -Force"},
    {"u": "dns önbelleğini temizle", "c": "Clear-DnsClientCache; ipconfig /flushdns"},
    {"u": "tüm ip ayarlarını ve mac i göster", "c": "ipconfig /all"},
    {"u": "hangi portlar dinleniyor bak", "c": "netstat -ano | findstr LISTENING"},
    {"u": "tcp bağlantıları ne alemde", "c": "Get-NetTCPConnection | Where-Object State -eq Established"},
    {"u": "dış ip adresimi öğren", "c": "(Invoke-WebRequest -Uri 'https://api.ipify.org').Content"},
    {"u": "arp tablosunu temizle", "c": "arp -d *"},
    {"u": "duran dockerları kes", "c": "docker system prune -a --volumes -f"},
    {"u": "tüm docker imajlarını listele", "c": "docker images -a"},
    {"u": "docker volume'leri sil", "c": "docker volume prune -f"},
    {"u": "tum docker loglarını tail ile son 50 satır göster", "c": "docker logs --tail 50 {klasor}"},
    {"u": "docker composu arkaplanda çalıştır", "c": "docker-compose up -d"},
    {"u": "tüm docker containerları döngüyle kapat", "c": "docker ps -aq | ForEach-Object {{ docker stop $_ }}"},
    {"u": "tüm dockerları sök", "c": "docker ps -aq | ForEach-Object {{ docker rm -f $_ }}"},
    {"u": "git cache temizle untracked falan uçur", "c": "git clean -fdx"},
    {"u": "eski ve silinmiş branchleri uzak sunucuya bakıp sil", "c": "git fetch -p"},
    {"u": "git logu graph gibi göster", "c": "git log --graph --oneline --all"},
    {"u": "son commitin mesajını ucretsizce değiştir", "c": "git commit --amend -m \"{branch}\""},
    {"u": "commit atmadan değişiklikleri çöpe at", "c": "git reset --hard HEAD"},
    {"u": "git rebase yap mastera", "c": "git fetch; git rebase origin/master"},
    {"u": "tüm git ayarlarımı dök", "c": "git config --list"},
    {"u": "lokal branchleri listele", "c": "git branch -a"},
    {"u": "tar çıkar", "c": "tar -xf {dosya}"},
    {"u": "zip dosyasından çıkar", "c": "Expand-Archive -Path {dosya}.zip -DestinationPath .\\{klasor}"},
    {"u": "{dosya} dosyasının hash koduna sha256 bak", "c": "Get-FileHash '{dosya}' -Algorithm SHA256"},
    {"u": "en büyük 5 dosyayı bul getir", "c": "Get-ChildItem -File -Recurse | Sort-Object Length -Descending | Select-Object -First 5"},
    {"u": "boş klasörleri silsene", "c": "Get-ChildItem -Directory -Recurse | Where-Object {{ $_.GetFiles().Count -eq 0 }} | Remove-Item"},
    {"u": "{klasor} içini tree şeklinde göster", "c": "tree {klasor} /f"},
    {"u": "dosyanın içinden log kelimesi geçenleri bul", "c": "Select-String -Path '{dosya}' -Pattern 'log'"},
    {"u": "dosyadaki satır sayısını say", "c": "(Get-Content '{dosya}').Count"},
    {"u": "disk c nin bos olanı ne", "c": "Get-PSDrive C | Select-Object Used, Free"},
    {"u": "ps yetkisini remotesigned yap", "c": "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"},
    {"u": "{paket} nerede kurulu", "c": "Get-Command {paket} | Select-Object Source"},
    {"u": "ram miktarı nedir", "c": "Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum | % {{ [math]::round(($_.sum / 1GB),2) }} "},
    {"u": "ortam değişkenlerini listele", "c": "Get-ChildItem Env:"},
    {"u": "{klasor} PATH'e ekle", "c": "$env:PATH += ';{klasor}'"},
    {"u": "yönetici yetkili powershell aç", "c": "Start-Process powershell -Verb runAs"},
    {"u": "windows defendırı geçici kapat", "c": "Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue"},
    {"u": "clipboardı kopyalananı terminale bas", "c": "Get-Clipboard"},
    {"u": "şu anki tarihi formattlı ver", "c": "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"},
    {"u": "çalışan süreç isimlerini sırala txt kaydet", "c": "Get-Process | Select-Object ProcessName | Sort-Object ProcessName | Out-File {dosya}"},
    {"u": "son reboottan bu yana geçen süre", "c": "(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime"}
]

REAL_KNOWLEDGE_EN = [
    {"u": "kill anything on port {port}", "c": "Stop-Process -Id (Get-NetTCPConnection -LocalPort {port}).OwningProcess -Force"},
    {"u": "flush dns cache quickly", "c": "Clear-DnsClientCache; ipconfig /flushdns"},
    {"u": "show complete ip properties", "c": "ipconfig /all"},
    {"u": "look at listening ports", "c": "netstat -ano | findstr LISTENING"},
    {"u": "check established tcp connections", "c": "Get-NetTCPConnection | Where-Object State -eq Established"},
    {"u": "what is my public ip", "c": "(Invoke-WebRequest -Uri 'https://api.ipify.org').Content"},
    {"u": "clear arp table", "c": "arp -d *"},
    {"u": "prune old docker caches completely", "c": "docker system prune -a --volumes -f"},
    {"u": "list all docker images", "c": "docker images -a"},
    {"u": "prune docker volumes", "c": "docker volume prune -f"},
    {"u": "tail docker logs last 50 lines", "c": "docker logs --tail 50 {klasor}"},
    {"u": "run docker compose in background", "c": "docker-compose up -d"},
    {"u": "stop dockers using ps pipe foreach", "c": "docker ps -aq | ForEach-Object {{ docker stop $_ }}"},
    {"u": "force remove all dockers pipe", "c": "docker ps -aq | ForEach-Object {{ docker rm -f $_ }}"},
    {"u": "clean untracked git files completely", "c": "git clean -fdx"},
    {"u": "fetch and prune remote branches in git", "c": "git fetch -p"},
    {"u": "git log as graph oneline", "c": "git log --graph --oneline --all"},
    {"u": "amend last commit message", "c": "git commit --amend -m \"{branch}\""},
    {"u": "hard reset git discarding everything", "c": "git reset --hard HEAD"},
    {"u": "rebase from origin master", "c": "git fetch; git rebase origin/master"},
    {"u": "dump git config list", "c": "git config --list"},
    {"u": "list all local branches", "c": "git branch -a"},
    {"u": "extract tar file", "c": "tar -xf {dosya}"},
    {"u": "unzip archive", "c": "Expand-Archive -Path {dosya}.zip -DestinationPath .\\{klasor}"},
    {"u": "check sha256 hash of {dosya}", "c": "Get-FileHash '{dosya}' -Algorithm SHA256"},
    {"u": "find top 5 largest files", "c": "Get-ChildItem -File -Recurse | Sort-Object Length -Descending | Select-Object -First 5"},
    {"u": "remove empty directories", "c": "Get-ChildItem -Directory -Recurse | Where-Object {{ $_.GetFiles().Count -eq 0 }} | Remove-Item"},
    {"u": "tree view of folder", "c": "tree {klasor} /f"},
    {"u": "grep search 'log' in file", "c": "Select-String -Path '{dosya}' -Pattern 'log'"},
    {"u": "count lines in file", "c": "(Get-Content '{dosya}').Count"},
    {"u": "show c drive free space", "c": "Get-PSDrive C | Select-Object Used, Free"},
    {"u": "set ps execution policy remote signed", "c": "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"},
    {"u": "where is {paket} located", "c": "Get-Command {paket} | Select-Object Source"},
    {"u": "show total installed RAM", "c": "Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum | % {{ [math]::round(($_.sum / 1GB),2) }} "},
    {"u": "dump all env variables", "c": "Get-ChildItem Env:"},
    {"u": "append to PATH variable", "c": "$env:PATH += ';{klasor}'"},
    {"u": "run elevated powershell window admin", "c": "Start-Process powershell -Verb runAs"},
    {"u": "disable windows defender realtime monitoring", "c": "Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue"},
    {"u": "paste clipboard to terminal", "c": "Get-Clipboard"},
    {"u": "current date formatted", "c": "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"},
    {"u": "sort processes by name to file", "c": "Get-Process | Select-Object ProcessName | Sort-Object ProcessName | Out-File {dosya}"},
    {"u": "system uptime since boot", "c": "(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime"}
]

SYNTHETIC_TR = [
    {"u": "{klasor} git ve eksikse kur sonra npm init", "c": "if (-not (Test-Path {klasor})) {{ mkdir {klasor} }}; cd {klasor}; npm init -y"},
    {"u": "tüm txt leri {klasor} icine tasi", "c": "Move-Item -Path *.txt -Destination {klasor}"},
    {"u": "son git logu sil ama dosyama dokunma soft reset", "c": "git reset --soft HEAD~1"},
    {"u": "{paket} global npm den indir", "c": "npm install -g {paket}"},
    {"u": "git stash ve {branch} geç", "c": "git stash; git checkout {branch}"},
    {"u": "{dosya} python dosyasını calıştır", "c": "python {dosya}"},
    {"u": "masaustunde {klasor} ac icine gec", "c": "mkdir $env:USERPROFILE\\Desktop\\{klasor}; cd $env:USERPROFILE\\Desktop\\{klasor}"},
    {"u": "{klasor} u komple sil", "c": "Remove-Item -Recurse -Force {klasor} -ErrorAction SilentlyContinue"},
    {"u": "pip install {paket}", "c": "pip install {paket}"}
]

SYNTHETIC_EN = [
    {"u": "go to {klasor} create if missing then npm init", "c": "if (-not (Test-Path {klasor})) {{ mkdir {klasor} }}; cd {klasor}; npm init -y"},
    {"u": "move all txt files to {klasor}", "c": "Move-Item -Path *.txt -Destination {klasor}"},
    {"u": "undo last commit soft reset files intact", "c": "git reset --soft HEAD~1"},
    {"u": "install {paket} globally npm", "c": "npm install -g {paket}"},
    {"u": "stash project changes jump to {branch}", "c": "git stash; git checkout {branch}"},
    {"u": "run py script {dosya}", "c": "python {dosya}"},
    {"u": "create {klasor} on desktop then cd into it", "c": "mkdir $env:USERPROFILE\\Desktop\\{klasor}; cd $env:USERPROFILE\\Desktop\\{klasor}"},
    {"u": "nuke folder {klasor}", "c": "Remove-Item -Recurse -Force {klasor} -ErrorAction SilentlyContinue"},
    {"u": "pip install {paket}", "c": "pip install {paket}"}
]

def formatla_komut(cmd):
    c = cmd.replace("\n", "; ")
    c = re.sub(r";\s*;", ";", c)
    return c.strip()

def egitim_olustur(hedef_sayi_ciftleri=50000, dosya_adi="Kusursuz_Egitim_V7.jsonl"):
    seen = set()
    basarili = 0
    failed_attempts = 0
    
    with open(dosya_adi, "w", encoding="utf-8") as f:
        # Custom helper to write rows
        def write_row(istek_t, cevap_t, istek_e, cevap_e):
            nonlocal basarili, failed_attempts
            
            # Key checks inside JSON format
            h_key = (istek_t, cevap_t)
            if h_key in seen and failed_attempts < 500:
                failed_attempts += 1
                return False
                
            failed_attempts = 0
            seen.add(h_key)
            
            veri_t = {"messages": [
                {"role": "system", "content": get_system_prompt("tr", only_cmd)},
                {"role": "user", "content": istek_t},
                {"role": "assistant", "content": cevap_t}
            ]}
            
            veri_e = {"messages": [
                {"role": "system", "content": get_system_prompt("en", only_cmd)},
                {"role": "user", "content": istek_e},
                {"role": "assistant", "content": cevap_e}
            ]}
            
            f.write(json.dumps(veri_t, ensure_ascii=False) + "\n")
            f.write(json.dumps(veri_e, ensure_ascii=False) + "\n")
            
            basarili += 1
            if basarili % 10000 == 0:
                print(f"Ilerleme: {basarili} cift (Toplam {basarili*2} satir)...")
            return True

        while basarili < hedef_sayi_ciftleri:
            zar = random.random()
            
            uretilen = {
                "klasor": random.choice(KLASORLER),
                "dosya": random.choice(DOSYALAR),
                "branch": random.choice(BRANCHLER),
                "paket": random.choice(PAKETLER),
                "port": random.choice(PORTLAR)
            }
            
            only_cmd = random.random() < 0.8
            
            if zar < 0.05:
                # 🚮 EDGE CASES
                istek_tr = random.choice(EDGE_CASE_INPUT)
                istek_en = random.choice(EDGE_CASE_INPUT)
                cevap_tr = json_build("error", EDGE_CEVAP)
                cevap_en = json_build("error", EDGE_CEVAP)
                write_row(istek_tr, cevap_tr, istek_en, cevap_en)
                
            elif zar < 0.15:
                # 🛡️ CONTRAST / SELF-CORRECTION
                if random.random() > 0.5:
                    # Pure Negative Random
                    istek_tr = random.choice(NEGATIVE_TR)
                    istek_en = random.choice(NEGATIVE_EN)
                    cevap_tr = json_build("refusal", REFUSAL_TR)
                    cevap_en = json_build("refusal", REFUSAL_EN)
                    write_row(istek_tr, cevap_tr, istek_en, cevap_en)
                else:
                    # V7 Contrast: Emit BOTH the bad and the good to ensure perfect memory distribution!
                    pair_tr = random.choice(CONTRAST_PAIRS_TR)
                    pair_en = random.choice(CONTRAST_PAIRS_EN)
                    
                    # EMIT BAD FIRST
                    i_bad_tr = pair_tr["bad"]
                    i_bad_en = pair_en["bad"]
                    c_bad_tr = json_build("refusal", REFUSAL_TR)
                    c_bad_en = json_build("refusal", REFUSAL_EN)
                    write_row(i_bad_tr, c_bad_tr, i_bad_en, c_bad_en)
                    
                    if basarili >= hedef_sayi_ciftleri: break
                    
                    # EMIT GOOD SECOND
                    i_good_tr = pair_tr["good"]
                    i_good_en = pair_en["good"]
                    cmd_tr = formatla_komut(pair_tr["c"])
                    cmd_en = formatla_komut(pair_en["c"])
                    if not validate_command(cmd_tr): continue
                    
                    c_good_tr = json_build("command", cmd_tr)
                    c_good_en = json_build("command", cmd_en)
                    write_row(i_good_tr, c_good_tr, i_good_en, c_good_en)

            elif zar < 0.70:
                # 📚 REAL DATA
                idx = random.randint(0, len(REAL_KNOWLEDGE_TR)-1)
                u_tr = REAL_KNOWLEDGE_TR[idx]["u"].format(**uretilen)
                c_tr = formatla_komut(REAL_KNOWLEDGE_TR[idx]["c"].format(**uretilen))
                u_en = REAL_KNOWLEDGE_EN[idx]["u"].format(**uretilen)
                c_en = formatla_komut(REAL_KNOWLEDGE_EN[idx]["c"].format(**uretilen))
                
                if random.random() < 0.20:
                    u_tr = f"{u_tr} {random.choice(NOISE_TR)}" if random.random() > 0.5 else f"{random.choice(NOISE_TR)} {u_tr}"
                    u_en = f"{u_en} {random.choice(NOISE_EN)}" if random.random() > 0.5 else f"{random.choice(NOISE_EN)} {u_en}"
                
                if c_tr and not validate_command(c_tr): continue
                    
                cevap_tr = json_build("command", c_tr) if only_cmd else json_build("command", c_tr, "System component loaded.")
                cevap_en = json_build("command", c_en) if only_cmd else json_build("command", c_en, "Running system level operation.")
                write_row(u_tr, cevap_tr, u_en, cevap_en)

            else:
                # 🚀 SYNTHETIC COMPLEX & NOISY
                idx = random.randint(0, len(SYNTHETIC_TR)-1)
                u_tr = SYNTHETIC_TR[idx]["u"].format(**uretilen)
                c_tr = formatla_komut(SYNTHETIC_TR[idx]["c"].format(**uretilen))
                
                u_en = SYNTHETIC_EN[idx]["u"].format(**uretilen)
                c_en = formatla_komut(SYNTHETIC_EN[idx]["c"].format(**uretilen))
                
                if random.random() < 0.30:
                    u_tr = f"{random.choice(NOISE_TR)} {u_tr}"
                    u_en = f"{random.choice(NOISE_EN)} {u_en}"
                
                d_tr = SYNTHETIC_TR[idx].get("d", "Komut işletiliyor.")
                d_en = SYNTHETIC_EN[idx].get("d", "Executing logic block.")
                
                if c_tr and not validate_command(c_tr): continue
                
                cevap_tr = json_build("command", c_tr) if only_cmd else json_build("command", c_tr, d_tr)
                cevap_en = json_build("command", c_en) if only_cmd else json_build("command", c_en, d_en)
                write_row(u_tr, cevap_tr, u_en, cevap_en)

    print(f"\nBASARILI: V7 MASTER DATABASE ({basarili*2} KAYIT) '{dosya_adi}' ICINE YAZILDI!")

if __name__ == "__main__":
    print("V7 MOTORU ATESLENDI: EXTREME REGEX & KUSURSUZ CONTRAST PAIRS...")
    egitim_olustur(50000, "Kusursuz_Egitim_V7.jsonl")
