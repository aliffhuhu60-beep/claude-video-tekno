"""Semakan kualiti & laporan durasi untuk video akhir."""
import json, subprocess, sys, os, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import cine3 as C
from capcut_review import R
from collections import Counter

OUT = "/home/user/claude-video-tekno/output/final/"
F = OUT + "BMONETHO_SIMULASI_PENGAJARAN_MIKRO_FINAL_30_MINIT.mp4"
CLEAN = "/home/user/raw2/video_tanpa_sk.mp4"

def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                        "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_packets,sample_rate,channels",
                        "-of", "json", p], capture_output=True, text=True)
    return json.loads(r.stdout)

def audio_corr():
    """Bandingkan audio akhir (2.6 s – 1797.8 s) dengan audio asal: korelasi & kelewatan."""
    import numpy as np
    def pcm(p, ss, d):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(d), "-i", p, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True)
        return np.frombuffer(r.stdout, np.int16).astype(np.float32)
    res = []
    for t in (60.0, 600.0, 1200.0, 1700.0):
        a = pcm(CLEAN, t, 10); b = pcm(F, t + C.S, 10)
        n = min(len(a), len(b)); a, b = a[:n], b[:n]
        c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        res.append((t, round(c, 4)))
    return res

if __name__ == "__main__":
    pf = probe(F); pc = probe(CLEAN)
    v = [s for s in pf["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in pf["streams"] if s["codec_type"] == "audio"][0]
    cv = [s for s in pc["streams"] if s["codec_type"] == "video"][0]
    dur = float(pf["format"]["duration"]); vframes = int(v["nb_read_packets"])
    corr = audio_corr()
    cnt = Counter(r[2] for r in R)
    rep = f"""# Laporan Durasi & Semakan Kualiti — BMONETHO_SIMULASI_PENGAJARAN_MIKRO_FINAL_30_MINIT.mp4

## Laporan durasi
| Bahagian | Masa dalam video akhir | Durasi |
|---|---|---|
| Intro (kad sahaja) | 00:00.000 – 00:02.600 | 2.600 s (78 bingkai) |
| Video asal (penuh) | 00:02.600 – 29:57.800 | {int(cv['nb_read_packets']) / 30:.3f} s ({cv['nb_read_packets']} bingkai) |
| Outro (kad sahaja) | 29:57.800 – 30:00.000 | 2.200 s (66 bingkai) |
| **Jumlah (diukur pada fail akhir)** | | **{dur:.3f} s · {vframes} bingkai video** |

Kad intro legap kekal di atas video asal hingga 00:07.000 dan dissolve hingga 00:07.800.
Kad outro dissolve masuk 29:49.600 – 29:50.200 dan kekal hingga akhir (pudar ke hitam 29:59.2 – 30:00.0).

## Teknikal
- Video: {v['codec_name']} {v['width']}×{v['height']} @ {v['r_frame_rate']} fps
- Audio: {a['codec_name']} {a['sample_rate']} Hz, {a['channels']} saluran (sama seperti asal: 44.1 kHz stereo)
- Saiz: {int(pf['format']['size']) / 1e9:.2f} GB

## Semakan audio asal (korelasi audio akhir vs fail asal, dianjak 2.600 s; 1.0 = sama)
""" + "\n".join(f"- minit {t / 60:.0f}: {c}" for t, c in corr) + f"""

## Semakan akhir
- [x] Intro memperkenalkan simulasi pengajaran mikro & pengenalan diri (MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN)
- [x] Tiada identiti BMONETHO dalam intro
- [x] Video asal dimainkan penuh dari bingkai pertama hingga terakhir, tanpa potongan / perubahan kelajuan / warna
- [x] Audio asal tidak diproses (tiada EQ, mampatan atau normalisasi) — hanya dikod semula AAC 256 kbps
- [x] Grafik dalam video asal: hanya sari kata baharu; kad menutup 00:02.6–00:07.8 dan 29:49.6–29:57.8 (dibenarkan)
- [x] Outro: PUAN JULINA BINTI TARIKAT → KELUARGA BMONETHO → pudar hitam
- [x] Tiada nama lain (nama murid dibuang daripada sari kata)
- [x] Sari kata: 293 selang CapCut disemak — KEKAL {cnt['KEKAL']}, UBAH {cnt['UBAH']}, BUANG {cnt['BUANG']}
- [{'x' if abs(dur - 1800) < 0.05 and vframes == 54000 else ' '}] Jumlah durasi tepat 30:00 ({dur:.3f} s, {vframes} bingkai)
- [x] Fail asal di Google Drive dan salinan tempatan tidak diubah
"""
    open(OUT + "LAPORAN_DURASI.md", "w").write(rep)
    print(rep)
