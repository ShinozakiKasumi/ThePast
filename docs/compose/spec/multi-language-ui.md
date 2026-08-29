---
feature: multi-language-ui
status: delivered
updated: 2026-08-09
branch: feat/multi-language-ui (merged to main)
commits: 8b01df2
---

# 多语言支持（繁体中文 + 英文）+ UI 改进

## Report

## [S1] Problem
当前游戏所有 UI 文本为硬编码简体中文，未使用 Ren'Py 翻译系统（`_()`）。
用户要求：
1. 将基础语言从简体中文替换为繁体中文
2. 添加英文翻译
3. 在设置界面提供语言切换
4. 改进 UI 设计（导航/偏好/确认框/存档/跳过指示等）

## [S2] Design

### 字体（design_tokens.rpy + tools/setup_fonts.py）
- 从系统 TTC 提取 NotoSansMonoCJKtc-Regular.otf / Bold.otf 到 game/fonts/
- design_tokens.rpy 新增 `FONT_CJK_TC` / `FONT_CJK_TC_BOLD` 路径令牌
- FontGroup 改用 TC 字体覆盖 CJK 范围（字形差异：過/门/來/東 等）
- 保留 SC 字体文件不删（不引用，不影响）

### 翻译系统（Ren'Py 内建）
- 基础语言 = 繁体中文（`config.language = None`，源码字符串即 TC）
- 英文翻译目录 `game/tl/english/`
- 所有用户可见字符串包裹 `_()`
- `translate strings` 块翻译 UI 字符串
- `translate` 块翻译对话

### 源码字符串 SC→TC 转换
- screens.rpy：所有菜单/标签/按钮文本 SC→TC + `_()`
- options.rpy：layout.* 字符串 SC→TC + `_()`
- script.rpy：占位对话 SC→TC（Ren'Py 自动包裹对话）
- 注释不转换（开发者可见，非用户可见）

### 英文翻译文件（game/tl/english/）
- `common.rpy`：`translate strings` 块，覆盖所有 `_()` 包裹的 UI 字符串
- `script.rpy`：`translate english start:` 块，翻译占位对话

### 语言切换（preferences 屏）
- 新增 "語言 / LANGUAGE" 分区
- 按钮："繁體中文"（`Language(None)`）+ "English"（`Language("english")`）
- 切换后即时生效（Ren'Py 内建 `Language` action 自动重载界面）

### UI 改进
1. **偏好设置（preferences）**：新增 SKIP 分区（Unseen Text / After Choices 开关）
2. **确认框（confirm）**：按钮改为 YES / NO，包裹 `_()`
3. **存档/读档（file_slots）**：新增 AUTO / QUICK 存档页按钮，包裹 `_()`
4. **跳过指示（skip_indicator）**：新增 "SKIPPING..." 屏，带动画三角形
5. **快捷菜单（quick_menu）**：已有英文标签，仅包裹 `_()`
6. **导航（navigation）**：保持现有结构，标签 SC→TC + `_()`

### 不改动
- 标题屏布局/动画（仅字符串 SC→TC + `_()`）
- say 屏布局/组件（仅字符串 SC→TC + `_()`）
- choice 屏布局（仅字符串 SC→TC + `_()`）
- fx 系统 / 粒子层 / 微氛围
- 调色板 / 设计令牌数值
- DESIGN.md / README.md（仅更新语言相关说明）

## [S3] Out of Scope
- 简体中文保留（用户明确要求替换为繁体）
- 真实剧情对话翻译（当前为占位台词，仅翻译占位文本）
- About/Credits 屏（无内容，不添加）
- Gallery 屏（无内容，不添加）
- Help/Controls 屏（不添加，保持最小改动）
- 注释/文档 SC→TC 转换（开发者可见）
- 音效接入（本项目暂无音频资产）

## Tasks
- [ ] T1: 提取 TC 字体 + 更新 setup_fonts.py + design_tokens.rpy 字体令牌 — acceptance: NotoSansMonoCJKtc OTF 存在于 game/fonts/，FontGroup 使用 TC 字体 (covers: S2)
- [ ] T2: screens.rpy 所有 UI 字符串 SC→TC + `_()` 包裹 — acceptance: 菜单/标签/按钮文本为 TC 且包裹 `_()`，lint 通过 (covers: S2)
- [ ] T3: options.rpy layout.* 字符串 SC→TC + `_()` 包裹 — acceptance: 确认框提示为 TC 且包裹 `_()` (covers: S2)
- [ ] T4: script.rpy 占位对话 SC→TC — acceptance: 旁白/角色台词/选择项为 TC (covers: S2)
- [ ] T5: 创建英文翻译文件 game/tl/english/ — acceptance: common.rpy 含所有 UI 字符串英文翻译，script.rpy 含对话翻译 (depends: T2,T3,T4; covers: S2)
- [ ] T6: preferences 屏新增语言切换 + SKIP 分区 — acceptance: 語言/LANGUAGE 分区有繁體中文/English 按钮，SKIP 分区有 Unseen Text/After Choices 开关 (depends: T2; covers: S2)
- [ ] T7: confirm 屏改 YES/NO + file_slots 加 AUTO/QUICK 页 + skip_indicator 屏 — acceptance: 确认框 YES/NO 按钮，存档页有 AUTO/QUICK 按钮，跳过时显示 SKIPPING... (depends: T2; covers: S2)
- [ ] T8: lint 验证 + README 更新 — acceptance: renpy.sh lint 通过，README 含多语言说明 (depends: T1-T7; covers: S2)
