import logging
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Init Database SQLite
conn = sqlite3.connect('cekbio.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, tier TEXT, usage INTEGER, last_reset TEXT, expire_date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, total_detections INTEGER)''')
    cursor.execute('INSERT OR IGNORE INTO stats (id, total_detections) VALUES (1, 4296)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pending (user_id INTEGER PRIMARY KEY, tier TEXT)''')
    conn.commit()

init_db()

TIER_LIMITS = {"Free": 5, "VIP": 25, "XVIP": 50, "VVIP": 100}
TIER_PRICES = {"VIP": 3000, "XVIP": 7000, "VVIP": 10000}

# === FUNGSI DATABASE ===
def get_user(user_id: int, username: str):
    today = date.today().isoformat()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users VALUES (?, ?, 'Free', 0, ?, NULL)", (user_id, username, today))
        conn.commit()
        user = (user_id, username, "Free", 0, today, None)
    
    user_dict = {
        "user_id": user[0], "username": user[1], "tier": user[2],
        "usage": user[3], "last_reset": user[4], "expire_date": user[5]
    }
    if user_dict["last_reset"] != today:
        cursor.execute("UPDATE users SET usage = 0, last_reset = ? WHERE user_id = ?", (today, user_id))
        conn.commit()
        user_dict["usage"] = 0
    if user_dict["tier"] != "Free" and user_dict["expire_date"]:
        expire_date = date.fromisoformat(user_dict["expire_date"])
        if date.today() > expire_date:
            cursor.execute("UPDATE users SET tier = 'Free', expire_date = NULL WHERE user_id = ?", (user_id,))
            conn.commit()
            user_dict["tier"] = "Free"
            user_dict["expire_date"] = None
    return user_dict

