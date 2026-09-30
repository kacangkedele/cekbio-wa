```markdown
# 🤖 Bot By Angga Official - CekBio WA

Bot Telegram canggih untuk pengecekan Bio WhatsApp dengan sistem tiering (Free, VIP, XVIP, VVIP) dan integrasi pembayaran QRIS semi-otomatis. Dibangun dengan `python-telegram-bot` versi 20+ dan database SQLite agar data tahan banting saat dijalankan di Termux.

## ✨ Fitur Utama
- 🔍 **CekBio WhatsApp:** Deteksi nomor dan bio WhatsApp pengguna.
- 📊 **Sistem Limit Harian:** Batas deteksi otomatis reset setiap hari.
- 💎 **Sistem Tier Premium:** Free, VIP, XVIP, VVIP dengan limit masing-masing.
- 🛒 **Pembayaran QRIS:** Kirim gambar QRIS otomatis ke pengguna, terima bukti transfer, dan verifikasi oleh Admin.
- 🗄️ **Database Permanen:** Menggunakan SQLite (`cekbio.db`) sehingga data pengguna, limit, dan statistik tidak hilang saat bot di-restart.
- 📱 **Termux Ready:** Dioptimalkan untuk berjalan langsung dari ponsel Android menggunakan Termux.

---

## 🛠️ Prasyarat
Sebelum memulai, pastikan Anda memiliki:
1. **Token Bot Telegram** (Dapat dari [@BotFather](https://t.me/BotFather)).
2. **ID Telegram Anda** (Dapat dari [@userinfobot](https://t.me/userinfobot)).
3. Aplikasi **Termux** di Android (Jalankan dari Play Store atau F-Droid).

---

## 📲 Cara Install & Menjalankan di Termux

Ikuti langkah-langkah berikut secara berurutan di aplikasi Termux Anda:

### 1. Update & Install Dependensi
Masukkan perintah berikut untuk memperbarui paket Termux dan menginstall Python serta Git:
```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

### 2. Clone Repository
Unduh kode bot dari GitHub ke penyimpanan Termux Anda:
```bash
git clone https://github.com/kacangkedele/cekbio-wa
cd cekbio-wa
```

### 3. Install Library Python
Install semua kebutuhan library yang ada di file `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Bot
Edit file `config.py` untuk memasukkan Token Bot dan ID Admin Anda:
```bash
nano config.py
```
*Ubah bagian `BOT_TOKEN` dan `ADMIN_ID` dengan data Anda. Jika sudah selesai, tekan `CTRL+X`, lalu `Y`, dan `Enter` untuk menyimpan.*

### 5. Jalankan Bot
Mulai jalankan bot dengan perintah:
```bash
python bot.py
```
Jika muncul tulisan `"Bot By Angga Official sedang berjalan di Termux..."`, berarti bot Anda sudah online! Buka Telegram dan coba ketik `/start` di bot Anda.

---

## ⚙️ Konfigurasi File `config.py`
Pastikan Anda mengisi data berikut dengan benar:
```python
BOT_TOKEN = "TOKEN_BOT_DARI_BOTFATHER"
ADMIN_ID = 123456789  # ID Telegram Anda (berupa angka, bukan username)
ADMIN_USERNAME = "UsernameAdminAnda"  # Username Anda tanpa tanda @
CHANNEL_URL = "https://t.me/LinkChannelAnda"
QRIS_IMAGE_URL = "URL_GAMBAR_QRIS_ANDA"
```

---

## 🎮 Daftar Perintah (Commands)

### Perintah Pengguna:
- `/start` - Menampilkan menu utama dan info pengguna.
- `/premium` - Menampilkan daftar paket premium dan harga.
- `/detek <nomor>` - Mengecek bio WhatsApp. Contoh: `/detek +628123456789`

### Perintah Khusus Admin:
- `/upgrade <ID_User> <Tier> <Jumlah_Hari>` - Mengaktifkan premium user secara manual setelah verifikasi pembayaran.
  - **Contoh:** `/upgrade 6281234567 VIP 30`

---

## 🔄 Alur Pembayaran QRIS (Semi-Otomatis)
1. Pengguna menekan tombol "Beli VIP".
2. Bot otomatis mengirimkan gambar QRIS dan nominal yang harus dibayar.
3. Pengguna melakukan pembayaran via OVO/Dana/GoPay/Bank.
4. Pengguna mengirimkan **screenshot bukti pembayaran** ke chat bot.
5. Bot meneruskan bukti pembayaran tersebut ke chat **Admin** beserta detail user.
6. Admin mengecek penerimaan dana, lalu mengetik command `/upgrade <ID> <Tier> <Hari>`.
7. Bot otomatis memperbarui status pengguna menjadi VIP dan mengirim notifikasi selamat kepada pengguna.

---

## ❓ Troubleshooting
- **Bot mati saat Termux di-tutup:** 
  Ini wajar. Untuk menjalankan bot 24 jam di latar belakang, Anda bisa menggunakan layanan seperti `screen` atau `tmux` di Termux, atau menjalankannya di server VPS.
- **Error `ModuleNotFoundError`:**
  Pastikan Anda sudah menjalankan `pip install -r requirements.txt` di dalam folder `cekbio-wa`.

---
Dibuat dengan ❤️ oleh [Angga Official](https://github.com/kacangkedele)
🏠.(https://youtube.com/@bacotamatpro03).
``` 

