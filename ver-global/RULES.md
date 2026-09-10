# Rules

记录全球版资料使用、翻译边界、改写边界和跨文化表达规则。

## Hard Rules

- rule: 每章必须保留中文原文入口。
  scope: 章节篇
  evidence: 项目以《道德经》八十一章为骨架，不能只剩主题散文。
  consequence_if_broken: 全球版会失去经典文本的可核查根基。

- rule: 一章多篇时，第一篇必须完整呈现本章原文与整体义理。
  scope: 章节篇
  evidence: 后续篇可能专注典故、故事或升华；若第一篇不立稳原文入口，整章会散。
  consequence_if_broken: 读者和绘本生成 agent 会不知道本章核心章义。

- rule: 章节文件只放正文页稿。
  scope: 章节篇
  evidence: 用户要求 metadata 和其它说明放到其它文件，不干扰原文。
  consequence_if_broken: 绘本生成 agent 复制章节时会混入说明、提示词和研究备注。

- rule: 区分“译文”“脚本文字”和“解释性改写”。
  scope: 全系列
  evidence: Legge 译文可作为公共领域英译入口，但全球版脚本需要现代英语表达。
  consequence_if_broken: 读者会误以为原创英文是严谨逐字翻译。

- rule: 不把单一注本解释为唯一正解。
  scope: 义理解释
  evidence: 《道德经》有王弼、河上公、简帛、现代学者等多重解释传统。
  consequence_if_broken: 文本会显得武断，且削弱经典的开放性。

- rule: 跨文化类比必须标明功能。
  scope: research / chapters
  evidence: 全球版需要桥梁，但不能用外来概念替换老子思想。
  consequence_if_broken: 容易把《道德经》误读成“东方版某某西方概念”。

- rule: 虚构叙事必须以 `fiction` 或“原创框架”标识。
  scope: chapters / research
  evidence: 绘本脚本会使用寓言、角色和场景。
  consequence_if_broken: 读者或后续作者可能把原创故事当作历史典故。

- rule: 避免东方主义、神秘化和装饰性中国风。
  scope: 文字与视觉
  evidence: 全球版面向国际读者，尤其需要避免把中国古典思想变成异国情调背景。
  consequence_if_broken: 作品会变浅，并损害文化表达的可信度。

- rule: 场景动作必须形成因果或递进动作链，场景转换必须由人物、物件或环境变化承接。
  scope: 章节正文与画面描述
  evidence: 用户于 2026-09-09 明确要求动作 A 自然引发动作 B，并禁止只靠时间词切换场景。
  consequence_if_broken: 叙事会呈现分镜清单感，人物心理与画面缺乏连续性。

- rule: 作者叙述避免先否定后肯定的对偶句式，否定词不得替代正面描写。
  scope: 中英文正文
  evidence: 用户明确禁用“不是……而是……”“没有……只有……”“不像……更像……”等结构；人物对话中的自然否定可保留。
  consequence_if_broken: 文风会回到模板化论证，削弱朗读节奏和画面实感。

- rule: 修饰语必须精准、节制，一个名词通常只带一个关键修饰成分。
  scope: 中英文正文
  evidence: 用户要求删除可有可无的形容词，并禁止连续形容词与短词堆叠。
  consequence_if_broken: 信息被装饰淹没，文本产生明显生成式写作痕迹。

## Soft Constraints

- constraint: 章节正文尽量短，解释留给创作者笔记或附注。
  usually_true_when: 做成人绘本/艺术书页稿。
  exceptions_allowed_if: 背景篇或导读页需要稍完整说明。

- constraint: 英文正文使用 `Dao`，保留 Legge 原文时照录 `Tao`。
  usually_true_when: 现代全球脚本。
  exceptions_allowed_if: 讨论历史译名或引用 Legge 时。

- constraint: 每章最好有一个核心图像装置。
  usually_true_when: 逐章绘本脚本。
  exceptions_allowed_if: 某章更适合连续叙事或多图像并置。

## Pending Rules

- candidate_rule: 是否每章都附一段 `Reader's Note`。
  needs_confirmation_from: author / editor

- candidate_rule: 是否保留中英双语全文并列。
  needs_confirmation_from: author

- candidate_rule: 是否固定 16 页作为标准章长。
  needs_confirmation_from: art director / production