# === FUNGSI CEK BIO WA (TERHUBUNG KE sender.js) ===
async def cek_bio_wa(nomor: str):
    phone = nomor.lstrip('+')
    url = f"http://localhost:3000/cek?nomor={phone}"
    try:
        # Tambah batas waktu 10 detik. Jika lebih, bot akan balas gagal.
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("status"):
                    return data.get("bio", "Bio tidak tersedia")
                else:
                    return data.get("bio", "Gagal mendeteksi")
    except asyncio.TimeoutError:
        return "⚠️ Timeout: Server WA butuh waktu terlalu lama. Coba lagi nanti."
    except Exception as e:
        logger.error(f"Error API WA: {e}")
        return "⚠️ Server Sender (Node.js) sedang offline. Nyalakan sender.js!"

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = get_user(user.id, user.username or "TidakAda")
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    limit = TIER_LIMITS.get(user_data["tier"], 5)
    sisa_limit = limit - user_data["usage"]
    
    cursor.execute("SELECT total_detections FROM stats WHERE id = 1")
    total_det = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    text = (
        f"🤖 *Bot By Angga Official* 🤖\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 *Waktu:* {now}\n\n"
        f"👤 *INFO PENGGUNA*\n"
        f"├─ ID: `{user.id}`\n"
        f"├─ Username: @{user_data['username']}\n"
        f"├─ Tier: {user_data['tier']}\n"
        f"└─ Sisa Deteksi Hari ini: {sisa_limit} nomor\n\n"
        f"📊 *STATISTIK BOT*\n"
        f"├─ Total Users: {total_users}\n"
        f"└─ Total Deteksi: {total_det}x\n\n"
        f"📌 *DAFTAR PERINTAH*\n"
        f"├─ /start - Menampilkan menu ini\n"
        f"├─ /detek <nomor> - Cek Bio WhatsApp\n"
        f"└─ /premium - Lihat paket upgrade tier\n\n"
        f"📝 *CARA PENGGUNAAN CEKBIO*\n"
        f"Contoh: `/detek +628123456789`\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"_Deteksi nomor mata elang bersama Bot By Angga Official_"
    )

    keyboard = [
        [InlineKeyboardButton("💎 Lihat Paket Premium", callback_data="show_premium")],
        [InlineKeyboardButton("📢 Info Channel", url=config.CHANNEL_URL), InlineKeyboardButton("🐞 Laporkan Bug", url=f"https://t.me/{config.ADMIN_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = get_user(user.id, user.username or "TidakAda")
    
    text = (
        f"💎 *Paket Premium Bot By Angga Official* 💎\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"◇ Status kamu saat ini: *{user_data['tier']}* (maks {TIER_LIMITS[user_data['tier']]} nomor/sesi)\n\n"
        f"◇ *Paket VIP* ⭐\n├ /detek → maks 25 nomor\n└ Mulai Rp 3.000/hari\n\n"
        f"◇ *Paket XVIP* 🌟\n├ /detek → maks 50 nomor\n└ Mulai Rp 7.000/hari\n\n"
        f"◇ *Paket VVIP* 💎\n├ /detek → maks 100 nomor\n└ Mulai Rp 10.000/hari\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"_Klik tombol di bawah untuk melihat QRIS & melakukan pembayaran otomatis._"
    )
    
    keyboard = [
        [InlineKeyboardButton("💸 Beli VIP (3K/hari)", callback_data="buy_VIP")],
        [InlineKeyboardButton("💸 Beli XVIP (7K/hari)", callback_data="buy_XVIP")],
        [InlineKeyboardButton("💸 Beli VVIP (10K/hari)", callback_data="buy_VVIP")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def detek(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = get_user(user.id, user.username or "TidakAda")
    
    limit = TIER_LIMITS.get(user_data["tier"], 5)
    if user_data["usage"] >= limit:
        await update.message.reply_text("🚫 *LIMIT HARIAN HABIS!*\n\nGunakan /premium untuk meningkatkan limit.", parse_mode='Markdown')
        return

    if not context.args:
        await update.message.reply_text("❌ Format salah! Gunakan: `/detek +628xxx`", parse_mode='Markdown')
        return

    nomor_asli = context.args[0]
    if not nomor_asli.startswith('+'):
        await update.message.reply_text("❌ Nomor harus diawali dengan format internasional contoh: `+628xxx`", parse_mode='Markdown')
        return

    # Kurangi limit langsung
    cursor.execute("UPDATE users SET usage = usage + 1 WHERE user_id = ?", (user.id,))
    cursor.execute("UPDATE stats SET total_detections = total_detections + 1 WHERE id = 1")
    conn.commit()
    sisa_limit = limit - (user_data["usage"] + 1)
    
    # Kirim pesan proses
    proses_msg = await update.message.reply_text(
        f"🔍 *Sedang mendeteksi Bio untuk nomor:* `{nomor_asli}`\n\n⏳ _Mohon tunggu, sedang menarik data WhatsApp..._",
        parse_mode='Markdown'
    )

    # Panggil fungsi cek WA
    hasil_bio = await cek_bio_wa(nomor_asli)
    
    # Format teks hasil
    final_text = (
        f"✅ *Hasil Deteksi Bio WhatsApp*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📞 Nomor: `{nomor_asli}`\n"
        f"📝 Bio: {hasil_bio}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ Sisa deteksi hari ini: *{sisa_limit}* nomor"
    )
    
    # Gunakan try...except agar bot tidak crash jika Markdown error
    try:
        await proses_msg.edit_text(final_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Gagal edit pesan (Markdown Error): {e}")
        # Jika gagal, kirim ulang tanpa format Markdown
        try:
            await proses_msg.edit_text(final_text)
        except Exception:
            await update.message.reply_text(final_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    cursor.execute("SELECT tier FROM pending WHERE user_id = ?", (user.id,))
    pending = cursor.fetchone()
    
    if not pending:
        await update.message.reply_text("❌ Anda tidak ada transaksi yang tertunda. Silakan pilih paket di /premium terlebih dahulu.")
        return

    tier = pending[0]
    price = TIER_PRICES[tier]
    photo_file = await update.message.photo[-1].get_file()
    
    caption = (
        f"🛒 *PEMBAYARAN BARU MASUK* 🛒\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 User: @{user.username or 'TidakAda'}\n"
        f"🆔 ID: `{user.id}`\n"
        f"💎 Paket: *{tier}*\n"
        f"💰 Jumlah: Rp {price}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Jika uang sudah masuk, balas pesan ini dengan command:\n"
        f"`/upgrade {user.id} {tier} 1`"
    )
    
    await context.bot.send_photo(chat_id=config.ADMIN_ID, photo=photo_file.file_id, caption=caption, parse_mode='Markdown')
    cursor.execute("DELETE FROM pending WHERE user_id = ?", (user.id,))
    conn.commit()
    
    await update.message.reply_text("✅ *Bukti pembayaran berhasil dikirim ke Admin!*\n\nMohon tunggu 1-5 menit, Admin akan memverifikasi pembayaran Anda dan mengaktifkan tier Anda secara manual.\n\nTerima kasih!", parse_mode='Markdown')

async def upgrade_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != config.ADMIN_ID:
        return
        
    try:
        target_user_id = int(context.args[0])
        target_tier = context.args[1].upper()
        days = int(context.args[2])
        
        if target_tier not in TIER_LIMITS:
            await update.message.reply_text("❌ Tier tidak valid. Pilih: VIP, XVIP, atau VVIP")
            return
            
        user = get_user(target_user_id, "Unknown")
        current_expire_str = user.get("expire_date")
        base_date = date.today()
        
        if current_expire_str:
            current_expire = date.fromisoformat(current_expire_str)
            if current_expire > base_date:
                base_date = current_expire
                
        new_expire = base_date + timedelta(days=days)
        
        cursor.execute("UPDATE users SET tier = ?, expire_date = ? WHERE user_id = ?", (target_tier, new_expire.isoformat(), target_user_id))
        conn.commit()
        
        await update.message.reply_text(f"✅ Berhasil! User `{target_user_id}` telah di-upgrade ke tier *{target_tier}* selama {days} hari.", parse_mode='Markdown')
        await context.bot.send_message(chat_id=target_user_id, text=f"🎉 *PEMBAYARAN DITERIMA* 🎉\n\nSelamat! Akun Anda telah di-upgrade ke tier *{target_tier}*.\nDurasi: {days} hari.\n\nSekarang Anda bisa mendeteksi hingga {TIER_LIMITS[target_tier]} nomor per hari!", parse_mode='Markdown')
        
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Format salah! Gunakan: `/upgrade <user_id> <tier> <hari>`\nContoh: `/upgrade 6281234567 VIP 1`", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user = query.from_user
    
    if data == "show_premium":
        await premium(update, context)
    elif data == "back_to_start":
        await start(update, context)
    elif data.startswith("buy_"):
        tier_name = data.split("_")[1]
        price = TIER_PRICES[tier_name]
        
        cursor.execute("INSERT OR REPLACE INTO pending (user_id, tier) VALUES (?, ?)", (user.id, tier_name))
        conn.commit()
        
        text = (
            f"🛒 *PEMBAYARAN TIER {tier_name}* 🛒\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Silakan scan QRIS di bawah ini dan bayar sebesar:\n"
            f"💵 *Rp {price}*\n\n"
            f"📌 *Panduan:*\n"
            f"1. Scan QRIS menggunakan OVO, GoPay, Dana, atau Bank apa saja.\n"
            f"2. Bayar sesuai nominal di atas.\n"
            f"3. Screenshot bukti pembayaran Anda.\n"
            f"4. Kirimkan foto/screenshot bukti pembayaran KE CHAT INI.\n\n"
            f"_Bot akan meneruskan bukti pembayaran Anda ke Admin untuk diverifikasi._"
        )
        keyboard = [[InlineKeyboardButton("❌ Batalkan Transaksi", callback_data="cancel_payment")]]
        
        await query.answer()
        await query.message.delete()
        await context.bot.send_photo(chat_id=user.id, photo=config.QRIS_IMAGE_URL, caption=text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "cancel_payment":
        cursor.execute("DELETE FROM pending WHERE user_id = ?", (user.id,))
        conn.commit()
        await query.answer("Transaksi dibatalkan.")
        await start(update, context)

def main() -> None:
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("detek", detek))
    app.add_handler(CommandHandler("upgrade", upgrade_user))
    
    # Handler untuk foto bukti pembayaran
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handler untuk tombol callback
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Bot By Angga Official (Python) sedang berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
