<div align="center">

# ⚡ LingoCLI: AI Terminal Assistant

**A local AI-powered terminal assistant for Windows PowerShell, powered by its OWN Custom Finetuned Model.**  
Runs entirely on your machine — no internet, no API keys, no cloud. Just you and your local, specially trained AI.

![AI Terminal Home](assest/screenshots/home.png)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![LM Studio](https://img.shields.io/badge/LM_Studio-Required-purple?logo=data:image/png;base64,iVBORw0KGgo=)](https://lmstudio.ai)
[![Model](https://img.shields.io/badge/Model-LingoCLI--Qwen_2.5--3B-orange)](https://huggingface.co/Carus10/LingoCLI-Qwen2.5-3B)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://www.microsoft.com/windows)

</div>

---

## 🎯 What Is This?

LingoCLI is a desktop application that lets you **control your computer using natural language**. Instead of memorizing commands, just describe what you want in plain English or Turkish — the AI translates your request into a PowerShell command, shows it to you for approval, and executes it.

**Example:**
```
You type:  "create a folder called Projects on desktop"
AI runs:   New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\Projects"
```

Everything runs **locally** on your computer using [LM Studio](https://lmstudio.ai) and our **Exclusively Finetuned Qwen 2.5 3B** model (`Carus10/LingoCLI-Qwen2.5-3B`). No data leaves your machine.

---

## 🧠 The Custom Finetuned Model

Unlike other wrappers that use massive, complicated prompts to force a base model to output code, **LingoCLI runs on its own Finetuned Model**. 

We took Qwen 2.5 3B and trained it on a custom **4700+ line bilingual (English/Turkish) DevOps dataset**. As a result:
* The model natively understands terminal execution intents.
* It always outputs in an exact `AÇIKLAMA:/KOMUT:` format without heavy prompting.
* It achieves lower latency and zero "hallucination" on syntax formatting.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥️ **Real Terminal Look** | Black background, monospaced font, authentic terminal experience |
| 🤖 **Custom AI Model** | Powered by `LingoCLI-Qwen2.5-3B`, natively trained for Windows PowerShell tasks |
| 🧠 **Smart Memory** | Token-based memory with auto-summarization — unlimited conversation |
| 🔒 **Security System** | Dangerous commands (delete system files, format disk, etc.) require double confirmation |
| 🌍 **Bilingual** | Full English & Turkish support — switchable instantly from settings |
| 🎨 **Customizable Colors** | Change user text, AI command, description, and prompt colors |
| 🔄 **Git Workflows** | Understands multi-step Git operations natively |
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

### Step 2: Download the LingoCLI AI Model

1. In LM Studio, click the **Search** bar (magnifying glass) at the left menu.
2. Search exactly for: **`Carus10/LingoCLI-Qwen2.5-3B`**
3. Download the **GGUF** version (usually 1.93 GB).
4. Wait for the download to complete.

> **💡 Note:** This is our custom finetuned version of Qwen. It is optimized to run lightning-fast on 4-bit quantization, even without a GPU!

### Step 3: Start the LM Studio Server

1. In LM Studio, go to the **"Local Server"** tab (left sidebar, `<->` icon)
2. Select the **LingoCLI-Qwen2.5-3B** model from the dropdown at the top.
3. Click **"Start Server"**
4. You should see: `Server running on http://localhost:1234`

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
python main.py
```
*(or `python ai_terminal_asistan.py` depending on your entry point)*

That's it! The app will test the server connection and open the terminal interface, ready to serve as your local system expert.

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

The executable will be in the `dist/` folder. Double click `AI_Terminal.exe` to run.

---

## 🎮 How to Use

### Basic Usage

Just type what you want in natural language:

| You Type | AI Executes |
|---|---|
| `create a folder called Test on desktop` | `New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\Test"` |
| `list all files in Documents` | `Get-ChildItem -Path "$env:USERPROFILE\Documents"` |
| `Masaüstümdeki Test klasörünü sil` | `Remove-Item -Path "$env:USERPROFILE\Desktop\Test"` |
| `projem için python gitignore tạo` | `Set-Content -Path ".gitignore" -Value "__pycache__/...` |

### Dangerous Commands

If the AI generates a potentially dangerous command (delete system files, format disk, shutdown, etc.), local Python guardrails intercept the request and prompt an **extra confirmation dialog** before it runs:

```
⚠ DANGER: Bulk force delete
[Are you sure? Yes / No]
```

### Session Management

- **+ New Session:** Clears all memory and starts fresh
- **ⓘ Info:** Shows memory usage, token budget, and system stats
- **Memory Bar:** Shows real-time memory usage in the title bar

---

## 🏗️ Project Structure

```
LingoCLI/
├── ai_terminal_asistan.py    # Main app: UI, boot screen, memory, API
├── komut_veritabani.py       # Danger guardrails & minimal persona logic
├── dil.py                    # Translation module (EN/TR, 82 keys)
├── terminal_ayarlar.json     # User settings (colors, language)
├── assest/
│   └── screenshots/          # App screenshots
├── dist/
│   └── AI_Terminal.exe       # Standalone executable (after build)
└── README.md                 # This file
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| **"Connection error"** | Make sure LM Studio is running and the server is started on port 1234 |
| **App doesn't start** | Check Python 3.10+ is installed: `python --version` |
| **Turkish characters broken** | The app uses UTF-8. Make sure your terminal supports it |

> Built with ❤️ using Python, CustomTkinter, and local Custom AI. No cloud. No API keys. No data leaves your machine.
