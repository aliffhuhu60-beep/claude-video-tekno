"""Render akhir: BMONETHO_SIMULASI_PENGAJARAN_MIKRO_FINAL_30_MINIT.mp4

1. Klip grafik beralfa (intro 0–7.8 s, outro 1789.6–1800 s) daripada cine3.graphic()
2. Muzik asli untuk intro/outro sahaja (tidak bertindih dengan ucapan asal)
3. FFmpeg: video tanpa sari kata dianjak +2.600 s (tpad hitam), tindihan kad, sari kata ASS,
   audio asal dianjak +2.600 s tanpa sebarang pemprosesan + muzik intro/outro.
4. Fail intro & outro berasingan (kad di atas latar hitam + muzik).
Fail asal tidak diubah.
"""
import os, subprocess, sys, json, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import cine3 as C
import intro_outro as IO

W = "/home/user/work/"
OUT = "/home/user/claude-video-tekno/output/final/"
os.makedirs(OUT, exist_ok=True)
CLEAN = "/home/user/raw2/video_tanpa_sk.mp4"
FPS = 30
INTRO_T = (0.0, C.IN_HOLD + C.IN_FADE)          # 0 – 7.8
OUTRO_T = (C.OUT_IN0, C.TOTAL)                   # 1789.6 – 1800
SR = 44100

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)
    return r

def overlay_clip(t0, t1, path):
    n = int(round((t1 - t0) * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "1920x1080", "-r", "30",
                          "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", path], stdin=subprocess.PIPE)
    from PIL import Image
    blank = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)).tobytes()
    for i in range(n):
        g = C.graphic(t0 + i / FPS)
        p.stdin.write(blank if g is None else g.tobytes())
    p.stdin.close(); p.wait()
    print("klip grafik", path, n)

def music_wav(dur, path, seed, fade_in=0.05):
    IO.music(dur, path, seed=seed)                    # -> path.wav (48 kHz, -14 LUFS)
    run(["ffmpeg", "-v", "error", "-y", "-i", path + ".wav", "-ar", str(SR),
         "-af", f"volume=-6dB,afade=t=in:d={fade_in}", path + "_44.wav"])
    return path + "_44.wav"

def main():
    io_mov, oo_mov = W + "intro_ovl.mov", W + "outro_ovl.mov"
    if not os.path.exists(io_mov): overlay_clip(*INTRO_T, io_mov)
    if not os.path.exists(oo_mov): overlay_clip(*OUTRO_T, oo_mov)
    m_in = music_wav(3.4, W + "mus_intro", 3)           # 0 – 3.4 (pudar keluar sebelum ucapan pertama 10.1 s)
    m_out = music_wav(C.TOTAL - C.E, W + "mus_outro", 11, fade_in=0.3)   # 1797.8 – 1800 (selepas audio asal tamat)

    final = OUT + "BMONETHO_SIMULASI_PENGAJARAN_MIKRO_FINAL_30_MINIT.mp4"
    S_ms = int(C.S * 1000); E_ms = int(round(C.E * 1000))
    fc = (
        f"[0:v]tpad=start_duration={C.S}:stop_duration={C.TOTAL - C.E:.3f}:color=black,setpts=PTS-STARTPTS[base];"
        f"[1:v]setpts=PTS-STARTPTS[iov];"
        f"[2:v]setpts=PTS-STARTPTS+{OUTRO_T[0]}/TB[oov];"
        f"[base][iov]overlay=0:0:eof_action=pass[v1];"
        f"[v1][oov]overlay=0:0:eof_action=pass[v2];"
        f"[v2]subtitles={W}subs3.ass:fontsdir=/usr/share/fonts/opentype/inter,format=yuv420p[v];"
        f"[0:a]adelay={S_ms}|{S_ms}[oa];"
        f"[3:a]apad[mi];"
        f"[4:a]adelay={E_ms}|{E_ms}[mo];"
        f"[oa][mi][mo]amix=inputs=3:duration=longest:normalize=0,apad,atrim=0:{C.TOTAL}[a]"
    )
    run(["ffmpeg", "-v", "error", "-y", "-i", CLEAN, "-i", io_mov, "-i", oo_mov, "-i", m_in, "-i", m_out,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{C.TOTAL:.3f}", "-r", "30",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-g", "60", "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-ac", "2", "-movflags", "+faststart", final])
    print("siap", final)

    # intro & outro berasingan (kad di atas hitam + muzik)
    for mov, mus, dur, name in ((io_mov, m_in, INTRO_T[1] - INTRO_T[0], "INTRO"),
                                (oo_mov, m_out, OUTRO_T[1] - OUTRO_T[0], "OUTRO")):
        delay = 0 if name == "INTRO" else int(round((C.E - OUTRO_T[0]) * 1000))
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s=1920x1080:r=30:d={dur:.3f}", "-i", mov, "-i", mus,
             "-filter_complex", f"[0:v][1:v]overlay=0:0,format=yuv420p[v];[2:a]adelay={delay}|{delay},apad,atrim=0:{dur:.3f}[a]",
             "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
             "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", OUT + f"BMONETHO_{name}.mp4"])
    print("intro/outro siap")

if __name__ == "__main__":
    main()
