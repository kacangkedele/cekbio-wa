// #TERMUX# // 
const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const express = require('express');
const P = require('pino');
const config = require('./config.json');

const app = express();
let sock;

async function startWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version } = await fetchLatestBaileysVersion();
    
    sock = makeWASocket({
        version,
        auth: state,
        logger: P({ level: 'silent' }),
        printQRInTerminal: false
    });

    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', (update) => {
        if (update.connection === 'open') {
            console.log('✅ WhatsApp Sender Berhasil Terhubung!');
        }
        if (update.connection === 'close') {
            console.log('❌ Koneksi WA terputus. Mencoba menghubungkan kembali dalam 5 detik...');
            setTimeout(() => startWhatsApp(), 5000); // Jeda 5 detik biar gak spam
        }
    });

    if (!state.creds.registered && config.WA_NUMBER) {
        // Ambil nomor murni tanpa @s.whatsapp.net
        const phoneNumber = config.WA_NUMBER.replace(/\D/g, '');
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
            // Request pairing code hanya dengan format angka
            const code = await sock.requestPairingCode(phoneNumber);
            console.log('\n========================================');
            console.log('🔑 KODE PAIRING ANDA:', code);
            console.log('========================================');
            console.log('Buka WhatsApp > Perangkat Tertaut > Tautkan Perangkat > Masukkan Kode.');
            console.log('========================================\n');
        } catch (err) {
            console.log('❌ Gagal meminta kode pairing.');
        }
    }
}

startWhatsApp();

// API Lokal untuk Bot Python
app.get('/cek', async (req, res) => {
    const nomor = req.query.nomor;
    if (!nomor) return res.json({ status: false, bio: "Nomor tidak ada" });
    
    const jid = nomor.replace(/\D/g, '') + "@s.whatsapp.net";
    try {
        const status = await sock.fetchStatus(jid);
        res.json({ status: true, bio: status.status || "Bio tidak tersedia" });
    } catch (err) {
        res.json({ status: false, bio: "Nomor tidak terdaftar di WA / Gagal" });
    }
});

app.listen(3000, () => console.log('🟢 API Sender jalan di port 3000'));
EOF
