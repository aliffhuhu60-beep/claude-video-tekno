"""Eksport EDL (CMX3600), SRT dan nota keputusan suntingan."""
import json, shutil, sys
W = "/home/user/work/"
OUT = "/home/user/claude-video-tekno/output/"
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
TL = json.load(open(W + "timeline.json")); SH = TL["shots"]
OV = json.load(open(W + "overlays.json"))
FPS = 30
REEL = {"A": "PDP", "S": "SOKONGAN", "G": "GAMEPLAY"}
NAMEF = {"A": "video pdp.mp4", "S": "video sokongan.mp4", "G": "video gameplay.mp4"}

def tc(t):
    f = int(round(t * FPS)); return f"{f // 108000:02d}:{f // 1800 % 60:02d}:{f // 30 % 60:02d}:{f % 30:02d}"

e = [f"TITLE: SIMULASI_PENGAJARAN_MIKRO_{VER}", "FCM: NON-DROP FRAME", ""]
n = 1
e += [f"{n:03d}  INTRO    V     C        00:00:00:00 00:00:08:00 {tc(0)} {tc(8)}", "* FROM CLIP NAME: intro_v1.mp4", ""]
for x in SH:
    n += 1
    tr = "D    009" if x.get("xfade_in") else "C       "
    e.append(f"{n:03d}  {REEL[x['src']]:8s} V     {tr} {tc(x['tin'])} {tc(x['tout'])} {tc(x['out_start'])} {tc(x['out_end'])}")
    e.append(f"* FROM CLIP NAME: {NAMEF[x['src']]}")
    crop = f" CROP {x['crop']}" if x.get("crop") else ""
    au = f"AUDIO PDP {tc(x['pdp'][0])}-{tc(x['pdp'][1])}" if x["audio"] == "A" else "AUDIO MUZIK (suara disenyap)"
    e.append(f"* {x['phase']} | {x['kind']} | {au}{crop}")
    e.append("")
n += 1
e += [f"{n:03d}  OUTRO    V     C        00:00:00:00 00:00:40:00 {tc(TL['body_end'])} {tc(TL['total'])}", "* FROM CLIP NAME: outro_v1.mp4", ""]
open(f"{OUT}SIMULASI_PENGAJARAN_MIKRO_{VER}.edl", "w").write("\n".join(e))
shutil.copy(W + "subs.srt", f"{OUT}SIMULASI_PENGAJARAN_MIKRO_{VER}.srt")

from collections import defaultdict
k = defaultdict(float); ph = defaultdict(float)
for x in SH:
    k[x["kind"]] += x["dur"]; ph[x["phase"]] += x["dur"]
