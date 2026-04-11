<div align="center">

# ⚡ AI Terminal Assistant

**A local AI-powered terminal assistant for Windows PowerShell.**  
Runs entirely on your machine — no internet, no API keys, no cloud. Just you and your local AI.

![AI Terminal Home](assest/screenshots/home.png)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![LM Studio](https://img.shields.io/badge/LM_Studio-Required-purple?logo=data:image/png;base64,iVBORw0KGgo=)](https://lmstudio.ai)
[![Model](https://img.shields.io/badge/Model-Qwen_2.5_3B-orange)](https://huggingface.co/Qwen/Qwen2.5-3B)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://www.microsoft.com/windows)

</div>

---

## 🎯 What Is This?

AI Terminal Assistant is a desktop application that lets you **control your computer using natural language**. Instead of memorizing commands, just describe what you want in plain English or Turkish — the AI translates your request into a PowerShell command, shows it to you for approval, and executes it.

**Example:**
```
You type:  "create a folder called Projects on desktop"
AI runs:   New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\Projects"
```

Everything runs **locally** on your computer using [LM Studio](https://lmstudio.ai) and the **Qwen 2.5 3B** model. No data leaves your machine.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥️ **Real Terminal Look** | Black background, monospaced font, authentic terminal experience |
| 🧠 **Smart Memory** | Token-based memory with auto-summarization — unlimited conversation |
| 🔒 **Security System** | Dangerous commands (delete system files, format disk, etc.) require double confirmation |
| 🌍 **Bilingual** | Full English & Turkish support — switchable instantly from settings |
| 🎨 **Customizable Colors** | Change user text, AI command, description, and prompt colors |
| 📚 **267 Command Examples** | Built-in database across 27 categories for accurate command generation |
| 🔄 **Git Workflows** | Multi-step Git operations: init → add → commit → push in one command |
| 📊 **Memory Bar** | Real-time memory usage indicator (green → yellow → red) |
| 🚀 **Auto-Launch** | Automatically starts LM Studio if it's not running |
| 📦 **Standalone .exe** | Can be packaged as a single executable — no Python required |

---

## 📸 Screenshots

<div align="center">

| Boot Screen | Settings |
|---|---|
| ![Boot](assest/screenshots/open%20screen(control%20area).png) | ![Settings](assest/screenshots/settings.png) |

</div>

---

## 🚀 Quick Start (Step by Step)

### Step 1: Install LM Studio

1. Go to **[https://lmstudio.ai](https://lmstudio.ai)**
2. Download and install **LM Studio** for Windows
3. Open LM Studio

### Step 2: Download the AI Model

1. In LM Studio, click the **Search** bar at the top
2. Search for: **`Qwen2.5-3B-Instruct`**
3. Download the **GGUF** version (recommended: `Q4_K_M` quantization)
4. Wait for the download to complete (~2 GB)

> **💡 Why Qwen 2.5 3B?** It's small enough to run on most computers (even without a GPU), fast, and understands both English and Turkish well. If you have a powerful GPU, you can use larger models like 7B or 14B — just update the `MODEL_CONTEXT` value in the code.

### Step 3: Start the LM Studio Server

1. In LM Studio, go to the **"Local Server"** tab (left sidebar, server icon)
2. Select the **Qwen 2.5 3B** model from the dropdown
3. Click **"Start Server"**
4. You should see: `Server running on http://localhost:1234`

![LM Studio Server](https://github.com/user-attachments/assets/lm-studio-server-placeholder.png)

> **⚠️ Important:** The server must be running on **port 1234** (this is the default). Do not change it.

### Step 4: Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/LingoCLI.git
cd LingoCLI
```

### Step 5: Install Python Dependencies

Make sure you have **Python 3.10+** installed. Then:

```bash
pip install customtkinter requests
```

### Step 6: Run the App

```bash
python ai_terminal_asistan.py
```

That's it! The app will:
1. ✅ Check if LM Studio server is running
2. ✅ If not, try to launch LM Studio automatically
3. ✅ Wait for the server to be ready
4. ✅ Open the terminal interface

---

## 📦 Build Standalone .exe (Optional)

Want to run the app **without Python installed**? Build it as a standalone executable:

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the .exe

```bash
python -m PyInstaller --noconfirm --onefile --windowed --name "AI_Terminal" --add-data "komut_veritabani.py;." --add-data "dil.py;." --hidden-import customtkinter --collect-all customtkinter ai_terminal_asistan.py
```

### 3. Find Your .exe

The executable will be in the `dist/` folder:

```
dist/
└── AI_Terminal.exe    ← Double-click to run!
```

### 4. Create a Desktop Shortcut (Optional)

Right-click `AI_Terminal.exe` → **Send to** → **Desktop (create shortcut)**

> **📝 Note:** The `.exe` is ~16 MB because it bundles Python and all dependencies. LM Studio still needs to be installed separately — the app will auto-launch it.

---

## 🎮 How to Use

### Basic Usage

Just type what you want in natural language:

| You Type | AI Executes |
|---|---|
| `create a folder called Test on desktop` | `New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\Test"` |
| `list all files in Documents` | `Get-ChildItem -Path "$env:USERPROFILE\Documents"` |
| `delete the Test folder from desktop` | `Remove-Item -Path "$env:USERPROFILE\Desktop\Test"` |
| `push this project to github` | `git add .; git commit -m "Update"; git push origin main` |
| `create a python gitignore` | `Set-Content -Path ".gitignore" -Value "__pycache__/..."` |

### Command Flow

```
You type a request
    ↓
AI generates a command + description
    ↓
You see: # Description of what it does
         > The actual PowerShell command
    ↓
Click [Run] to execute or [Cancel] to skip
    ↓
Output is displayed in the terminal
```

### Dangerous Commands

If the AI generates a potentially dangerous command (delete system files, format disk, shutdown, etc.), you'll get an **extra confirmation dialog** before it runs:

```
⚠ DANGER: Bulk force delete
[Are you sure? Yes / No]
```

### Settings (⚙ Button)

- **Colors:** Customize user text, AI command, description, and prompt colors
- **Language:** Switch between English and Turkish instantly

### Session Management

- **+ New Session:** Clears all memory and starts fresh
- **ⓘ Info:** Shows memory usage, token budget, database stats
- **Memory Bar:** Shows real-time memory usage in the title bar

---

## 🧠 Smart Memory System

The app uses an intelligent token-based memory system:

```
┌────────────────────────────────────────┐
│  Model Context Window: 4096 tokens    │
├────────────────────────────────────────┤
│  System Prompt:   ~900 tokens         │
│  History Budget:  ~2596 tokens        │
│  Response Budget: ~300 tokens         │
│  Safety Margin:   ~300 tokens         │
└────────────────────────────────────────┘
```

- **Unlimited conversation:** When history exceeds 70% of the budget, old messages are automatically **summarized** by the AI
- **Last 3 exchanges always kept raw** for accurate recent context
- **Summary counter** shows how many times summarization occurred
- **Memory bar** turns green → yellow → red as memory fills up

---

## 📚 Command Database (267 Examples)

The built-in database covers **27 categories**:

| Category | Examples | Description |
|---|---|---|
| File Operations | 20 | Create, delete, copy, move, rename |
| Folder Operations | 15 | Create, list, navigate directories |
| System Info | 18 | CPU, RAM, disk, OS version, uptime |
| Network | 18 | IP, ping, DNS, ports, Wi-Fi |
| **Git Basic** | 10 | Status, log, config, branch |
| **Git Workflows** | 13 | Init→add→commit→push chains |
| **Git Branch** | 8 | Create, merge, delete, rebase |
| **Git Recovery** | 10 | Reset, revert, stash, undo |
| **Git Ignore** | 11 | Python/Node/C#/Java/React templates |
| **Git Troubleshoot** | 11 | Push rejected, merge conflicts |
| **Git Tags** | 6 | Create, push, delete tags |
| Process Management | 15 | List, kill, start processes |
| Package Managers | 15 | npm, pip, choco, winget |
| Web & Browser | 10 | Open URLs, download files |
| Compression | 10 | Zip, unzip, tar |
| User & Permissions | 12 | Users, groups, ACL |
| Scheduled Tasks | 10 | Create, list, delete tasks |
| And 10 more... | 55+ | Services, registry, text, search... |

---

## 🏗️ Project Structure

```
LingoCLI/
├── ai_terminal_asistan.py    # Main app: UI, boot screen, memory, API
├── komut_veritabani.py       # 267 command examples + AI prompt engine
├── dil.py                    # Translation module (EN/TR, 82 keys)
├── terminal_ayarlar.json     # User settings (colors, language)
├── assest/
│   └── screenshots/          # App screenshots
├── dist/
│   └── AI_Terminal.exe       # Standalone executable (after build)
└── README.md                 # This file
```

---

## ⚙️ Configuration

### Change the AI Model

If you want to use a different model (e.g., 7B, 14B), update these values in `ai_terminal_asistan.py`:

```python
MODEL_CONTEXT = 4096    # Change to your model's context window
# For example:
# Qwen 2.5 7B  → MODEL_CONTEXT = 8192
# Qwen 2.5 14B → MODEL_CONTEXT = 32768
```

### Change the API Port

If your LM Studio runs on a different port:

```python
API_URL = "http://localhost:1234/v1/chat/completions"  # Change 1234 to your port
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| **"Connection error"** | Make sure LM Studio is running and the server is started on port 1234 |
| **App doesn't start** | Check Python 3.10+ is installed: `python --version` |
| **Wrong commands generated** | Make sure you're using **Qwen 2.5 3B Instruct** (not base model) |
| **Slow responses** | The 3B model is lightweight; if too slow, check your RAM/CPU usage |
| **Turkish characters broken** | The app uses UTF-8. Make sure your terminal supports it |
| **exe build fails** | Try: `pip install pyinstaller --upgrade` and run the build command again |
| **LM Studio not auto-detected** | Install LM Studio to default path: `C:\Program Files\LM Studio\` |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add more command examples to `komut_veritabani.py`
- Add new language translations to `dil.py`
- Improve the AI prompt for better accuracy
- Report bugs via Issues

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using Python, CustomTkinter, and local AI**

*No cloud. No API keys. No data leaves your machine.*

</div>
