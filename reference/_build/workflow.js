export const meta = {
  name: 'daodejing-reference-build',
  description: '校验《道德经》原文文件并撰写帛书/郭店选辑、南怀瑾/马保平导读、儿童故事种子',
  phases: [
    { title: '校验原文', detail: '将生成的全文/王弼注/河上公本与权威源逐章比对' },
    { title: '撰写资料', detail: '帛书郭店选辑、南怀瑾与马保平导读、故事种子（含版权与考据复核）' },
    { title: '总审校', detail: '通览 reference/ 目录，查缺、纠错、检查版权与交叉链接' },
  ],
}

const REF = '/Users/vik.qian/study/daodejing/reference'
const SRC = '/tmp/ddj-sources' // raw authoritative sources + substrate.json

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['file', 'chapters_checked', 'findings', 'verdict'],
  properties: {
    file: { type: 'string' },
    chapters_checked: { type: 'number' },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['location', 'issue', 'severity'],
        properties: {
          location: { type: 'string', description: 'e.g. 第16章 / 第3章经文' },
          issue: { type: 'string' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
      },
    },
    verdict: { type: 'string', enum: ['clean', 'minor-issues', 'major-issues'] },
  },
}

const AUTHOR_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['file_written', 'summary', 'sources', 'uncertainties', 'copyright_safe'],
  properties: {
    file_written: { type: 'string' },
    summary: { type: 'string' },
    sources: { type: 'array', items: { type: 'string' } },
    uncertainties: { type: 'array', items: { type: 'string' }, description: '未能核实/低置信之处' },
    copyright_safe: { type: 'boolean' },
  },
}

const CRITIC_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['issues', 'overall'],
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['file', 'problem', 'fix', 'severity'],
        properties: {
          file: { type: 'string' }, problem: { type: 'string' },
          fix: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
      },
    },
    overall: { type: 'string' },
  },
}

// ---------------- Phase 1: verify generated 原文 against raw sources ----------------
phase('校验原文')
const VERIFY_TARGETS = [
  {
    label: 'verify:full',
    file: `${REF}/texts/dao-de-jing-full.md`,
    extra: `这是“校订本全文”。底本为王弼本，但有 6 处依通行本校改（见 ${REF}/versions/variant-apparatus.md 第二节）：第2章相形、第3章知者、第16章「公乃王，王乃天」、第25章「天地母」、第78章「以其无以易之」、第80章「使民复结绳」。这些校改是**有意为之**，不要报为错误。重点检查：(a) 是否 1–81 章齐全、无重复；(b) 每章经文有无脱字、衍字、串行；(c) 简体转写有无残留繁体或乱码。`,
  },
  {
    label: 'verify:wangbi',
    file: `${REF}/texts/laozi-wangbi-zhu.md`,
    extra: `这是王弼注本全文（经文 + 王弼注）。源文件：${SRC}/ws_wangbi.txt（繁体 wikitext）与 ${SRC}/substrate.json 字段 wangbi_seq。重点检查：(a) 81 章齐全；(b) 经文与注是否错位（注是否归属正确的经文段）；(c) 有无注文混入经文或反之；(d) 简繁转写残留。`,
  },
  {
    label: 'verify:heshanggong',
    file: `${REF}/texts/heshanggong-zhangju.md`,
    extra: `这是河上公章句全文（二字章题 + 经文 + 注）。源文件：${SRC}/ws_hsg_dao.txt、${SRC}/ws_hsg_de.txt 与 ${SRC}/substrate.json 字段 hsg_title/hsg_seq。重点检查：(a) 81 章齐全、章题正确（第1章体道、第2章养身、第3章安民……）；(b) 经注错位；(c) 道经37章+德经44章衔接处（第37/38章）有无错乱；(d) 转写残留。`,
  },
]
const verifyResults = await parallel(VERIFY_TARGETS.map(t => () =>
  agent(
    `你是古籍校对专家。校对一个由脚本从权威电子底本自动生成的《道德经》Markdown 文件，找出生成/解析错误。\n\n` +
    `待校文件：${t.file}\n源数据目录：${SRC}（可用 Read 读取其中 substrate.json、ws_*.txt、ctext_wangbi.json）\n\n` +
    `${t.extra}\n\n` +
    `方法：用 Read 通读待校文件；抽样若干章与 ${SRC}/substrate.json 对应字段逐字比对（substrate 已是简体）；对经文完整性可结合你对《道德经》的常识判断有无明显脱衍串行。\n` +
    `不要把“有意的通行本校改”“正常的简体字”“经—注分行体例”当作错误。只报真正的生成/解析/转写错误。\n` +
    `按 schema 返回；findings 为空表示干净。`,
    { label: t.label, phase: '校验原文', schema: VERIFY_SCHEMA }
  )
))

// ---------------- Phase 2: author the research/judgment files ----------------
phase('撰写资料')

