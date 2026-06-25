# Rules

记录资料使用、改写边界、事实核查和儿童表达规则。

## Hard Rules

- rule: 区分原文、解释、历史事实、传说和虚构故事。
  scope: 全系列
  evidence: 项目需要同时使用经典资料和故事创作。
  consequence_if_broken: 儿童读者会把改编当成事实，影响可信度。

- rule: 每章必须保留《道德经》原文入口。
  scope: 章节篇
  evidence: 用户要求每章开头讲原文。
  consequence_if_broken: 系列会失去逐章经典启蒙的骨架。

- rule: 故事服务于本章核心含义，不用故事淹没原文。
  scope: 章节篇
  evidence: 用户要求生成能够解释文章的故事或内容。
  consequence_if_broken: 章节会变成普通故事集，失去《道德经》对应关系。

- rule: 英文"Original Text"必须使用 James Legge (1891) 译本原文，不得自由改写或混用其他译本。
  scope: 章节篇（英文部分）
  evidence: Legge 是权威公共领域全译本（`reference/texts/dao-de-jing-legge-full.md`），每章可直接引用对应段落，确保来源统一、可核查。
  consequence_if_broken: 不同章英文原文风格不一致，glossary 词条与原文对不上，读者无法跨章对照。

- rule: 英文"Vocabulary Notes"只解释本章 Legge 译文中实际出现的词/短语。
  scope: 章节篇（英文部分）
  evidence: Glossary 是为了帮小读者读懂面前这章英文原文；如果定义的词在原文中根本没出现，就失去了辅助阅读的功能。
  consequence_if_broken: 名词解释与原文脱节，小读者翻回去找不到对应单词，信任感下降。

- rule: 每章完整结构 = 中文全篇（原文 + 释义 + 难词注解 + 正文 + 回扣）+ `---` 分隔 + 英文全篇（Original Text + Interpretation + Vocabulary Notes + Main Text + Return to the Original）。
  scope: 章节篇
  evidence: ch001 已按此结构完成并通过审阅，是已验证的可复现格式。
  consequence_if_broken: 各章格式不统一，编辑排版时需要逐章返工。

## Soft Constraints

- constraint: 儿童解释优先用具体动作、物件和画面。
  usually_true_when: 面向低龄或亲子共读。
  exceptions_allowed_if: 背景篇需要少量知识说明。

- constraint: 全球故事素材优先选结构清楚、价值冲突鲜明、可核查来源的案例。
  usually_true_when: 每章寻找历史典故或现代故事。
  exceptions_allowed_if: 明确标注为寓言式原创改编。

## Pending Rules

- candidate_rule: 每章页数、字数和插图数量。
  needs_confirmation_from: author

- candidate_rule: 是否加入英文、拼音或现代白话旁注。
  needs_confirmation_from: author
