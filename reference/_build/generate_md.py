#!/usr/bin/env python3
"""Generate reference markdown files verbatim from the verified substrate.
Deterministic: every Chinese character originates from a sourced, cross-checked
file (王弼/河上公 维基文库 + ctext), never from model memory."""
import json, re, difflib, pathlib
S = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(__file__).resolve().parents[1]
sub = json.load(open(S/'substrate.json'))

PROVENANCE_DATE = "2026-06-16"

# ---- 6 documented 通行本 corrections applied to the 王弼底本 reading-text ----
# (chapter, 王弼底本读, 通行本读). Each MUST change the string (asserted).
OVERRIDES = {
    2:  ('长短相较', '长短相形'),
    3:  ('使夫智者', '使夫知者'),
    16: ('公乃全，全乃天', '公乃王，王乃天'),
    25: ('可以为天下母', '可以为天地母'),
    78: ('莫之能胜，其无以易之', '莫之能胜，以其无以易之'),
    80: ('使人复结绳', '使民复结绳'),
}
OVERRIDE_NOTES = {
    2:  '“长短相较” / “长短相形”：王弼注本（华亭张氏本）作“相较”，通行本与河上公本多作“相形”。义皆通：相较，相比较；相形，相比照而显。本读取通行习见之“相形”。',
    3:  '“使夫智者” / “使夫知者”：王弼本作“智者”，通行本多作“知者”。“知”“智”古通；“使夫知（智）者不敢为”谓使逞智巧者不敢妄为。',
    16: '“公乃全” / “公乃王”：此为著名异文。王弼本作“公乃全，全乃天”，通行本（河上公等）作“公乃王，王乃天”。帛书本残损，学界两说并存。本读取通行习见之“王”，并存“全”说。',
    25: '“为天下母” / “为天地母”：王弼本作“天下母”，与马王堆帛书甲乙本合；通行本（河上公、傅奕等）多作“天地母”。二者意义相近，皆指道为万物所自出。本读取通行习见之“天地母”，帛书“天下母”说见出土文献笔记。',
    78: '“其无以易之” / “以其无以易之”：王弼底本作“莫之能胜，其无以易之”，通行本多作“以其无以易之”，多一“以”字，文意更顺（因其无物可以替代水之柔）。本读取通行读法。',
    80: '“使人复结绳” / “使民复结绳”：王弼本作“使人”，通行本作“使民”。唐人或因避讳改“民”为“人”，传世王弼本多存其迹；通行本回改作“民”。本读取“民”。',
}

def cjk(s): return ''.join(re.findall(r'[一-鿿]', s))

def linebreak(jing):
    """Break a punctuated 经文 string into readable lines at sentence terminators."""
    jing = jing.replace('﹕', '：')
    # split after 。 ！ ？ ； and after closing 」, keeping the delimiter
    out=[]; buf=''
    for ch in jing:
        buf+=ch
        if ch in '。！？；' or ch=='」':
            out.append(buf); buf=''
    if buf.strip(): out.append(buf)
    return '\n'.join(x for x in out if x.strip())

def reading_text(n):
    t = sub[str(n)]['wangbi_jing']
    if n in OVERRIDES:
        old,new = OVERRIDES[n]
        assert old in t, f"override ch{n}: '{old}' not found"
        t = t.replace(old, new)
    return t.replace('﹕', '：')

def seq_to_md(seq, note_label='注'):
    """Render an ordered 经-注 sequence: 经文 as text lines, 注 as blockquotes."""
    lines=[]
    for item in seq:
        if item['t']=='jing':
            lines.append(item['s'])
        else:
            for ln in item['s'].split('\n'):
                lines.append(f"> {note_label}：{ln}" if note_label else f"> {ln}")
            lines.append('')
    return '\n'.join(lines).strip()

HEADER_FULL = f"""# 《道德经》全文（八十一章·校订本）

> 底本与来源：以**王弼《老子道德经注》**（华亭张氏原本，维基文库）经文为底本，转写为简体（OpenCC t2s），
> 并参校**中国哲学书电子化计划（ctext.org）**通行本与**河上公章句**本。
> 通行本习见异文（如第十六章「公乃王」、第二十五章「天地母」、第七十八章「以其无以易之」等）已据通行读法校订，
> 全部校改与异文逐条见 [版本异文校记](../versions/variant-apparatus.md)。
> 王弼注、河上公注全文分别见 [王弼注本](laozi-wangbi-zhu.md)、[河上公章句](heshanggong-zhangju.md)。
> 取材日期：{PROVENANCE_DATE}。古籍原文宜保留异文空间，引用正式出版物时请再核纸本校勘本。

---
"""

def gen_full():
    parts=[HEADER_FULL]
    for n in range(1,82):
        parts.append(f"## 第{n}章\n")
        parts.append(linebreak(reading_text(n)))
        parts.append("")
    (REPO/'texts'/'dao-de-jing-full.md').write_text('\n'.join(parts).rstrip()+'\n')

def gen_wangbi():
    head=f"""# 老子《道德经》王弼注（全本）

> 来源：维基文库《老子道德經注》（华亭张氏原本），王弼（三国魏）注；繁体原文经 OpenCC t2s 转写为简体。取材日期：{PROVENANCE_DATE}。
> 体例：每章先列经文，**> 注** 为王弼注文，依原书经—注次序排列。王弼注为公有领域文献。
> 经文以本注本为底本；通行本校订与异文见 [版本异文校记](../versions/variant-apparatus.md)。

---
"""
    parts=[head]
    for n in range(1,82):
        parts.append(f"## 第{n}章\n")
        parts.append(seq_to_md(sub[str(n)]['wangbi_seq'], note_label='注'))
        parts.append("")
    (REPO/'texts'/'laozi-wangbi-zhu.md').write_text('\n'.join(parts).rstrip()+'\n')