const banGu = () => agent(
  `撰写《道德经》出土文献选辑文件，写入：${REF}/texts/mawangdui-guodian-selected.md\n\n` +
  `目标读者：一个“道德经儿童绘本”项目的资料库。本仓库已有传世本全文与王弼/河上公注本；本文件补出土文献维度。\n\n` +
  `内容要求：\n` +
  `1) 开篇说明马王堆帛书甲乙本（约公元前2世纪）、郭店楚简《老子》（约公元前3世纪）的基本背景、与传世本的总体差异（如帛书“德经”在前、用“恒”不用“常”、多虚词“也/矣”等）。\n` +
  `2) 精选若干**确凿可考、你高度确信**的对照条目（建议 8–15 条），每条给出：章次/主题、帛书或郭店读法、传世通行读法、一句话异文说明。优先选最著名、最无争议者（如帛书第一章“道，可道也，非恒道也”一类；第二十五章“天下母”；郭店甲组“绝智弃辩”“绝伪弃诈”与传世“绝圣弃智/绝仁弃义”之别）。残损字用 □。\n` +
  `3) 【极重要·去伪存真】绝不可凭记忆杜撰或“补全”出土文本。凡你不能确证逐字的段落，**只做描述、不照录**，并指明应据纸本精校本（高明《帛书老子校注》、荆门市博物馆《郭店楚墓竹简》、李零《郭店楚简校读记》）核对。把任何低置信处放进返回的 uncertainties。\n` +
  `4) 末尾给出权威整理本书目与说明：网络电子本帛书/郭店质量参差，本文件只作线索，严肃引用须查纸本。\n` +
  `5) 中文、Markdown、简体。开头加来源/日期(2026-06-16)说明与“宜保留异文空间”的提示。与 ../versions/variant-apparatus.md、version-notes.md 交叉链接。\n\n` +
  `可用 Read 参考 ${REF}/versions/version-notes.md 既有笔记，保持术语一致。写完用 Read 自检：确认没有照录任何你无法确证的古文。`,
  { label: 'author:mawangdui-guodian', phase: '撰写资料', schema: AUTHOR_SCHEMA }
)
const verifyBanGu = (r) => agent(
  `你是出土文献校核者，对抗式复核文件 ${REF}/texts/mawangdui-guodian-selected.md。\n` +
  `逐条检查其中每一处帛书/郭店古文引文：是否确属可靠通行学界共识？有无疑似凭记忆杜撰、张冠李戴、或把传世本误标为帛书本？“帛书读 vs 通行读”的对照是否准确？\n` +
  `凡发现可疑或不能确证的古文照录，直接用 Edit 改为“描述性说明 + 指向纸本精校本”，并保留明确的存疑标注。确保版权安全（古籍及学界共识性异文可用；勿大段照搬今人专著文字）。\n` +
  `用 Read/Edit 操作。返回：你做了哪些修改、是否仍有高风险残留（写进 uncertainties）、copyright_safe。file_written 填该路径。`,
  { label: 'verify:mawangdui-guodian', phase: '撰写资料', schema: AUTHOR_SCHEMA }
)

const nanHuaijin = () => agent(
  `撰写《南怀瑾〈老子他说〉导读与阅读笔记》，写入：${REF}/commentaries/nan-huaijin-laozi-tashuo.md\n\n` +
  `背景：本仓库是“道德经儿童绘本”项目资料库。${REF}/README.md 的使用原则明确：现代著作有版权，除少量摘引外，只记录来源线索与自己的读书笔记。请严格遵守。\n\n` +
  `【版权红线】不得复制或大段转录《老子他说》原文。只能：用你自己的话概述其方法、风格、结构；至多极少量（一两句、明确标注）示例性引用以说明风格。本文件是“导读笔记”，不是该书内容的替代。\n\n` +
  `内容要求（中文/简体/Markdown）：\n` +
  `1) 著者与书：南怀瑾（1918–2012）其人、《老子他说》（及续集）的成书背景（讲记整理）、常见版本/出版信息。请用 WebSearch/WebFetch 核实出版信息（先用 ToolSearch 加载 select:WebSearch,WebFetch）。不确定就标注“待核”，勿编造。\n` +
  `2) 解读特色：经史合参、以史证经、贯通儒释道、口语化讲故事的方式；优点与读时应注意之处（其为一家之言、夹叙夹议，不可当唯一定解）。\n` +
  `3) 对本项目的用法：哪些章/主题（道、无为、柔弱、水、反复等）他讲得生动、适合转化为儿童故事；如何与本仓库 ../texts/dao-de-jing-full.md、../themes/core-concepts.md 对照使用。给出“章次 → 可借鉴的讲法方向”的小表（用你的话描述方向，不照录原文）。\n` +
  `4) 合法获取途径（购买/图书馆/正版电子书）。\n` +
  `5) 开头注明编写日期(2026-06-16)与“本文件为读书笔记，非原书内容”。\n\n` +
  `凡无法核实的生平/出版细节放入 uncertainties。copyright_safe 必须为 true（若做不到则说明）。`,
  { label: 'author:nan-huaijin', phase: '撰写资料', schema: AUTHOR_SCHEMA }
)

