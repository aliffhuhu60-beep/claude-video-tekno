"""Bina sari kata baharu (ASS + SRT) daripada semakan CapCut. Masa dalam video akhir (+2.600 s)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from capcut_review import R
from subs_data import KEY
import cine3 as C

W = "/home/user/work/"
SEG = json.load(open(W + "cap_segs.json"))
KEY = KEY + [("objektif", "gold"), ("Galeri Isu", "green"), ("Cabaran Akhir", "gold"), ("PETI 1", "green"),
             ("PETI 2", "green"), ("bingkai", "green"), ("parkour", "green"), ("kata kerja transitif", "gold"),
             ("stesen", "green"), ("lobi", "green")]

def items():
    out = []
    for idx, cap, dec, new in R:
        if dec == "BUANG" or not new:
            continue
        a = SEG[idx[0]][0]; b = SEG[idx[-1]][1]
        out.append([a + C.S, b + C.S, new, dec, cap, idx])
    out.sort(key=lambda x: x[0])
    for i, it in enumerate(out):                       # paparan minimum 1.0 s, +0.15 s bacaan
        nxt = out[i + 1][0] - 0.04 if i + 1 < len(out) else C.TOTAL
        it[1] = min(max(it[1] + 0.15, it[0] + 1.0), nxt)
    return out

def colorize(text):
    keys = sorted(KEY, key=lambda k: -len(k[0]))
    col = {"gold": r"{\b1\c&H37AFD4&}", "green": r"{\b1\c&H62B06E&}"}
    out, i = "", 0
    while i < len(text):
        for k, c in keys:
            if text[i:i + len(k)].lower() == k.lower() and (i == 0 or not text[i - 1].isalnum()) \
                    and (i + len(k) >= len(text) or not text[i + len(k)].isalnum()):
                out += col[c] + text[i:i + len(k)] + r"{\b0\c&HFFFFFF&}"; i += len(k); break
        else:
            out += text[i]; i += 1
    return out

def wrap2(text, n=48):
    if len(text) <= n:
        return [text]
    words = text.split(); best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]: best = (sc, a, b)
    return [best[1], best[2]]

def ts(t, ass=True):
    if ass:
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

if __name__ == "__main__":
    its = items()
    ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Sub,Inter SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H3A2C3B0B,&H3A2C3B0B,0,0,0,0,100,100,0,0,3,14,0,2,120,120,60,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    srt = []
    for i, (a, b, t, *_r) in enumerate(its):
        lines = wrap2(t)
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{chr(92).join([''] * 0) + (chr(92) + 'N').join(colorize(l) for l in lines)}")
        srt += [str(i + 1), f"{ts(a, False)} --> {ts(b, False)}", "\n".join(lines), ""]
    open(W + "subs3.ass", "w").write("\n".join(ass) + "\n")
    open(W + "subs3.srt", "w").write("\n".join(srt))
    json.dump(its, open(W + "subs3.json", "w"), ensure_ascii=False)
    print("sari kata", len(its))
