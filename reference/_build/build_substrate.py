#!/usr/bin/env python3
# Build a verified per-chapter substrate from authoritative sources.
# Sources (fetched verbatim via curl):
#   - ctext.org gettext API: ctp:dao-de-jing  (received/王弼 text)
#   - 维基文库 老子道德經注 (王弼注本, 華亭張氏原本): 经文 + 王弼注
#   - 维基文库 老子河上公章句 (道經/德經): 章题 + 经文 + 河上公注
# Conversion: opencc t2s (traditional -> simplified), validated against curated chapters.
import json, re, pathlib
from opencc import OpenCC
cc = OpenCC('t2s')
BUILD = pathlib.Path(__file__).resolve().parent
S = BUILD / 'sources'
SUB = BUILD / 'substrate.json'

DIG={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
def cn2int(s):
    s=s.strip()
    if s=='十': return 10
    if '十' in s:
        a,b=s.split('十'); return (DIG.get(a,1) if a else 1)*10+(DIG.get(b,0) if b else 0)
    return DIG.get(s,0)

NOTE_RE = re.compile(r'\{\{\*\|\s*(.*?)\s*\}\}', re.S)

# --- normalization: strip MediaWiki langconv, map variant/rare glyphs & punctuation ---
LANGCONV = re.compile(r'-\{(.*?)\}-', re.S)
def _lc(m):
    inner = m.group(1)
    for key in ('zh-hans', 'zh-cn', 'zh-sg', 'zh-hk', 'zh-tw', 'zh'):
        mm = re.search(key + r'\s*:\s*([^;}]+)', inner)
        if mm: return mm.group(1).strip()
    return inner.strip()  # simple -{X}- escape: keep inner
# rare glyphs opencc leaves unconverted, keyed by codepoint (astral-safe)
VARIANT = {0x7DDC: '绵', 0x25874: '稽', 0x2620E: '繟', 0x2B35A: '妖'}
SMALL   = {0xFE17: '！', 0xFE55: '：', 0xFE50: '、', 0xFE51: '，', 0xFE54: '；', 0xFE56: '？', 0xFE13: '：',
           ord('﹗'): '！', ord('﹕'): '：', ord('﹑'): '、', ord('﹐'): '，', ord('﹔'): '；', ord('﹖'): '？', ord('︰'): '：'}
ASCIIP  = {',': '，', ';': '；', '!': '！', '?': '？'}          # half-width -> full-width when CJK-adjacent
TRANS = {**VARIANT, **SMALL}

def clean(t):
    """Raw wikitext cleanup, applied PRE-conversion."""
    t = LANGCONV.sub(_lc, t)
    t = re.sub(r"'''?", '', t)
    t = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\[\[([^\]]*)\]\]', r'\1', t)
    return t.strip()

def post(t):
    """Glyph/punctuation normalization, applied AFTER opencc conversion
    (opencc t2s emits rare glyphs like 繟->𦈎, 綿->緜; remap to recognizable forms)."""
    t = t.translate(TRANS)
    t = re.sub(r'(?<=[一-鿿])([,;!?])', lambda m: ASCIIP[m.group(1)], t)
    return t

def parse_jing_zhu(body, stop_on_heading=True):
    """Return (joined_jing, seq) where seq is an ordered list of
    {'t':'jing'|'zhu','s':text} preserving the original 经-注 interleaving.
    经文 = non-':' lines; 注 = ':{{*| ... }}' blocks (may span lines)."""
    seq=[]; jing_lines=[]; in_note=False; note_buf=[]
    def emit(t,s):
        s=post(cc.convert(s)).strip()
        if s: seq.append({'t':t,'s':s})
    for line in body.splitlines():
        s=line.rstrip()
        if not s.strip(): continue
        if stop_on_heading and re.match(r'^=+.*=+\s*$', s): break
        if in_note:
            note_buf.append(s)
            if '}}' in s:
                in_note=False
                m=NOTE_RE.search('\n'.join(note_buf))
                emit('zhu', clean(m.group(1)) if m else clean('\n'.join(note_buf).replace(':{{*|','').replace('}}','')))
                note_buf=[]
            continue
        if s.startswith(':'):
            if '{{*|' in s and '}}' not in s:
                in_note=True; note_buf=[s]; continue
            m=NOTE_RE.search(s)
            emit('zhu', clean(m.group(1)) if m else clean(re.sub(r'^:+','',s))); continue
        jl=clean(s); jing_lines.append(jl); emit('jing', jl)
    return ''.join(jing_lines), seq

