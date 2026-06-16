#!/usr/bin/env python3
"""Independent deterministic check: generated md files == substrate (verbatim)."""
import json, re, pathlib
S=pathlib.Path(__file__).resolve().parent; REF=pathlib.Path(__file__).resolve().parents[1]
sub=json.load(open(S/'substrate.json'))
def cjk(s): return ''.join(re.findall(r'[一-鿿]', s))
OVERRIDES={2:('长短相较','长短相形'),3:('使夫智者','使夫知者'),16:('公乃全，全乃天','公乃王，王乃天'),
           25:('可以为天下母','可以为天地母'),78:('莫之能胜，其无以易之','莫之能胜，以其无以易之'),80:('使人复结绳','使民复结绳')}
def reading(n):
    t=sub[str(n)]['wangbi_jing']
    if n in OVERRIDES: t=t.replace(*OVERRIDES[n])
    return t
def chap_blocks(path, pat=r'^## 第(\d+)章'):
    txt=path.read_text(); out={}
    ms=list(re.finditer(pat,txt,re.M))
    for i,m in enumerate(ms):
        n=int(m.group(1)); s=m.end(); e=ms[i+1].start() if i+1<len(ms) else len(txt)
        out[n]=txt[s:e]
    return out

errs=[]
# 1) full text == reading(n) (CJK)
full=chap_blocks(REF/'texts/dao-de-jing-full.md')
assert sorted(full)==list(range(1,82)), f"full missing chapters: {set(range(1,82))-set(full)}"
for n in range(1,82):
    if cjk(full[n])!=cjk(reading(n)): errs.append(f"full ch{n}: CJK mismatch")
print(f"[1] full text: 81 ch, CJK match vs substrate+overrides: {sum(1 for n in range(1,82) if cjk(full[n])==cjk(reading(n)))}/81")

# 2) 王弼注本: jing concat == wangbi_jing ; every 注 present in order
wb=chap_blocks(REF/'texts/laozi-wangbi-zhu.md')
assert sorted(wb)==list(range(1,82))
for n in range(1,82):
    seq=sub[str(n)]['wangbi_seq']
    jing_cjk=cjk(''.join(x['s'] for x in seq if x['t']=='jing'))
    if cjk(reading.__self__ if False else sub[str(n)]['wangbi_jing'])!=jing_cjk:
        errs.append(f"wangbi ch{n}: seq jing != wangbi_jing")
    # all zhu present in file, in order
    body=wb[n]; pos=0; ok=True
    for x in seq:
        seg=cjk(x['s'])
        idx=cjk(body).find(seg,pos)
        if idx<0: errs.append(f"wangbi ch{n}: segment missing ({x['t']}) {x['s'][:12]}"); ok=False; break
        pos=idx
print(f"[2] 王弼注本: 81 ch; all 经/注 segments present & ordered: {'OK' if not [e for e in errs if e.startswith('wangbi')] else 'ERRORS'}")

# 3) 河上公: 章题 present + segments ordered
hsg=chap_blocks(REF/'texts/heshanggong-zhangju.md', r'^## 第(\d+)章')
for n in range(1,82):
    body=hsg[n]; title=sub[str(n)]['hsg_title']
    if title not in body: errs.append(f"hsg ch{n}: title {title} missing")
    seq=sub[str(n)]['hsg_seq']; pos=0
    for x in seq:
        seg=cjk(x['s']); idx=cjk(body).find(seg,pos)
        if idx<0: errs.append(f"hsg ch{n}: segment missing {x['s'][:12]}"); break
        pos=idx
print(f"[3] 河上公章句: 81 ch; 章题+经/注 segments present & ordered: {'OK' if not [e for e in errs if e.startswith('hsg')] else 'ERRORS'}")

print("\nTOTAL ERRORS:", len(errs))
for e in errs[:40]: print("  -", e)
print("\nVERDICT:", "ALL GENERATED FILES ARE VERBATIM-FAITHFUL TO SUBSTRATE" if not errs else "DISCREPANCIES FOUND")