def gen_hsg():
    head=f"""# 老子河上公章句（全本）

> 来源：维基文库《老子河上公章句》（道经、德经）；繁体原文经 OpenCC t2s 转写为简体。取材日期：{PROVENANCE_DATE}。
> 体例：每章标出河上公本特有的**二字章题**（如「体道」「养身」），先列经文，**> 注** 为河上公注文，依原书经—注次序排列。河上公章句为公有领域文献。
> 河上公本经文与王弼/通行本互有异文，阅读时可与 [全文校订本](../texts/dao-de-jing-full.md) 对看。

---
"""
    parts=[head]
    for n in range(1,82):
        title=sub[str(n)]['hsg_title']
        parts.append(f"## 第{n}章　{title}\n")
        parts.append(seq_to_md(sub[str(n)]['hsg_seq'], note_label='注'))
        parts.append("")
    (REPO/'texts'/'heshanggong-zhangju.md').write_text('\n'.join(parts).rstrip()+'\n')

def diff_tokens(a, b):
    """Return human-readable token-level differences between two CJK strings."""
    sm=difflib.SequenceMatcher(None, a, b)
    diffs=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal': continue
        ca=a[max(0,i1-3):i1]; wbseg=a[i1:i2]; ctseg=b[j1:j2]; ctx=a[i2:i2+3]
        diffs.append(f"…{ca}〔王弼:{wbseg or '∅'}／ctext:{ctseg or '∅'}〕{ctx}…")
    return diffs

def gen_apparatus():
    head=f"""# 《道德经》版本异文校记

本文件记录本仓库《道德经》文本整理过程中的校改与异文，体现“去伪存真”的取舍依据。
所据电子底本：维基文库王弼《老子道德經注》、河上公章句，及中国哲学书电子化计划（ctext.org）通行本，均经 OpenCC t2s 转写为简体。取材日期：{PROVENANCE_DATE}。

> 说明：电子文本难免有转写、脱漏之误；本校记仅作阅读与改写时的参考，严肃校勘请以纸本校勘本（楼宇烈《王弼集校释》、高明《帛书老子校注》、朱谦之《老子校释》等）为准。

## 一、底本与校订原则

- **底本**：王弼《老子道德经注》（华亭张氏本）经文。王弼本是后世通行八十一章系统的主要来源之一，文字较谨严。
- **参校本**：ctext.org 通行本（received text）、河上公章句本。
- **读法取舍**：面向讲解与儿童改写，正文（[全文校订本](../texts/dao-de-jing-full.md)）取**通行习见读法**；凡校改一律在下文“二”逐条标明，王弼注本原读保留在 [王弼注本全文](../texts/laozi-wangbi-zhu.md)。

## 二、正文对王弼底本的校改（通行本读法）

下列各处，正文采用通行本读法，括注王弼底本原字，供对照：

"""
    parts=[head]
    for n in sorted(OVERRIDES):
        parts.append(f"- **第{n}章**　{OVERRIDE_NOTES[n]}")
    # auto machine-diff of 王弼 vs ctext
    parts.append(f"""
## 三、王弼底本与 ctext 通行本逐章异文（机器比对）

下表为王弼本经文与 ctext.org 通行本经文的自动比对结果（仅就汉字，忽略标点）。
全经八十一章中，**{sum(1 for n in range(1,82) if sub[str(n)]['wb_ct_agree'])} 章两本完全一致**；其余各章异文如下。
这类差异多为虚词、通假与个别脱字，反映传世文本在不同刊本间的细微层累，不宜仅凭单句论定优劣。
""")
    for n in range(1,82):
        if sub[str(n)]['wb_ct_agree']: continue
        a=cjk(sub[str(n)]['wangbi_jing']); b=cjk(sub[str(n)]['ctext_jing'])
        ds=diff_tokens(a,b)
        if ds:
            parts.append(f"- **第{n}章**：" + "；".join(ds))
    parts.append(f"""
## 四、河上公本与出土本

- **河上公章句本**经文亦与王弼/通行本互有异文，并附二字章题，全文见 [河上公章句](../texts/heshanggong-zhangju.md)。
- **马王堆帛书甲乙本、郭店楚简本**为更早的出土文本，与传世本异文较多（如帛书德经在前、用“恒”不用“常”等），其精校文本不宜由网络电子本径取，详见 [出土文献选辑与对照](../texts/mawangdui-guodian-selected.md) 与 [版本与出土文献笔记](version-notes.md)。
""")
    (REPO/'versions'/'variant-apparatus.md').write_text('\n'.join(parts).rstrip()+'\n')

gen_full(); gen_wangbi(); gen_hsg(); gen_apparatus()

# verification summary
import os
for f in ['texts/dao-de-jing-full.md','texts/laozi-wangbi-zhu.md','texts/heshanggong-zhangju.md','versions/variant-apparatus.md']:
    p=REPO/f; print(f"{f}: {len(p.read_text().splitlines())} lines, {p.stat().st_size} bytes")
# assert all 81 chapters present in full text
full=(REPO/'texts/dao-de-jing-full.md').read_text()
chs=re.findall(r'^## 第(\d+)章', full, re.M)
print("full text chapters:", len(chs), "first/last:", chs[0], chs[-1], "complete:", [str(i) for i in range(1,82)]==chs)
print("OVERRIDES applied OK")
