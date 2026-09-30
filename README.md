```markdown
# 🤖 Bot By Angga Official - CekBio WA

An advanced Telegram bot for checking WhatsApp bios with a tiering system (Free, VIP, XVIP, VVIP) and semi-automatic QRIS payment integration. Built with `python-telegram-bot` version 20+ and an SQLite database for robust data when running on Termux.

## ✨ Key Features
- 🔍 **CekBio WhatsApp:** Detects user's WhatsApp number and bio.
- 📊 **Daily Limit System:** Automatic detection limit resets daily.
- 💎 **Premium Tier System:** Free, VIP, XVIP, VVIP with their respective limits.
- 🛒 **QRIS Payment:** Automatically sends QRIS images to users, receives proof of transfer, and is verified by the admin.

- 🗄️ **Permanent Database:** Uses SQLite (`cekbio.db`) so user data, limits, and statistics are not lost when the bot is restarted.
- 📱 **Termux Ready:** Optimized to run directly from an Android phone using Termux.

---

## 🛠️ Prerequisites
Before you begin, make sure you have:
1. **Telegram Bot Token** (Get it from [@BotFather](https://t.me/BotFather)).
2. **Your Telegram ID** (Get it from [@userinfobot](https://t.me/userinfobot)).
3. **Termux** app on Android (Run it from Play Store or F-Droid).

---

## 📲 How to Install & Run in Termux

Follow these steps sequentially in your Termux application:

### 1. Update & Install Dependencies
Enter the following commands to update the Termux packages and install Python and Git:
```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

### 2. Clone Repository
Download the bot code from GitHub to your Termux repository:
```bash
git clone https://github.com/kacangkedele/cekbio-wa
cd cekbio-wa
```

### 3. Install Python Libraries
Install all required libraries in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Configure the Bot
Edit the `config.py` file to include the Bot Token and Admin ID You:
```bash
nano config.py
```
*Change the `BOT_TOKEN` and `ADMIN_ID` sections with your data. When finished, press `CTRL+X`, then `Y`, and `Enter` to save.*

### 5. Run the Bot
Start running the bot with the command:
```bash
python bot.py
```
If the message `"Bot By Angga Official is running on Termux..."` appears, your bot is online! Open Telegram and try typing `/start` in your bot.

---

## ⚙️ `config.py` File Configuration
Make sure you fill in the following information correctly:
```python
BOT_TOKEN = "TOKEN_BOT_DARI_BOTFATHER"
ADMIN_ID = 123456789 # Your Telegram ID (number, not username)
ADMIN_USERNAME = "YourAdminUsername" # Your username without the @ symbol
CHANNEL_URL = "https://t.me/YourChannelLink"
QRIS_IMAGE_URL = "YOURQRIS_IMAGE_URL"
```

---

## 🎮 Command List

### User Commands:
- `/start` - Displays the main menu and user info.
- `/premium` - Displays a list of premium packages and prices.
- `/detect <number>` - Checks WhatsApp bio. Example: `/detect +628123456789`

### Special Admin Commands:
- `/upgrade <User_ID> <Tier> <Number_of_Days>` - Manually activates a premium user after payment verification.
- **Example:** `/upgrade 6281234567 VIP 30`

---

## 🔄 QRIS Payment Flow (Semi-Automatic)
1. The user presses the "Buy VIP" button.
2. The bot automatically sends a QRIS image and the amount to be paid.
3. The user makes the payment via OVO/Dana/GoPay/Bank.
4. The user sends a screenshot of proof of payment to the bot chat.
5. The bot forwards the proof of payment to the **Admin** chat along with the user details.
6. The admin checks the funds received, then types the command `/upgrade <ID> <Tier> <Days>`.
7. The bot automatically updates the user's status to VIP and sends a congratulatory notification to the user.

---

## ❓ Troubleshooting
- **Bot shuts down when Termux is closed:**
This is normal. To run the bot 24/7 in the background, you can use services like `screen` or `tmux` in Termux, or run it on a VPS server.
- **Error `ModuleNotFoundError`:**
Make sure you have run `pip install -r requirements.txt` in the `cekbio-wa` folder.

---
Made with ❤️ by [Angga Official](https://github.com/kacangkedele)
🏠.(https://youtube.com/@bacotamatpro03).
```

 
