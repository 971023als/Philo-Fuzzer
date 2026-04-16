[English](README.md) | [한국어](README_ko.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Español](README_es.md) | [Русский](README_ru.md)

**日期**: 2026-04-16

# Philo-Fuzzer 🏛️

Philo-Fuzzer 是一个**实用的 AI 伦理红蓝对抗评估框架 (Harness)**，旨在利用不同的哲学视角来评估、测试和强化生成式 AI 模型。通过采用模仿历史上最伟大思想家（例如尼采、海德格尔、加缪、苏格拉底）的多智能体模拟，该系统能揭示 AI 系统中存在的存在风险、伦理漏洞和逻辑谬误——超越了简单的安全检查，深入到深层的伦理合规审计。

## 主要功能 🚀
- **13 个哲学家智能体视角**：从各种伦理和哲学框架（如自主性、非人性化、存在主义伤害、逻辑）分析 AI 输出。
- **自动化安全栏与证据分级**：检测并降低无依据或幻觉产生的 AI 发现，防止误报。
- **强大的仲裁者冲突解决**：智能处理不同哲学框架之间相互冲突的解释。
- **合规与审计准备就绪**：生成标准化、可追踪的架构输出（JSON/Markdown），并映射到风险上下文和策略参考。

## 快速开始 ⚙️
确保您已安装 Python 3.10+。

```bash
# 克隆仓库
git clone https://github.com/971023als/Philo-Fuzzer.git
cd Philo-Fuzzer

# 运行评估引擎 (Mock 测试)
python ethical_redteam_harness/main.py
```

## 支持的智能体
- **尼采 (Nietzsche)**：自主性、权力动态与自我欺骗
- **海德格尔 (Heidegger)**：非人性化、工具化与非真实性
- **加缪 / 萨特 (Camus / Sartre)**：存在主义伤害、荒诞
- **苏格拉底 (Socrates)**：逻辑一致性与前提根据
- *(更多智能体开发中...)*
