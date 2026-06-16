# 原文构建管线（可复现 · 去伪存真）

本目录保存 `reference/texts/` 与 `reference/versions/variant-apparatus.md` 的**生成脚本与原始电子底本快照**，使全文整理过程可审计、可复现。原文的每一个汉字都来自下列具名底本，经确定性脚本生成，不依赖记忆录入。

## 来源快照（`sources/`，取材日期 2026-06-16）

| 文件 | 来源 | 用途 |
|---|---|---|
| `ws_wangbi.txt` | 维基文库《老子道德經注》（王弼注本，华亭张氏原本），`?action=raw` | 全文底本 + 王弼注 |
| `ws_hsg_dao.txt` / `ws_hsg_de.txt` | 维基文库《老子河上公章句》道经 / 德经，`?action=raw` | 河上公章题 + 经 + 注 |
| `ctext_wangbi.json` | ctext.org API `gettext?urn=ctp:dao-de-jing` | 通行本经文（交叉参校） |

## 脚本

- `build_substrate.py` — 解析三种底本，繁→简（OpenCC `t2s`）并规范少数生僻字形/标点，逐章对齐，产出 `substrate.json`（已含校验报告：81 章、王弼注 405 段、河上公注 931 段、王弼≡ctext 49/81）。
- `generate_md.py` — 由 `substrate.json` 确定性生成 4 个文件：`dao-de-jing-full.md`（含 6 处通行本校改）、`laozi-wangbi-zhu.md`、`heshanggong-zhangju.md`、`variant-apparatus.md`。
- `verify_generated.py` — 独立复核：生成文件是否与 `substrate.json` 逐字一致、经注是否齐全有序（应输出 0 errors）。
- `workflow.js` — 撰写 `mawangdui-guodian-selected.md`、两份现代著作导读、`story-seeds.md` 的多 agent 编排脚本（含对抗式考据/版权复核），仅作记录。

## 复现步骤

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install opencc            # 真正的 C 版 OpenCC（1.3.x）
cd reference/_build
python build_substrate.py     # 生成 substrate.json
python generate_md.py         # 生成 reference/texts/*、versions/variant-apparatus.md
python verify_generated.py    # 复核：应为 0 errors
```

## 校订原则

- **底本**：王弼《老子道德经注》（华亭张氏本）。其转写较 ctext 电子本严谨（ctext 第 3 章有脱误）。
- **6 处通行本校改**：第 2、3、16、25、78、80 章采用通行习见读法，逐条见 [版本异文校记](../versions/variant-apparatus.md)。
- **生僻字形规范**：OpenCC `t2s` 对个别字产出罕见字形（繟→𦈎、綿→緜 等），脚本将其规范为可读形（繟、绵、稽、妖），并清除维基语言转换标记 `-{…}-`。
- 严肃引用仍以纸本校勘本为准（楼宇烈《王弼集校释》、高明《帛书老子校注》等），见 [bibliography.md](../bibliography.md)。