# ---------- 王弼 ----------
raw = (S/'ws_wangbi.txt').read_text()
wb={}
parts=re.split(r'^==\s*([一二三四五六七八九十]+)\s*章\s*==\s*$', raw, flags=re.M)
for i in range(1,len(parts),2):
    n=cn2int(parts[i]); body=parts[i+1]
    jing,seq=parse_jing_zhu(body, stop_on_heading=True)
    wb[n]={'jing':post(cc.convert(jing)),'seq':seq}

# ---------- 河上公 ----------
def parse_hsg(path, start_ch):
    raw=(path).read_text()
    segs=re.split(r'^==\s*([^=\n]+?)\s*==\s*$', raw, flags=re.M)
    out={}; n=start_ch
    for i in range(1,len(segs),2):
        title=segs[i].strip(); body=segs[i+1]
        if title in ('道經','德經'):  # skip part headers if matched
            continue
        jing,seq=parse_jing_zhu(body, stop_on_heading=True)
        out[n]={'title':post(cc.convert(title)),'jing':post(cc.convert(jing)),'seq':seq}; n+=1
    return out, n
hsg={}
d,nxt=parse_hsg(S/'ws_hsg_dao.txt',1); hsg.update(d)
d,_=parse_hsg(S/'ws_hsg_de.txt',nxt); hsg.update(d)

# ---------- ctext ----------
ct=[post(cc.convert(c)) for c in json.load(open(S/'ctext_wangbi.json'))['fulltext']]

# ---------- curated 通行本 anchor (CJK only) ----------
def cjk(s): return ''.join(re.findall(r'[一-鿿]', s))
ctxt=(BUILD.parent/'texts'/'dao-de-jing-selected.md').read_text()
cn_map={'一':1,'二':2,'三':3,'八':8,'十一':11,'十六':16,'二十五':25,'三十七':37,'四十二':42,'六十四':64,'七十八':78,'八十':80,'八十一':81}
blocks=re.split(r'^## 第(.+?)章\s*$', ctxt, flags=re.M); curated={}
for i in range(1,len(blocks),2):
    if blocks[i].strip() in cn_map: curated[cn_map[blocks[i].strip()]]=blocks[i+1].strip()

sub={}
for n in range(1,82):
    sub[str(n)]={
        'wangbi_jing':wb[n]['jing'],
        'wangbi_seq':wb[n]['seq'],
        'hsg_title':hsg[n]['title'],
        'hsg_jing':hsg[n]['jing'],
        'hsg_seq':hsg[n]['seq'],
        'ctext_jing':ct[n-1],
        'wb_ct_agree': cjk(wb[n]['jing'])==cjk(ct[n-1]),
    }
json.dump(sub, open(SUB,'w'), ensure_ascii=False, indent=1)

# ---------- verification report ----------
print("chapters:", len(sub))
print("王弼 注 total:", sum(sum(1 for x in wb[n]['seq'] if x['t']=='zhu') for n in range(1,82)))
print("河上公 注 total:", sum(sum(1 for x in hsg[n]['seq'] if x['t']=='zhu') for n in range(1,82)))
print("河上公 titles ch1-5:", [hsg[n]['title'] for n in range(1,6)])
print("王弼 ch81 jing:", wb[81]['jing'][:80])
agree=sum(1 for n in range(1,82) if sub[str(n)]['wb_ct_agree'])
print(f"王弼≡ctext exact (CJK): {agree}/81")
# curated anchor consistency vs 王弼
print("\ncurated(通行) vs 王弼 mismatches:")
for n in sorted(curated):
    a=cjk(curated[n]); b=cjk(wb[n]['jing'])
    if a!=b:
        for j,(x,y) in enumerate(zip(a,b)):
            if x!=y: print(f"  ch{n}: 通行…{a[max(0,j-4):j+3]} | 王弼…{b[max(0,j-4):j+3]}"); break
        else: print(f"  ch{n}: lengths {len(a)}/{len(b)}")
print("\nsaved substrate.json")
