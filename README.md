# Antigravity Cloud Bridge

> Autonomous two-way bridge connecting mobile Telegram and Resend email infrastructure to local AI coding workspaces (Google Antigravity, Cursor, Claude Code). Ingests photos, documents, and voice notes while you are away from your desk, sanitizes files, executes on-the-fly binary generation (Word, PowerPoint, Excel, vector PDF), and dispatches output back to your phone.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Clean](https://img.shields.io/badge/Code%20Style-Production-emerald.svg)](<>)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](<>)

---

## Why This Exists: The Desk-Tethered AI Problem

Modern AI agents excel inside terminal sessions and IDEs, but they are completely blind to the physical world when you step away from your keyboard:

1. **Information Fragmentation:** Snapping a photo of a whiteboard, book page, or handwritten diagram requires manual transfer before your AI workspace can inspect it.
2. **Zero Out-of-Office Execution:** When you are walking, commuting, or away from your desk, you cannot instruct your local AI environment to run analysis or generate assets.
3. **Asset Delivery Bottlenecks:** When a local AI creates a 16:9 presentation, Word document, or compiled PDF, delivering that binary file back to your phone usually requires setting up webhooks, reverse tunnels, or manual file-sharing links.

**Antigravity Cloud Bridge** solves this by running a lightweight local daemon that continuously syncs with your private Telegram bot. When you send notes or files, it buffers them into your workspace ledger. When you append `- now`, it runs autonomous reasoning, compiles the requested binary documents, and uploads the results straight to your phone.

---

## Core Philosophy: Works with Just ONE API Key

> **Important Setup Principle:**
> You do **not** need three different AI accounts or keys to run this project.
>
> Adding **just ONE AI API key** (either OpenAI, OR Google Gemini, OR OpenRouter) is 100% enough to make every single feature work: asking questions, generating Word documents, creating PowerPoint slides, compiling vector PDFs, creating Excel sheets, running single-file web apps, and sanitizing documents.
>
> **Why are three options provided?**
> Redundancy and zero-downtime reliability. In real-world software engineering, commercial APIs can hit HTTP 429 rate limits, sudden credit caps, or temporary cloud outages. With three providers configured, if your primary provider fails or times out, Antigravity Cloud Bridge automatically falls over to the next provider within milliseconds without dropping your request or requiring manual intervention.

---

## System Architecture

```
                    MOBILE PHONE (You on the Move)
                                 │
                                 ▼
                         Telegram Bot API
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
          Passive Buffer                  Immediate Trigger
        (Normal Send / Sync)                  (`- now`)
                │                                 │
                ▼                                 ▼
    [Local Ingestion Daemon]            [Instant Acknowledgment]
    • Downloads to ./inbox/                       │
    • Appends to ./mobile_notes.md                ▼
    • Updates ./inbox_ledger.json       [Multi-Tier LLM Engine]
                │                       • 1 Key Required (3 for Failover)
                │                       • OpenAI -> Gemini -> OpenRouter
                ▼                       • Media Sanitizer (#FFFFFF / <100KB)
      [Ready for Local IDE]             • Office Compilers (DOCX / PPTX / PDF)
                                                  │
                                                  ▼
                                      [Two-Way Binary Dispatch]
                                      • Direct Upload to Telegram Chat
                                      • Automatic Resend Email Fallback
```

---

## Step-by-Step API Key Acquisition Guide

Here is the exact procedure to get every key used by the system. Remember: you only need **Telegram credentials + any ONE AI key** to begin.

### 1. Telegram Bot Token (Required)

The bot acts as your private bridge to your AI workspace.

1. Open Telegram on your phone or desktop and search for `@BotFather` (look for the verified blue checkmark badge).
2. Click **Start** or send `/start`.
3. Send the command `/newbot`.
4. BotFather will ask for a display name. Enter any name you like (for example: `My AI Cloud Bridge`).
5. BotFather will ask for a username. Enter a unique username that ends in `bot` (for example: `my_cloud_bridge_bot`).
6. BotFather will reply with your **HTTP API Token**. It looks like this:  
   `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
7. Copy this token. Save it in your `.env` file under `TELEGRAM_BOT_TOKEN`.
8. **Crucial Step:** Search for your newly created bot username in Telegram, open the chat, and tap **Start** (or send `/start`). The bot cannot initiate contact with you until you send the first message.

### 2. Telegram Chat ID (Required)

Your numeric Chat ID ensures that the bridge only accepts commands and sends files to your personal Telegram account.

**Method A: Using an Info Bot (Fastest)**

1. Open Telegram and search for `@userinfobot`.
2. Tap **Start**.
3. The bot will immediately reply with your account details. Look for the numeric value labeled `Id` (for example: `123456789`).
4. Copy this number and paste it into `TELEGRAM_CHAT_ID` in your `.env` file.

**Method B: Direct Browser Inspection**

1. Send any test message (for example: `hello`) to your newly created bot.
2. Open your web browser and navigate to:  
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`  
   _(Replace `<YOUR_BOT_TOKEN>` with your actual token from Step 1)_.
3. In the JSON output, look for `"chat":{"id":123456789}`. That number is your Chat ID.

---

### 3. AI Provider Keys (Pick at Least ONE)

Choose any one provider below. If you want zero-downtime failover, configure two or all three.

#### Option A: OpenAI API Key (High Speed)

- **Model Used:** `gpt-4o-mini`
- **Cost:** Pay-as-you-go (fractions of a cent per request).

1. Go to [platform.openai.com](https://platform.openai.com/) and sign up or log in.
2. In the left navigation menu, click **API keys** (or go to `platform.openai.com/api-keys`).
3. Click **+ Create new secret key**.
4. Enter an identifier (such as `antigravity-bridge`) and click **Create secret key**.
5. Copy the secret key (`sk-proj-...`). Save it in `.env` under `OPENAI_API_KEY`.

#### Option B: Google Gemini API Key (High Speed + Multimodal Vision + Free Tier)

- **Models Used:** `models/gemini-2.5-flash`, `models/gemini-3.8-flash`
- **Cost:** Generous free tier available via Google AI Studio.

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your standard Google account.
3. In the top navigation bar, click the blue **Get API key** button.
4. Click **Create API key**. Select an existing Google Cloud project or click "Create API key in new project".
5. Copy the generated key (`AIzaSy...`). Save it in `.env` under `GEMINI_API_KEY`.

#### Option C: OpenRouter API Key (Model Aggregator + Free Endpoints)

- **Model Used:** `google/gemini-2.0-flash-exp:free` (and dozens of other models).
- **Cost:** Free models available; pay-as-you-go for premium models.

1. Go to [openrouter.ai](https://openrouter.ai/) and sign up with Google or GitHub.
2. Click your profile icon in the upper-right corner and select **Keys** (or visit `openrouter.ai/keys`).
3. Click **Create Key**. Enter a label (such as `cloud-bridge`) and click Create.
4. Copy the secret token (`sk-or-v1-...`). Save it in `.env` under `OPENROUTER_API_KEY`.

---

### 4. Resend API Key (Optional Email Dispatcher)

Resend provides transactional email sending. The bridge uses this to deliver documents or summaries directly to your email inbox if Telegram encounters file size limits or transient network drops.

1. Go to [resend.com](https://resend.com/) and create a free account (includes 3,000 free emails per month).
2. From the Resend dashboard, click **API Keys** in the left sidebar.
3. Click **Create API Key**. Leave permissions as "Full access" and click Add.
4. Copy the API key starting with `re_...`. Save it in `.env` under `RESEND_API_KEY`.
5. In `.env`, set `NOTIFICATION_EMAIL_RECIPIENT` to your destination email address.
6. **Domain Setup:**
   - For instant local testing without a custom domain, you can send emails from `onboarding@resend.dev` to the exact email address registered on your Resend account.
   - For custom domain sending (e.g. `ci@yourdomain.com`), navigate to **Domains** in Resend, add your domain, and configure the DNS records with your registrar.

---

## Installation & Setup

### 1. System Requirements

- Python 3.10, 3.11, or 3.12.
- Git installed on your system.
- An active internet connection.

### 2. Clone the Repository

```bash
git clone https://github.com/rajchhapariya/antigravity-cloud-bridge.git
cd antigravity-cloud-bridge
```

### 3. Create and Activate a Virtual Environment

**On Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**On Linux / macOS (Bash / Zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

_(Optional) Install in editable mode so you can run the `antigravity-bridge` command directly:_

```bash
pip install -e .
```

### 5. Create Your Environment Configuration

Copy the example template to create your `.env` file:

```bash
# On Linux/macOS
cp .env.example .env

# On Windows PowerShell
Copy-Item .env.example .env
```

Now open `.env` in your text editor.

#### Scenario A: Minimal Setup (Only 1 AI Key Needed)

If you only want to use Google Gemini (free tier) and Telegram, your `.env` looks like this:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Single AI key - everything works
GEMINI_API_KEY=AIzaSyYourGeminiKeyHere

# Storage defaults
INBOX_DIR=./inbox
LEDGER_FILE=./inbox/inbox_ledger.json
OFFSET_FILE=./inbox/.telegram_offset.json
NOTES_FILE=./inbox/mobile_notes.md
POLL_INTERVAL=3
```

#### Scenario B: Full Production Setup (Redundant AI Failovers + Email)

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Redundant AI Providers (OpenAI -> Gemini -> OpenRouter)
OPENAI_API_KEY=sk-proj-your-openai-key
GEMINI_API_KEY=AIzaSy-your-gemini-key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Resend Transactional Email
RESEND_API_KEY=re_your_resend_key
NOTIFICATION_EMAIL_RECIPIENT=developer@example.com
SENDER_DEFAULT_IDENTITY=AI Assistant <noreply@yourdomain.com>
SENDER_DOMAIN=yourdomain.com

# System Settings
SYSTEM_INSTRUCTION="You are an autonomous AI software engineering and development assistant. Strictly ZERO emojis."
INBOX_DIR=./inbox
LEDGER_FILE=./inbox/inbox_ledger.json
OFFSET_FILE=./inbox/.telegram_offset.json
NOTES_FILE=./inbox/mobile_notes.md
POLL_INTERVAL=3
```

### 6. Verify Your Connection

Send a quick test message from your terminal to verify that your Telegram bot can communicate with your phone:

```bash
python -m antigravity_bridge.cli --send-text "Antigravity Cloud Bridge initialized successfully."
```

If your phone receives the message, your credentials and connection are verified.

---

## Running the Bridge

### Mode 1: Continuous Background Daemon (Standard)

Keep the daemon running in the background to handle incoming mobile requests continuously:

```bash
python -m antigravity_bridge.cli --daemon --interval 3
```

- Polls Telegram every 3 seconds.
- Automatically buffers files and notes sent without `- now`.
- Automatically executes tasks and delivers generated documents when `- now` is included.

### Mode 2: One-Shot Cloud Sync

If you only want to ingest items currently pending in the cloud queue without keeping a background process alive:

```bash
python -m antigravity_bridge.cli --sync
```

---

## How to Use from Your Phone

Once the daemon is running, you can interact with your AI workspace directly through your Telegram bot while walking, commuting, or away from your desk.

### 1. Passive Cloud Buffering (No `- now`)

Send any text, voice note, photo, or PDF to your bot.

- **Action:** The daemon downloads the file into `./inbox/`, appends any note to `mobile_notes.md`, and updates `inbox_ledger.json`.
- **Response:** The bot sends a discreet receipt message: `Buffered to Antigravity Inbox`.
- **Purpose:** Queues reference material for when you return to your IDE without interrupting your current workflow.

### 2. Immediate Execution (`- now`)

Add `- now` to the end of your message to trigger instant processing.

| What you send on Telegram                                    | Action taken by Bridge                                     | Output Delivered to Phone                             |
| :----------------------------------------------------------- | :--------------------------------------------------------- | :---------------------------------------------------- |
| `Explain difference between B-Trees and LSM Trees - now`     | Queries AI resolver                                        | Markdown technical breakdown sent to your chat        |
| `Create a 4-slide PPT on Event-Driven Architecture - now`    | Compiles native 16:9 widescreen presentation               | Native `.pptx` presentation file uploaded to Telegram |
| `Create a doc file on REST API conventions - now`            | Compiles structured document with styled headings          | Native `.docx` document file uploaded to Telegram     |
| `Create an Excel sheet comparing cloud databases - now`      | Compiles spreadsheet with formatted headers and data       | Native `.xlsx` workbook uploaded to Telegram          |
| `Create a PDF report on system metrics - now`                | Compiles clean vector layout                               | Native `.pdf` document uploaded to Telegram           |
| `Create an app for a pomodoro timer - now`                   | Compiles single-file responsive PWA                        | Runnable `.html` file uploaded to Telegram            |
| Send signature photo with caption `Sanitize signature - now` | Crops ink, enforces `#FFFFFF` background, $<100\text{ KB}$ | Clean signature image dispatched to Telegram          |
| Send portrait photo with caption `Sanitize photo - now`      | Centers face, standardizes 3:4 crop, $<200\text{ KB}$      | Clean profile image dispatched to Telegram            |
| Send large PDF with caption `Sanitize PDF - now`             | Compresses stream, downsamples to 180 DPI                  | Strict $<1\text{ MB}$ PDF dispatched to Telegram      |

---

## Direct CLI Commands

The CLI also lets you trigger bridge actions manually from your terminal or CI/CD pipelines:

```bash
# Send text message to your phone
python -m antigravity_bridge.cli --send-text "Deployment #142 passed all tests."

# Send a binary document or image to your phone
python -m antigravity_bridge.cli --send-file ./reports/benchmark.pdf --caption "Benchmark Report"

# Send email notification via Resend
python -m antigravity_bridge.cli --send-email "Build Alert" "Integration suite passed on branch main."

# Sanitize signature image to pure white background under 100KB
python -m antigravity_bridge.cli --sanitize-sig ./assets/signature.jpg

# Crop and compress profile photo under 200KB
python -m antigravity_bridge.cli --sanitize-photo ./assets/headshot.jpg

# Compress PDF strictly under 1MB while preserving vector text
python -m antigravity_bridge.cli --sanitize-pdf ./assets/heavy_report.pdf
```

---

## Agentic IDE Integration

To wire this daemon directly into your AI coding assistant (Antigravity IDE, Cursor, Claude Code, or Codex), add the following protocol to your workspace rules (such as `AGENTS.md`, `GEMINI.md`, or `.cursorrules`):

```markdown
### Mobile Cloud Buffer Protocol

1. Whenever the user mentions mobile notes or incoming files, inspect `inbox/inbox_ledger.json` for new updates.
2. If an item contains the `- now` flag, treat it as immediate priority and execute without delay.
3. Whenever generating or modifying any document, presentation, spreadsheet, PDF, or image, execute `python -m antigravity_bridge.cli --send-file <path>` to mirror the finished artifact directly to the user's phone.
```

---

## Directory Layout

```
antigravity-cloud-bridge/
├── .env.example                     # Environment configuration template
├── .gitignore                       # Standard python ignore rules
├── LICENSE                          # MIT License
├── pyproject.toml                   # Packaging configuration
├── README.md                        # Documentation and architecture guide
├── requirements.txt                 # Pinned production dependencies
└── src/
    └── antigravity_bridge/
        ├── __init__.py              # Package entry exports
        ├── cli.py                   # Unified command-line interface
        ├── core/
        │   ├── ai_resolver.py       # Multi-provider LLM failover engine
        │   ├── config.py            # Environment & credential manager
        │   ├── daemon.py            # Main polling & ingestion loop
        │   └── ledger.py            # Idempotent state & ledger engine
        ├── dispatchers/
        │   ├── email_dispatcher.py   # Context-aware Resend email client
        │   └── telegram_dispatcher.py# Telegram Bot API client & chunker
        ├── generators/
        │   └── office_generator.py  # DOCX, PPTX, XLSX, PDF & App builder
        └── sanitizers/
            └── media_sanitizer.py   # Signature, photo & PDF compressor
```

---

## Troubleshooting

- **Bot does not respond to messages:**
  - Verify that you opened your bot in Telegram and tapped **Start** (or sent `/start`). Telegram bots cannot message users who have not initiated contact.
  - Verify that your `TELEGRAM_CHAT_ID` matches your numeric account ID from `@userinfobot`. The daemon automatically ignores messages from any other chat ID to prevent unauthorized access.
- **LLM Rate Limits (HTTP 429):**
  - If you configure multiple providers in `.env` (`OPENAI_API_KEY`, `GEMINI_API_KEY`, and `OPENROUTER_API_KEY`), the resolver automatically handles rate limits by failing over to the next provider.
- **Windows Terminal Unicode Output:**
  - On Windows PowerShell, ensure console encoding is set to UTF-8:
    ```powershell
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    ```
- **Permission Errors on Portals:**
  - Ensure the user running the daemon has read and write permissions to the `./inbox/` directory.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
