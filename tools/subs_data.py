"""Sari kata terpilih (masa = saat dalam rakaman kamera utama pdp.mp4).

Hanya baris yang jelas didengar dalam transkrip disalin. Baris yang kabur, sembang
murid dan sebutan nama murid dibuang. Setiap (mula, tamat) ialah julat ucapan;
tempoh paparan sebenar dikira semula ikut kelajuan bacaan.
"""

SUBS = [
    # SET INDUKSI
    (10.0, 16.5, "Waalaikumussalam, murid-murid. Baiklah, duduk semua."),
    (20.1, 26.0, "Baiklah, cikgu mulakan aktiviti kita pada hari ini."),
    (30.5, 37.0, "Ayat aktif menunjukkan subjek melakukan perbuatan."),
    (37.0, 43.0, "Contohnya, Ali menanam pokok."),
    (43.0, 51.0, "Ayat pasif menunjukkan subjek menerima perbuatan."),
    (51.0, 58.4, "Contohnya, pokok ditanam oleh Ali."),
    (60.0, 66.0, "Ayat aktif, subjek melakukan perbuatan."),
    (66.0, 72.0, "Ayat pasif, subjek menerima perbuatan."),
    (76.0, 86.0, "Melalui video tadi, cikgu nak tanya apa yang kamu nampak daripada video tadi."),
    (90.0, 97.5, "Saya nampak... mari kita terokai ayat aktif dan ayat pasif."),
    (97.5, 100.0, "Betul."),
    (102.0, 109.0, "Sekarang ni, dalam video tadi ada menerangkan tentang ciri-ciri ayat aktif dan ayat pasif."),
    (109.5, 115.5, "Kamu semua senaraikan ciri-ciri itu di papan putih."),
    (331.0, 336.5, "Sekarang ni cikgu nak kita ulang sekali lagi ciri-ciri ayat aktif dan ayat pasif ini."),
    (336.5, 340.4, "Sama-sama dengan cikgu. Satu, dua, mula."),
    (375.8, 386.5, "Dalam masa 30 minit, cikgu berharap murid dapat menjawab 5 soalan bagi 3 jenis kesalahan ayat dalam Minecraft Education dengan betul."),
    (386.5, 395.2, "Dan yang kedua, murid dapat membina sekurang-kurangnya dua ayat aktif dan pasif berdasarkan situasi di stesen Minecraft Education."),
    (401.5, 404.0, "Boleh tak? Siapa boleh tahu?"),
    (406.0, 410.5, "Saya akan main Minecraft."),
    (410.6, 412.8, "Main Minecraft apa? — Education."),
    (412.9, 413.9, "Betul."),
    # LANGKAH 1
    (450.0, 455.0, "Sekarang ni cikgu nak hos permainan ni."),
    (455.5, 460.0, "Sekarang kod dia dah keluar."),
    (487.5, 493.3, "Wow. Cikgu buat sendiri ke? — Ya."),
    (496.4, 502.3, "Okey, sebelum kita main, cikgu nak terangkan dulu."),
    (502.4, 509.3, "Minecraft Education ni ada 2 bahagian."),
    (510.0, 518.2, "Bahagian pertama, Misi Penyelamat Ayat, iaitu kamu akan baiki 3 jenis kesalahan ayat."),
    (518.6, 524.3, "Ayat tanpa subjek, ayat tidak lengkap dan bahasa rojak."),
    (525.0, 533.1, "Lepas siap bahagian itu, barulah kita masuk ke bahagian B, Ekspedisi Ayat Aktif dan Pasif."),
    (552.0, 561.0, "Baiklah, dalam Misi Penyelamat Ayat ini, mereka akan baca poster yang berada di sini."),
    (641.0, 643.0, "Yang hijau tu untuk individu."),
    (646.0, 648.0, "Sekarang ni cikgu nak letakkan setiap kumpulan."),
    (679.0, 685.0, "Baiklah, sekarang kamu berada di lobi, jenis yang pertama, ayat tanpa subjek."),
    (685.0, 692.0, "Di ruang ini kamu perlu menjawab soalan dengan memijak blok warna untuk beri jawapan."),
    (702.0, 710.0, "Bila dah nampak papan macam ni, cikgu nak kamu baca soalan dulu, dan pilihan jawapannya ada pada papan."),
    (750.0, 758.0, "Dalam bahagian ini, kamu kena jawab 5 soalan dengan betul. Barulah kamu boleh pergi ke jenis yang baru."),
    (845.0, 849.7, "Kumpulan ini telah berjaya menjawab jenis yang pertama."),
    (852.0, 857.0, "Jenis kedua, ayat tidak lengkap."),
    (870.0, 875.0, "Kedua ialah predikat ayat. Predikat mana yang sesuai dengan subjek ayat?"),
    (876.0, 881.0, "Bila dah dapat kedua-dua ayat tu, letak di bahagian bingkai."),
    (990.0, 996.0, "Bahagian ni sama juga. Kamu kena betul 5, barulah boleh pergi ke bahagian yang ketiga."),
    (1170.0, 1179.0, "Kita akan lihat papan kedudukan nanti."),
    (1354.5, 1359.0, "Murid yang dapat betul 5 akan ke lobi jenis yang ketiga."),
    (1359.0, 1364.0, "Di lobi jenis yang ketiga, murid akan dapat masa 30 saat untuk baca bahan yang ada."),
    (1369.0, 1375.0, "Baiklah, pada jenis yang ketiga, awak akan baca soalan dan pilihan jawapan yang ada."),
    (1375.0, 1379.2, "Tapi untuk menjawab, awak perlu melompat."),
    (1405.0, 1408.0, "Sekarang awak berada di lobi jenis yang ketiga."),
    # LANGKAH 2
    (2055.0, 2062.0, "Melalui situasi tersebut, cikgu nak kamu bina ayat aktif dan ayat pasif."),
    (2151.0, 2154.0, "Di sini kamu boleh bina ayat."),
    (2192.0, 2198.0, "Nampaknya kita kena jawab satu ayat aktif."),
    (2210.0, 2211.0, "Ayat aktif."),
    (2225.0, 2228.0, "Kamu pilih satu situasi."),
    (2260.6, 2265.0, "Kamu berkumpul di bahagian cikgu."),
    (2344.0, 2347.0, "Cikgu nak kamu jawab soalan yang terakhir."),
    (2347.0, 2352.0, "Kalau kamu boleh jawab soalan ini, maknanya tercapailah objektif cikgu pada hari ini."),
    # PENUTUP
    (2742.0, 2744.0, "Apa yang kamu rasa hari ini?"),
    (2790.0, 2800.8, "Saya rasa saya boleh membina ayat aktif untuk cikgu."),
    (2800.8, 2803.0, "Okey, apa ayatnya?"),
    (2807.2, 2810.0, "Okey, betul."),
    (2812.0, 2817.0, "Saya berasa sangat teruja untuk bermain Minecraft."),
    (2828.0, 2830.0, "Okey, betul."),
    (2838.0, 2841.0, "Sekian, terima kasih."),
    (2845.0, 2848.0, "Terima kasih, cikgu."),
    (2850.0, 2855.0, "Sama-sama semua. Jumpa lagi."),
]

# Istilah ditonjolkan: (frasa, warna)  emas = istilah utama, hijau = istilah pasangan/contoh
KEY = [
    ("ayat aktif", "gold"), ("ayat pasif", "green"), ("Ayat aktif", "gold"), ("Ayat pasif", "green"),
    ("Ayat Aktif", "gold"), ("Pasif", "green"),
    ("subjek", "green"), ("predikat", "green"), ("perbuatan", "green"),
    ("menanam", "gold"), ("ditanam oleh", "green"),
    ("kesalahan ayat", "gold"), ("ayat tanpa subjek", "green"), ("Ayat tanpa subjek", "green"),
    ("ayat tidak lengkap", "green"), ("bahasa rojak", "green"),
    ("Misi Penyelamat Ayat", "gold"), ("Ekspedisi Ayat", "gold"), ("Minecraft Education", "green"),
]
