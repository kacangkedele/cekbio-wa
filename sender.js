const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const P = require('pino');
const config = require('./config.json');

const app = express();
let sock;

async function startWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`Menggunakan Baileys versi: ${version}, Terbaru: ${isLatest}`);
    
    sock = makeWASocket({
        version,
        auth: state,
        logger: P({ level: 'warn' }),
        printQRInTerminal: false
    });

    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'open') {
            console.log('✅ WhatsApp Sender Berhasil Terhubung!');
        } else if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            console.log(`❌ Koneksi WA terputus. Status Code: ${statusCode || 'Tidak diketahui'}`);
            
            if (statusCode !== 410 && statusCode !== 401) {
                console.log('Mencoba menghubungkan kembali dalam 5 detik...');
                setTimeout(() => startWhatsApp(), 5000);
            } else {
                console.log('❌ Akun keluar/blockir. Hapus folder auth_info_baileys dan coba lagi.');
            }
        }
    });

    if (!state.creds.registered && config.WA_NUMBER) {
        const phoneNumber = config.WA_NUMBER.replace(/\D/g, '');
        await new Promise(resolve => setTimeout(resolve, 3000));
        try {
            const code = await sock.requestPairingCode(phoneNumber);
            console.log('\n========================================');
            console.log('🔑 KODE PAIRING ANDA:', code);
            console.log('========================================');
            console.log('Buka WhatsApp > Perangkat Tertaut > Tautkan Perangkat > Masukkan Kode.');
            console.log('========================================\n');
        } catch (err) {
            console.log('❌ Gagal meminta kode pairing.', err);
        }
    }
}

startWhatsApp();

app.get('/cek', async (req, res) => {
    const nomor = req.query.nomor;
    if (!nomor) return res.json({ status: false, bio: "Nomor tidak ada" });
    
    const jid = nomor.replace(/\D/g, '') + "@s.whatsapp.net";
    console.log(`Menerima request cek nomor: ${jid}`);
    
    try {
        if (!sock || !sock.user) {
            return res.json({ status: false, bio: "Sender WA belum siap/sedang offline!" });
        }
        const status = await sock.fetchStatus(jid);
        console.log("Berhasil ambil bio:", status.status);
        res.json({ status: true, bio: status.status || "Bio tidak tersedia" });
    } catch (err) {
        console.error("❌ Error saat fetchStatus:", err.message);
        res.json({ status: false, bio: "Nomor tidak terdaftar di WA / Private" });
    }
});

app.listen(3000, () => console.log('🟢 API Sender jalan di port 3000'));
