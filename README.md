<div align="center">

# 🏛️ AI Debate Arena

**让 AI 不再「你说得对」—— 用辩论对抗谄媚，从多角度探索真相**

**Stop AI from just agreeing — use debate to counter sycophancy and explore truth from multiple perspectives**

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[中文](#中文) | [English](#english)

<img src="https://img.shields.io/badge/AI%20Providers-14+-orange" alt="providers">

</div>

---

<a id="中文"></a>

## 🇨🇳 中文

### 💡 项目缘起

在与 AI 的日常对话中，你是否有过这样的体验——无论你提出什么观点，AI 总是倾向于表示赞同，甚至帮你「圆」那些本不严谨的论述？这种被称为「AI 谄媚」(Sycophancy) 的现象，让我们越来越难以通过与 AI 的对话来获得真正有价值的思考碰撞。

**AI Debate Arena** 的诞生正是为了打破这一困局。通过让多个 AI Agent 分别扮演持不同立场的辩手，我们迫使 AI 走出「讨好用户」的舒适区：正方必须全力进攻，反方必须据理力争，裁判必须公正裁决。当 AI 不再需要「讨好」任何人，而是被赋予明确的立场与使命时，它们展现出的批判性思维和论证深度往往令人惊喜。

这不仅是一场 AI 之间的辩论赛，更是一种**用对抗消除偏见、用辩证逼近真相**的思维工具。

### ✨ 功能特性

- 🎭 **三 Agent 对抗架构**：正方辩手、反方辩手、裁判各司其职，角色描述完全可自定义
- 🔌 **14+ AI 供应商支持**：OpenAI、Claude、Gemini、Kimi、DeepSeek、Groq 等，支持自定义 API
- ⚔️ **跨模型对战**：让 GPT-4 对阵 Claude，Kimi 对阵 DeepSeek，观察不同模型的思维风格
- 📊 **量化评判**：裁判从论点清晰度、逻辑严密性、攻防能力、综合表现四维度打分
- 📥 **一键导出**：辩论记录自动生成 Markdown 文件，可下载存档
- 🎨 **可视化界面**：Streamlit 驱动的美观交互界面，实时展示辩论进程

### 🚀 快速开始

#### 1. 安装依赖

```bash
cd streamlit_debate_app
pip install -r requirements.txt
```

#### 2. 启动应用

```bash
streamlit run app.py
```

应用将在浏览器中打开（默认 http://localhost:8501）

#### 3. 配置 API

在侧边栏中为正方、反方、裁判三个 Agent 分别配置：
- **API 提供商**：从下拉菜单选择（默认 Kimi）
- **API Key**：填入你的密钥
- **API Base URL**：自动填充，切换供应商时自动更新
- **模型**：根据供应商推荐，可手动修改

#### 4. 开始辩论

填写辩题、正反方立场，点击「🚀 开始辩论」即可观看 AI 的精彩交锋！

### 🤖 支持的 AI 供应商

| 供应商 | 格式 | 推荐模型 |
|--------|------|----------|
| OpenAI（ChatGPT） | OpenAI | gpt-4, gpt-4-turbo |
| Anthropic（Claude） | Anthropic | claude-3-opus, claude-3-sonnet |
| Google（Gemini） | Google | gemini-pro, gemini-1.5-pro |
| Kimi（月之暗面） | OpenAI | kimi-k2.5, moonshot-v1-32k |
| DeepSeek（深度求索） | OpenAI | deepseek-chat, deepseek-coder |
| Azure OpenAI（微软云） | Azure | 你的部署模型 |
| Groq（超高速推理） | OpenAI | llama2-70b, mixtral-8x7b |
| Cohere（Command R） | Cohere | command-r-plus |
| Ollama（本地部署） | OpenAI | llama2, mistral |
| OpenRouter（多模型聚合） | OpenAI | 任意模型 |
| 硅基流动（SiliconFlow） | OpenAI | Qwen2.5-72B-Instruct |
| 智谱 AI（GLM） | OpenAI | glm-4 |
| 百川智能（Baichuan） | OpenAI | Baichuan4 |
| 自定义 API | OpenAI | 任意 OpenAI 兼容 |

### 🎭 辩论流程

```
第 1 回合 ─── 正方：开篇立论
           └─ 反方：立论 + 反驳正方

第 2 回合 ─── 正方：反驳反方 + 强化论证
           └─ 反方：反驳正方 + 强化论证

第 N 回合 ─── 正方：总结陈词 + 最后一击
           └─ 反方：总结陈词 + 最后一击

裁判评判 ──── 四维度打分 → 宣布获胜方 → 详细评语
```

### 🎛️ Agent 角色自定义

每个 Agent 的角色描述均可在界面中自由编辑，涵盖：
- **思维方式** — 构建论证的策略偏好
- **进攻风格** — 反驳对手的方式特点
- **防守策略** — 应对质疑的响应模式
- **语言风格** — 表达和修辞的个性特征

### 💡 玩法建议

| 玩法 | 说明 |
|------|------|
| 🥊 跨模型对战 | GPT-4 vs Claude、Kimi vs DeepSeek，体验不同 AI 的思维差异 |
| 🏠 本地 vs 云端 | Ollama 本地模型对阵云端大模型，看差距有多大 |
| 📚 深度探讨 | 5 回合 + 1000 字，适合哲学、伦理等复杂议题 |
| ⚡ 快速交锋 | 1-2 回合 + 300 字，快速获取多角度观点 |

### ⚠️ 注意事项

- **API 费用**：辩论涉及多次 API 调用，请注意控制成本
- **密钥安全**：请勿将 `.env` 文件提交到代码仓库
- **内容合规**：辩论主题请遵守相关法律法规
- **Kimi 特别说明**：`kimi-k2.5` 模型仅支持 `temperature=1`，应用已自动处理

---

<a id="english"></a>

## 🇬🇧 English

### 💡 Motivation

Have you ever noticed that when discussing ideas with AI, it tends to agree with whatever you say — even reinforcing arguments that aren't quite sound? This phenomenon, known as **AI Sycophancy**, makes it increasingly difficult to have genuinely productive intellectual exchanges with AI.

**AI Debate Arena** was created to break through this limitation. By assigning multiple AI Agents to take opposing stances in a structured debate, we force AI out of its "people-pleasing" comfort zone: the affirmative side must attack relentlessly, the negative side must defend vigorously, and the judge must remain impartial. When AI no longer needs to "please" anyone and is instead given a clear stance and mission, the depth of critical thinking it demonstrates is often remarkable.

This is not just a debate between AIs — it's a **thinking tool that uses adversarial dialogue to eliminate bias and approach truth through dialectics**.

### ✨ Features

- 🎭 **Three-Agent Architecture**: Affirmative debater, negative debater, and judge — each with fully customizable role descriptions
- 🔌 **14+ AI Providers**: OpenAI, Claude, Gemini, Kimi, DeepSeek, Groq, and more, with custom API support
- ⚔️ **Cross-Model Battles**: Pit GPT-4 against Claude, Kimi against DeepSeek — observe different thinking styles
- 📊 **Quantified Judging**: Four-dimensional scoring on argument clarity, logical rigor, offense/defense, and overall performance
- 📥 **One-Click Export**: Auto-generated Markdown debate records, downloadable for archiving
- 🎨 **Visual Interface**: Beautiful interactive UI powered by Streamlit, with real-time debate progress

### 🚀 Quick Start

#### 1. Install Dependencies

```bash
cd streamlit_debate_app
pip install -r requirements.txt
```

#### 2. Launch the App

```bash
streamlit run app.py
```

The app will open in your browser (default: http://localhost:8501)

#### 3. Configure API

In the sidebar, configure each of the three Agents (Affirmative, Negative, Judge):
- **Provider**: Select from the dropdown (default: Kimi)
- **API Key**: Enter your key
- **Base URL**: Auto-filled and updates when switching providers
- **Model**: Recommended per provider, manually adjustable

#### 4. Start Debating

Enter your debate topic and stances, click "🚀 Start Debate", and watch the AI clash!

### 🤖 Supported AI Providers

| Provider | Format | Recommended Models |
|----------|--------|--------------------|
| OpenAI (ChatGPT) | OpenAI | gpt-4, gpt-4-turbo |
| Anthropic (Claude) | Anthropic | claude-3-opus, claude-3-sonnet |
| Google (Gemini) | Google | gemini-pro, gemini-1.5-pro |
| Kimi (Moonshot) | OpenAI | kimi-k2.5, moonshot-v1-32k |
| DeepSeek | OpenAI | deepseek-chat, deepseek-coder |
| Azure OpenAI | Azure | Your deployed model |
| Groq | OpenAI | llama2-70b, mixtral-8x7b |
| Cohere | Cohere | command-r-plus |
| Ollama (Local) | OpenAI | llama2, mistral |
| OpenRouter | OpenAI | Any model |
| SiliconFlow | OpenAI | Qwen2.5-72B-Instruct |
| Zhipu AI (GLM) | OpenAI | glm-4 |
| Baichuan | OpenAI | Baichuan4 |
| Custom API | OpenAI | Any OpenAI-compatible |

### 🎭 Debate Flow

```
Round 1 ──── Affirmative: Opening statement
          └─ Negative: Statement + rebuttal

Round 2 ──── Affirmative: Rebuttal + reinforcement
          └─ Negative: Rebuttal + reinforcement

Round N ──── Affirmative: Closing argument + final strike
          └─ Negative: Closing argument + final strike

Judging ───── Four-dimension scoring → Winner → Detailed commentary
```

### 🎛️ Agent Role Customization

Each Agent's role description is fully editable in the UI, covering:
- **Thinking Style** — Strategic preferences for building arguments
- **Attack Style** — Characteristics of rebutting opponents
- **Defense Strategy** — Response patterns when challenged
- **Language Style** — Expression and rhetorical personality

### 💡 Suggested Play Modes

| Mode | Description |
|------|-------------|
| 🥊 Cross-model | GPT-4 vs Claude, Kimi vs DeepSeek — experience different AI thinking |
| 🏠 Local vs Cloud | Ollama local model vs cloud-based LLMs — see the gap |
| 📚 Deep Dive | 5 rounds + 1000 words — for philosophy, ethics, complex topics |
| ⚡ Quick Clash | 1-2 rounds + 300 words — rapidly gather multi-angle perspectives |

### ⚠️ Notes

- **API Costs**: Debates involve multiple API calls — mind your budget
- **Key Security**: Never commit `.env` files to repositories
- **Content Policy**: Please comply with applicable laws and regulations
- **Kimi Note**: The `kimi-k2.5` model only supports `temperature=1`, handled automatically

---

## 📁 Project Structure

```
streamlit_debate_app/
├── app.py               # Main application
├── requirements.txt     # Dependencies
├── .env.example         # Environment variable template
└── README.md            # This file
```

## 📄 License

MIT

---

<div align="center">

**用对抗消除偏见，用辩证逼近真相**

*Eliminate bias through adversarial dialogue, approach truth through dialectics*

Made with 🤖 and ❤️

</div>
