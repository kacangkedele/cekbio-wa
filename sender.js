const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const P = require('pino');
const config = require('./config.json');

const app = express();
app.use(express.json()); // Tambahkan ini untuk baca JSON dari Python
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
        } catch (err) {
            console.log('❌ Gagal meminta kode pairing.', err);
        }
    }
}

startWhatsApp();

// API CEK 1 NOMOR
app.get('/cek', async (req, res) => {
    const nomor = req.query.nomor;
    if (!nomor) return res.json({ status: false, bio: "Nomor tidak ada" });
    
    const jid = nomor.replace(/\D/g, '') + "@s.whatsapp.net";
    try {
        if (!sock || !sock.user) return res.json({ status: false, bio: "Sender WA offline!" });
        const status = await sock.fetchStatus(jid);
        res.json({ status: true, bio: status.status || "Bio tidak tersedia" });
    } catch (err) {
        res.json({ status: false, bio: "Nomor tidak terdaftar di WA / Private" });
    }
});

// API CEK MASSAL (Baca file)
app.post('/masscek', async (req, res) => {
    const numbers = req.body.numbers;
    if (!numbers || !Array.isArray(numbers)) return res.json({ status: false, error: "Format salah" });
    
    let stats = {
        total: numbers.length,
        registered: 0,
        notRegistered: 0,
        hasBio: 0,
        noBio: 0,
        business: 0
    };

    console.log(`Menerima request massal cek ${numbers.length} nomor...`);

    for (const num of numbers) {
        const jid = num.replace(/\D/g, '') + "@s.whatsapp.net";
        try {
            const [result] = await sock.onWhatsApp(jid);
            if (result && result.exists) {
                stats.registered++;
                
                // Cek Bio
                try {
                    const status = await sock.fetchStatus(jid);
                    if (status && status.status && status.status.trim() !== "") {
                        stats.hasBio++;
                    } else {
                        stats.noBio++;
                    }
                } catch (e) {
                    stats.noBio++;
                }

                // Cek Business
                try {
                    const biz = await sock.getBusinessProfile(jid);
                    if (biz) stats.business++;
                } catch (e) {}

            } else {
                stats.notRegistered++;
            }
        } catch (err) {
            stats.notRegistered++;
        }
        await new Promise(resolve => setTimeout(resolve, 300)); // Jeda 300ms agar tidak banned
    }

    console.log("Selesai cek massal.");
    res.json({ status: true, stats: stats });
});

app.listen(3000, () => console.log('🟢 API Sender jalan di port 3000'));