const maBaoping = () => agent(
  `撰写《马保平〈道德经〉讲解 导读与阅读笔记》，写入：${REF}/commentaries/ma-baoping-daodejing-jiangjie.md\n\n` +
  `背景与版权红线同前：本仓库为“道德经儿童绘本”项目资料库，现代讲解有版权，只做导读笔记与来源线索，不得复制原文，至多极少量标注性引用。\n\n` +
  `【诚实第一】“马保平 道德经讲解”的公开权威资料可能有限。请务必先用 WebSearch/WebFetch 检索核实（先 ToolSearch 加载 select:WebSearch,WebFetch）：确认马保平其人、其《道德经》讲解的形式（视频/音频/书/公众号等）、可获取渠道。**严禁编造**生平、头衔、出版社、章节内容。若检索不到可靠信息，就如实写明“公开资料有限，以下仅据可见资料整理，细节待核”，并把缺口列入 uncertainties——宁可少写、留白，不可虚构。\n\n` +
  `内容要求（中文/简体/Markdown）：\n` +
  `1) 据可核实的资料介绍其人其讲（能查到多少写多少，标明来源链接）。\n` +
  `2) 若能判断其讲解取向（如通俗普及、结合现实生活、侧重修身/治理等），用你的话概述；不确定则不写。\n` +
  `3) 对本项目的潜在用法：可与本仓库 ../texts/dao-de-jing-full.md、../themes/core-concepts.md 如何对照（方向性建议）。\n` +
  `4) 合法获取途径。\n` +
  `5) 开头注明日期(2026-06-16)、“读书笔记非原作内容”、以及“因公开资料有限，本文件信息待进一步核实”。\n\n` +
  `copyright_safe 必为 true。uncertainties 要诚实、详尽。`,
  { label: 'author:ma-baoping', phase: '撰写资料', schema: AUTHOR_SCHEMA }
)

const storySeeds = () => agent(
  `撰写《道德经主题 → 儿童故事种子》文件，写入：${REF}/themes/story-seeds.md（README 计划中的 themes/story-seeds.md）。\n\n` +
  `这是把《道德经》主题转化为儿童绘本情节的“种子库”。先用 Read 通读 ${REF}/themes/core-concepts.md 与 ${REF}/texts/dao-de-jing-full.md，保持主题与章次准确。\n\n` +
  `要求（中文/简体/Markdown）：\n` +
  `1) 选 10–14 个核心主题（道、德、无为、自然、柔弱与水、反与复、知足、不争、慎终如始、上善若水、小国寡民、有无相生、生而不有、致虚守静等）。\n` +
  `2) 每个主题给出：对应章次（须与全文一致）、一句话童趣化的核心意象、2–3 个可发展成绘本一集的故事点子（生活化、适合学龄前到小学低年级、避免说教）、一个可视化画面建议。\n` +
  `3) 强调：故事是“借主题”，不要把某家注解当唯一定解；保留开放与想象空间。\n` +
  `4) 与 ../texts/dao-de-jing-full.md、core-concepts.md 交叉链接。开头注明用途与日期(2026-06-16)。\n\n` +
  `这是原创创作（你写的故事点子），不涉版权；copyright_safe=true。`,
  { label: 'author:story-seeds', phase: '撰写资料', schema: AUTHOR_SCHEMA }
)

const authored = await parallel([
  () => banGu().then(r => (r ? verifyBanGu(r) : r)), // 帛书/郭店：撰写 → 对抗式考据复核
  nanHuaijin,
  maBaoping,
  storySeeds,
])

// ---------------- Phase 3: whole-directory critic ----------------
phase('总审校')
const critic = await agent(
  `你是资料库总审校。通览目录 ${REF}/ 下所有 .md 文件（用 Bash \`find ${REF} -name '*.md'\` 列出后逐一 Read 关键文件）。\n\n` +
  `检查并列出问题（按 schema）：\n` +
  `1) 完整性：81 章原文是否齐全；README 承诺的文件是否都已存在。\n` +
  `2) 交叉链接：文件间的相对链接是否正确、无死链（注意 README 仍可能指向旧的“后续可补”文件名，需要更新）。\n` +
  `3) 版权：commentaries/ 下两份现代著作笔记是否确实只做导读、未照录原文。\n` +
  `4) 一致性/去伪存真：异文校记与全文是否自洽；有无明显错字、乱码、残留繁体。\n` +
  `5) 目录规划建议：README 索引是否需要更新以反映新结构（texts 下新增全文/王弼注/河上公/出土选辑；versions 下新增校记；commentaries 下新增两份导读；themes 下新增故事种子）。\n\n` +
  `不要自己改文件，只返回问题清单与修复建议（fix 要具体到可执行）。overall 给整体评价。`,
  { label: 'critic:whole-dir', phase: '总审校', schema: CRITIC_SCHEMA }
)

return {
  verify: verifyResults.filter(Boolean),
  authored: authored.filter(Boolean),
  critic,
}