tot = sum(k.values())
guru = k["guru"] + k["guru-wide"]
murid = k["montaj"] + k["broll"] + k["reaksi"]
def mm(t): return f"{int(t // 60):02d}:{t % 60:04.1f}"
ovl = "\n".join(f"| {mm(o['t0'])} | {o['kind']} | {(o['spec'][0] if isinstance(o['spec'], list) else (o['spec']['items'][0][2] if isinstance(o['spec'], dict) else o['spec'][0]))} | x={o['x']}, y={o['y']} |" for o in OV)
notes = f"""# Nota Keputusan Suntingan — {VER}

**Video:** SIMULASI PENGAJARAN MIKRO (MICRO TEACHING) · Bahasa Melayu Tahun 5 · SP 5.3.3
**Guru:** MOHAMAD ALIFF BIN AHMAD SHAHABUDDIN · Opsyen Bahasa Melayu, IPG Kampus Tun Hussein Onn
**Tempoh:** 30:00 tepat · 1920×1080 · 30 fps · H.264 + AAC 48 kHz stereo · −14 LUFS

## Perubahan v2 (ikut maklum balas)
- Pop-up guru: tiada lagi "Guru Pelatih"; dipaparkan pada awal Set Induksi (shot guru pertama selepas salam).
- Salam pembukaan dimasukkan (guru masuk, murid berdiri memberi salam, guru membalas).
- Scene jurukamera dibuang: setiap selang orang berdiri di dalam kelas disemak secara manual dan 41 selang jurukamera
  dikenal pasti; shot pada saat itu dipotong rapat pada guru atau diganti dengan B-roll (suara guru diteruskan).
- B-roll gameplay dipadankan dengan kandungan yang diterangkan (Jenis 1 → soalan blok warna, Jenis 2 → peti & bingkai,
  Jenis 3 → parkour, Bahagian B → stesen/Cabaran/keputusan).
- Teks panel disalin daripada teks sebenar dalam permainan Minecraft Education.
- Sari kata ditranskripsi semula (Whisper large-v3, dua versi audio + turbo) dan disemak baris demi baris; hanya
  perkataan yang disokong sekurang-kurangnya dua transkripsi dikekalkan, masa diambil daripada cap masa perkataan.
- Fail penuh 1080p dihantar dalam beberapa bahagian (stream copy, tanpa mampatan semula).

## Struktur
| Bahagian | Tempoh |
|---|---|
| Intro (grafik, tanpa klip PdP) | 00:08 |
""" + "\n".join(f"| {p} | {mm(v)} |" for p, v in ph.items()) + f"""
| Outro penghargaan (Puan Julina binti Tarikat, Keluarga BMONETHO) | 00:40 |

Peralihan: potongan terus; *cross-dissolve* 0.3 s hanya antara fasa.

## Nisbah shot (bahagian PdP)
- Guru jelas kelihatan: **{100 * guru / tot:.0f}%** (MCU/MS dipotong daripada kamera utama, berpusat pada guru melalui pengesanan YOLO)
- Aktiviti / reaksi murid / B-roll gameplay: **{100 * murid / tot:.0f}%**
- Wide kelas: **{100 * k['wide'] / tot:.0f}%**

Shot guru lebih rendah sedikit daripada sasaran 70% kerana saat jurukamera / orang berdiri di depan lensa
dibuang dan diganti dengan B-roll; suara guru diteruskan.

## Sumber & penyelarasan
- `video pdp.mp4` — kamera utama (audio utama untuk semua ucapan).
- `video sokongan.mp4` — kamera kedua pegang tangan (gabungan CapCut). Setiap klip diselaraskan berasingan dengan audio
  kamera utama (korelasi silang); hanya padanan yakin digunakan selari dengan ucapan. Klip lain hanya dalam montaj bermuzik.
  Bahagian goyang/kabur dan logo CapCut dibuang.
- `video gameplay.mp4` — rakaman skrin tablet (tiada audio), dipotong 1440×810 dan gelembung kamera hadapan (muka murid)
  dikesan & dielakkan.
- Setiap saat rakaman digunakan sekali sahaja (tiada klip berulang).

## Sari kata & kata kunci
- {sum(1 for _ in open(W + 'subs.srt')) // 4} baris, dibakar ke video (bawah-tengah, maks 2 baris, kotak hijau gelap separa lut sinar).
- Hanya baris yang jelas didengar; sembang murid, baris kabur dan nama murid dibuang.
- Kata kunci: *ayat aktif* (emas), *ayat pasif* (hijau), subjek, predikat, perbuatan, jenis kesalahan ayat.

## Grafik (kedudukan dipilih supaya tidak menutup muka)
| Masa | Jenis | Kandungan | Kedudukan |
|---|---|---|---|
{ovl}

Kandungan panel disalin daripada narator video Set Induksi, papan putih (objektif), slaid *Cara Bermain Misi Ayat* dan skrin
permainan (ayat yang ditaip murid).

## Audio
Suara guru: high-pass 100 Hz, nyah-hingar ringan, +4.5 dB @ 3 kHz, pemampat 3:1. Tiada muzik semasa guru mengajar —
muzik (asli, disintesis) hanya pada intro, montaj aktiviti dan outro. SFX halus (whoosh kad fasa, chime pop-up) hanya
pada saat tiada ucapan. Kenyaringan akhir −14 LUFS, true peak ≤ −1 dBTP.

## Perkara untuk disemak
- RPH menyebut Tema *Alam Sekitar* / Tajuk *Hotel Hijau*, tetapi papan putih dalam rakaman menulis Tema *Teknologi dan
  Inovasi* / Tajuk *Ekspedisi Ayat* — intro hanya memaparkan SP 5.3.3.
- Ayat murid "Minecraft dimainkan oleh saya" dikekalkan dalam sari kata (seperti dituturkan) tetapi tidak dijadikan
  panel (bercanggah dengan peraturan pelaku *saya* dalam bahan pelajaran sendiri).
- Sila sahkan kebenaran penerbitan wajah murid/rakan.
- Fail asal di Google Drive tidak diubah atau dipadam.
"""
open(f"{OUT}NOTA_SUNTINGAN_{VER}.md", "w").write(notes)
print("dokumen siap")
