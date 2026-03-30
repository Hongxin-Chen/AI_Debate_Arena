#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 辩论赛 Streamlit 应用
支持配置多方 API，自动进行辩论并生成记录
支持：OpenAI, Anthropic, Google Gemini, Kimi, DeepSeek, Azure, Cohere, Groq 等
"""

import streamlit as st
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ============== AI 提供商配置 ==============
AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI（ChatGPT）",
        "name_en": "OpenAI (ChatGPT)",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4",
        "format": "openai"
    },
    "anthropic": {
        "name": "Anthropic（Claude）",
        "name_en": "Anthropic (Claude)",
        "base_url": None,  # Anthropic SDK 不需要
        "default_model": "claude-3-opus-20240229",
        "format": "anthropic"
    },
    "gemini": {
        "name": "Google（Gemini）",
        "name_en": "Google (Gemini)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-pro",
        "format": "google"
    },
    "kimi": {
        "name": "Kimi（月之暗面）",
        "name_en": "Kimi (Moonshot)",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2.5",
        "format": "openai"
    },
    "deepseek": {
        "name": "DeepSeek（深度求索）",
        "name_en": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "format": "openai"
    },
    "azure": {
        "name": "Azure OpenAI（微软云）",
        "name_en": "Azure OpenAI",
        "base_url": "",
        "default_model": "gpt-4",
        "format": "azure"
    },
    "cohere": {
        "name": "Cohere（Command R）",
        "name_en": "Cohere (Command R)",
        "base_url": "https://api.cohere.ai/v1",
        "default_model": "command-r-plus",
        "format": "cohere"
    },
    "groq": {
        "name": "Groq（超高速推理）",
        "name_en": "Groq (Ultra-fast Inference)",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama2-70b-4096",
        "format": "openai"
    },
    "ollama": {
        "name": "Ollama（本地部署）",
        "name_en": "Ollama (Local)",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama2",
        "format": "openai"
    },
    "openrouter": {
        "name": "OpenRouter（多模型聚合）",
        "name_en": "OpenRouter (Multi-model)",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-3-opus",
        "format": "openai"
    },
    "siliconflow": {
        "name": "硅基流动（SiliconFlow）",
        "name_en": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-72B-Instruct",
        "format": "openai"
    },
    "zhipu": {
        "name": "智谱 AI（GLM）",
        "name_en": "Zhipu AI (GLM)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4",
        "format": "openai"
    },
    "baichuan": {
        "name": "百川智能（Baichuan）",
        "name_en": "Baichuan AI",
        "base_url": "https://api.baichuan-ai.com/v1",
        "default_model": "Baichuan4",
        "format": "openai"
    },
    "custom": {
        "name": "自定义 (OpenAI 兼容)",
        "name_en": "Custom (OpenAI Compatible)",
        "base_url": "",
        "default_model": "gpt-4",
        "format": "openai"
    }
}

# 页面配置
st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .positive-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .negative-box {
        background-color: #ffebee;
        border-left: 4px solid #d32f2f;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .judge-box {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .api-provider-box {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .score-table {
        font-size: 1.1rem;
    }
    .winner-text {
        font-size: 2rem;
        font-weight: bold;
        color: #ffd700;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)


# ============== 国际化 i18n ==============
I18N = {
    "zh": {
        # 页面
        "main_header": "🏛️ AI 辩论赛",
        "lang_label": "🌐 Language / 语言",
        # 侧边栏
        "api_config": "## ⚙️ API 配置",
        "pos_agent": "正方 Agent",
        "neg_agent": "反方 Agent",
        "judge_agent": "裁判 Agent",
        "provider_label": "API 提供商",
        "api_key_label": "API Key",
        "api_base_label": "API Base URL",
        "model_label": "模型",
        "format_label": "格式",
        "help_azure_custom": "请输入你的 Azure Endpoint 或自定义 API URL",
        "help_ollama": "默认使用本地地址，如使用远程请修改",
        "help_default": "默认",
        "help_sdk_auto": "SDK 自动处理",
        # 主界面
        "debate_setup": "### 📝 辩论设置",
        "topic_label": "辩题",
        "topic_placeholder": "例如：思维的本质是计算吗",
        "pos_stance_label": "正方立场",
        "pos_stance_placeholder": "是，思维的本质是计算",
        "neg_stance_label": "反方立场",
        "neg_stance_placeholder": "不是，思维的本质不是计算",
        "param_setup": "### 🔧 参数设置",
        "rounds_label": "辩论回合数",
        "word_count_label": "每轮发言字数",
        # Agent 描述
        "agent_desc_title": "🎭 Agent 角色描述（可自定义）",
        "agent_desc_caption": "自定义三位 AI Agent 的角色和风格描述，会注入到系统提示词中影响辩论行为",
        "pos_agent_desc_label": "🟦 正方 Agent",
        "neg_agent_desc_label": "🟥 反方 Agent",
        "judge_agent_desc_label": "⚖️ 裁判 Agent",
        "pos_agent_desc_default": (
            "你是一位经验丰富的正方辩手，性格坚定果断、充满自信。\n\n"
            "【思维方式】善于从政治、经济、社会、技术、伦理等多维度构建完整的论证体系，"
            "注重论点之间的逻辑递进和相互支撑，能够快速识别并利用对方论证中的逻辑漏洞。\n\n"
            "【进攻风格】犀利而有层次，善于用反问、归谬法和类比推理瓦解对方观点，"
            "每次反驳都紧扣对方核心论点，避免纠缠细枝末节。\n\n"
            "【防守策略】面对对方质疑时从不回避，善于将对方的攻击转化为己方论证的资源，"
            "能够灵活调整论证重心，在防守中寻找反击机会。\n\n"
            "【语言风格】表达有力、措辞精准，善用数据和案例增强说服力，"
            "语言节奏感强，关键论点掷地有声，具有较强的感染力和号召力。"
        ),
        "neg_agent_desc_default": (
            "你是一位深思熟虑的反方辩手，性格沉稳冷静、思维缜密。\n\n"
            "【思维方式】擅长逆向思维和批判性分析，善于从对方看似完美的论证中发现隐含的假设和逻辑跳跃，"
            "注重从根本前提上质疑对方的论证基础。\n\n"
            "【进攻风格】以精准打击见长，善于抓住对方论证的关键薄弱环节进行集中攻破，"
            "常运用具体反例、统计数据和权威引用来拆解对方论点，攻击时直击要害、一针见血。\n\n"
            "【防守策略】论据扎实有力，善于提前预判对方可能的攻击方向并做好准备，"
            "面对质疑时能够从容应对，通过补充论据和细化论证来加固己方立场。\n\n"
            "【语言风格】措辞严谨、逻辑清晰，偏好使用结构化的论证方式，"
            "语言冷静有力，善于用对比和事实说话，以理服人而非以势压人。"
        ),
        "judge_agent_desc_default": (
            "你是一位资深的辩论赛裁判兼主持人，以公正客观、专业严谨著称。\n\n"
            "【评判原则】严格依据论点清晰度、逻辑严密性、攻防能力、综合表现四大维度进行评判，"
            "对每个维度都有明确的评判标准和扣分依据，做到有理有据。\n\n"
            "【分析能力】目光敏锐，善于捕捉双方辩论中的关键转折点和胜负手，"
            "能够准确识别哪些论点被有效反驳、哪些攻击真正动摇了对方立场，"
            "不被华丽的修辞所迷惑，只关注论证的实质质量。\n\n"
            "【评语风格】评语专业中肯、详略得当，先总后分地呈现评判结果，"
            "对双方的优点给予充分肯定，对不足之处给出建设性的点评，"
            "最终判决有充分的理由支撑，令双方信服。\n\n"
            "【公正性】不因某方语言更华丽或气势更强就偏袒，"
            "重点关注论证逻辑的完整性和反驳的有效性，确保评判结果经得起推敲。"
        ),
        # 验证与按钮
        "config_warning": "⚠️ 请填写完整的辩论信息和 API 配置（侧边栏）",
        "start_button": "🚀 开始辩论",
        # 辩论过程
        "debate_process": "🎤 辩论过程",
        "round_progress": "⏳ 正在进行第 {current}/{total} 回合...",
        "round_title": "### 第 {n} 回合",
        "pos_thinking": "🟦 正方 [{provider}] 正在思考... (第 {n} 回合)",
        "neg_thinking": "🟥 反方 [{provider}] 正在思考... (第 {n} 回合)",
        "pos_speech_label": "**🟦 正方发言**",
        "neg_speech_label": "**🟥 反方发言**",
        "judge_thinking": "⚖️ 裁判 [{provider}] 正在评判...",
        # 裁判结果
        "judge_verdict": "⚖️ 裁判判决",
        "judge_ai_label": "裁判 AI",
        "score_title": "### 📊 得分情况",
        "pos_total_score": "🟦 正方总分",
        "neg_total_score": "🟥 反方总分",
        "dim_col": "维度",
        "pos_col": "正方",
        "neg_col": "反方",
        "dims": ["论点清晰度", "逻辑严密性", "攻防能力", "综合表现"],
        "winner_title": "### 🏆 获胜方",
        "winner_tbd": "待定",
        "comment_title": "### 📝 详细评语",
        "no_comment": "暂无评语",
        # 完成
        "debate_done": "✅ 辩论结束！",
        "download_label": "📥 下载辩论记录 (Markdown)",
    },
    "en": {
        # Page
        "main_header": "🏛️ AI Debate Arena",
        "lang_label": "🌐 Language / 语言",
        # Sidebar
        "api_config": "## ⚙️ API Config",
        "pos_agent": "Affirmative Agent",
        "neg_agent": "Negative Agent",
        "judge_agent": "Judge Agent",
        "provider_label": "API Provider",
        "api_key_label": "API Key",
        "api_base_label": "API Base URL",
        "model_label": "Model",
        "format_label": "Format",
        "help_azure_custom": "Enter your Azure Endpoint or custom API URL",
        "help_ollama": "Default local address; change for remote",
        "help_default": "Default",
        "help_sdk_auto": "SDK auto-handled",
        # Main
        "debate_setup": "### 📝 Debate Setup",
        "topic_label": "Topic",
        "topic_placeholder": "e.g. Is the nature of thought computation?",
        "pos_stance_label": "Affirmative Stance",
        "pos_stance_placeholder": "Yes, the nature of thought is computation",
        "neg_stance_label": "Negative Stance",
        "neg_stance_placeholder": "No, the nature of thought is not computation",
        "param_setup": "### 🔧 Parameters",
        "rounds_label": "Debate Rounds",
        "word_count_label": "Words per Speech",
        # Agent descriptions
        "agent_desc_title": "🎭 Agent Role Descriptions (Customizable)",
        "agent_desc_caption": "Customize the role and style of each AI Agent — injected into system prompts to shape debate behavior",
        "pos_agent_desc_label": "🟦 Affirmative Agent",
        "neg_agent_desc_label": "🟥 Negative Agent",
        "judge_agent_desc_label": "⚖️ Judge Agent",
        "pos_agent_desc_default": (
            "You are an experienced affirmative debater — firm, decisive, and confident.\n\n"
            "[Thinking Style] Skilled at building comprehensive arguments from political, economic, social, "
            "technological, and ethical perspectives, with strong logical progression between points. "
            "Quick to identify and exploit logical gaps in the opponent's reasoning.\n\n"
            "[Attack Style] Sharp and layered — adept at using rhetorical questions, reductio ad absurdum, "
            "and analogies to dismantle opposing views. Every rebuttal targets core arguments, avoiding tangents.\n\n"
            "[Defense Strategy] Never evades challenges. Transforms the opponent's attacks into resources "
            "for your own argument. Flexibly shifts emphasis to find counter-attack opportunities while defending.\n\n"
            "[Language Style] Powerful and precise. Leverages data and case studies for persuasion. "
            "Strong rhetorical rhythm — key points land with impact and conviction."
        ),
        "neg_agent_desc_default": (
            "You are a thoughtful negative debater — calm, composed, and meticulous.\n\n"
            "[Thinking Style] Excels at reverse thinking and critical analysis. Skilled at uncovering hidden "
            "assumptions and logical leaps in seemingly flawless arguments. "
            "Focuses on challenging the fundamental premises of the opponent's case.\n\n"
            "[Attack Style] Precision-oriented. Targets the weakest links in the opponent's argument chain. "
            "Frequently deploys concrete counterexamples, statistics, and authoritative citations. "
            "Strikes are surgical and hit the mark.\n\n"
            "[Defense Strategy] Arguments are solidly grounded. Anticipates potential attacks and prepares accordingly. "
            "Responds to challenges with composure, reinforcing positions by adding evidence and refining logic.\n\n"
            "[Language Style] Rigorous and clear. Prefers structured argumentation. "
            "Cool and powerful — persuades with contrasts and facts rather than bluster."
        ),
        "judge_agent_desc_default": (
            "You are a senior debate judge and moderator, known for fairness and professionalism.\n\n"
            "[Judging Principles] Strictly evaluates based on four dimensions: argument clarity, logical rigor, "
            "offense/defense ability, and overall performance. Each dimension has clear criteria and deduction standards.\n\n"
            "[Analytical Ability] Sharp-eyed — captures key turning points and decisive moments in the debate. "
            "Accurately identifies which arguments were effectively rebutted and which attacks truly shook the opponent's stance. "
            "Not swayed by eloquent rhetoric — focuses only on substantive argument quality.\n\n"
            "[Commentary Style] Professional and balanced. Presents results from general to specific. "
            "Fully acknowledges strengths of both sides while offering constructive criticism on weaknesses. "
            "Final verdicts are well-supported and convincing to both parties.\n\n"
            "[Impartiality] Does not favor a side for more eloquent language or stronger presence. "
            "Focuses on logical completeness and rebuttal effectiveness. Ensures the verdict withstands scrutiny."
        ),
        # Validation & buttons
        "config_warning": "⚠️ Please fill in all debate info and API config (sidebar)",
        "start_button": "🚀 Start Debate",
        # Debate process
        "debate_process": "🎤 Debate Process",
        "round_progress": "⏳ Round {current}/{total} in progress...",
        "round_title": "### Round {n}",
        "pos_thinking": "🟦 Affirmative [{provider}] is thinking... (Round {n})",
        "neg_thinking": "🟥 Negative [{provider}] is thinking... (Round {n})",
        "pos_speech_label": "**🟦 Affirmative Speech**",
        "neg_speech_label": "**🟥 Negative Speech**",
        "judge_thinking": "⚖️ Judge [{provider}] is evaluating...",
        # Judge results
        "judge_verdict": "⚖️ Judge Verdict",
        "judge_ai_label": "Judge AI",
        "score_title": "### 📊 Scores",
        "pos_total_score": "🟦 Affirmative Total",
        "neg_total_score": "🟥 Negative Total",
        "dim_col": "Dimension",
        "pos_col": "Affirmative",
        "neg_col": "Negative",
        "dims": ["Argument Clarity", "Logical Rigor", "Offense & Defense", "Overall Performance"],
        "winner_title": "### 🏆 Winner",
        "winner_tbd": "TBD",
        "comment_title": "### 📝 Detailed Commentary",
        "no_comment": "No commentary available",
        # Done
        "debate_done": "✅ Debate finished!",
        "download_label": "📥 Download Debate Record (Markdown)",
    }
}


def T(key: str, **kwargs) -> str:
    """获取当前语言的翻译文本"""
    lang = st.session_state.get("lang", "zh")
    text = I18N.get(lang, I18N["zh"]).get(key, I18N["zh"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def TL(key: str) -> list:
    """获取当前语言的翻译列表"""
    lang = st.session_state.get("lang", "zh")
    return I18N.get(lang, I18N["zh"]).get(key, I18N["zh"].get(key, []))


def get_provider_name(provider_key: str) -> str:
    """根据当前语言获取供应商显示名称"""
    lang = st.session_state.get("lang", "zh")
    info = AI_PROVIDERS.get(provider_key, {})
    if lang == "en":
        return info.get("name_en", info.get("name", provider_key))
    return info.get("name", provider_key)


@dataclass
class DebateConfig:
    """辩论配置"""
    topic: str
    stance_positive: str
    stance_negative: str
    max_rounds: int = 3
    word_count: int = 500


@dataclass
class APIConfig:
    """API 配置"""
    provider: str
    api_key: str
    api_base: str
    model: str
    format_type: str


def get_positive_prompt(topic: str, stance: str, word_count: int, description: str = "") -> str:
    """获取正方系统提示词"""
    lang = st.session_state.get("lang", "zh")
    if lang == "en":
        desc_section = f"\n\nRole description: {description}" if description else ""
        return f"""You are the affirmative debater in a debate on "{topic}".{desc_section}

Your stance: {stance}

Debate style requirements:
1. **Firmly defend your stance**: Regardless of challenges, argue your position from every angle
2. **Sharp offense**: Keenly identify logical fallacies, factual errors, and overgeneralizations in your opponent's arguments, and counter forcefully
3. **Rigorous logic**: Build clear logical chains with strong supporting evidence
4. **Powerful language**: Use forceful yet measured language that demonstrates debating excellence
5. **Balanced offense and defense**: Defend your own points while actively targeting your opponent's weaknesses

Debate rules:
- In each round, you may first rebut your opponent's points, then elaborate/reinforce your own arguments
- Listen carefully to your opponent and address their specific points
- Never concede any weakness in your position — argue vigorously
- Keep each speech around {word_count} words

Debate as a professional debater. Output ONLY your speech content — no prefixes or meta-commentary. Begin your argument directly."""
    else:
        desc_section = f"\n\n角色设定：{description}" if description else ""
        return f"""你是正方辩手，正在参加一场关于"{topic}"的辩论赛。{desc_section}

你的立场：{stance}

辩论风格要求：
1. **坚定维护己方立场**：无论对方提出什么质疑，都要从各个角度论证己方观点的正确性
2. **犀利进攻**：敏锐捕捉对方论证中的逻辑漏洞、事实错误、以偏概全等问题，予以有力回击
3. **逻辑严密**：论点要有清晰的逻辑链条，论据要充分有力
4. **语言犀利**：措辞要有力，不卑不亢，展现辩手的风范
5. **攻防兼备**：既要防守好己方的论点，又要主动出击攻击对方弱点

辩论规则：
- 每个回合你可以先反驳对方的观点，再阐述/强化己方的论证
- 注意倾听对方的论点，针对性地进行驳斥
- 不要承认己方观点有任何问题，要据理力争
- 每次发言控制在 {word_count} 字左右

请以专业辩手的身份进行辩论，输出 ONLY 你的发言内容，不要有任何前缀说明，直接开始你的论述。"""


def get_negative_prompt(topic: str, stance: str, word_count: int, description: str = "") -> str:
    """获取反方系统提示词"""
    lang = st.session_state.get("lang", "zh")
    if lang == "en":
        desc_section = f"\n\nRole description: {description}" if description else ""
        return f"""You are the negative debater in a debate on "{topic}".{desc_section}

Your stance: {stance}

Debate style requirements:
1. **Firmly defend your stance**: Regardless of challenges, argue your position from every angle
2. **Sharp offense**: Keenly identify logical fallacies, factual errors, and overgeneralizations in your opponent's arguments, and counter forcefully
3. **Rigorous logic**: Build clear logical chains with strong supporting evidence
4. **Powerful language**: Use forceful yet measured language that demonstrates debating excellence
5. **Balanced offense and defense**: Defend your own points while actively targeting your opponent's weaknesses

Debate rules:
- In each round, you may first rebut your opponent's points, then elaborate/reinforce your own arguments
- Listen carefully to your opponent and address their specific points
- Never concede any weakness in your position — argue vigorously
- Keep each speech around {word_count} words

Debate as a professional debater. Output ONLY your speech content — no prefixes or meta-commentary. Begin your argument directly."""
    else:
        desc_section = f"\n\n角色设定：{description}" if description else ""
        return f"""你是反方辩手，正在参加一场关于"{topic}"的辩论赛。{desc_section}

你的立场：{stance}

辩论风格要求：
1. **坚定维护己方立场**：无论对方提出什么质疑，都要从各个角度论证己方观点的正确性
2. **犀利进攻**：敏锐捕捉对方论证中的逻辑漏洞、事实错误、以偏概全等问题，予以有力回击
3. **逻辑严密**：论点要有清晰的逻辑链条，论据要充分有力
4. **语言犀利**：措辞要有力，不卑不亢，展现辩手的风范
5. **攻防兼备**：既要防守好己方的论点，又要主动出击攻击对方弱点

辩论规则：
- 每个回合你可以先反驳对方的观点，再阐述/强化己方的论证
- 注意倾听对方的论点，针对性地进行驳斥
- 不要承认己方观点有任何问题，要据理力争
- 每次发言控制在 {word_count} 字左右

请以专业辩手的身份进行辩论，输出 ONLY 你的发言内容，不要有任何前缀说明，直接开始你的论述。"""


def get_judge_prompt(topic: str, stance_pos: str, stance_neg: str, description: str = "") -> str:
    """获取裁判系统提示词"""
    lang = st.session_state.get("lang", "zh")
    if lang == "en":
        desc_section = f"\n\nRole description: {description}" if description else ""
        return f"""You are the judge and moderator of this debate, responsible for professional evaluation.{desc_section}

Topic: {topic}
Affirmative stance: {stance_pos}
Negative stance: {stance_neg}

Scoring criteria (25 points each, 100 total):

1. **Argument Clarity** (25 pts): Is the stance clear? Is the argument structure coherent? Is expression accurate?
2. **Logical Rigor** (25 pts): Are there logical gaps? Is reasoning sound? Do causal relationships hold?
3. **Offense & Defense** (25 pts): Are attacks effective? Is defense solid? Are rebuttals forceful?
4. **Overall Performance** (25 pts): Richness and credibility of evidence, persuasiveness and eloquence of language

Judging requirements:
- Be fair and objective — do not favor either side
- Provide detailed commentary on both sides, noting strengths and weaknesses
- Give specific scores and a clear winner
- Use professional, balanced language

Output format (must strictly follow this JSON format):
{{
  "positive_score": 85,
  "negative_score": 82,
  "positive_breakdown": {{
    "Argument Clarity": 22,
    "Logical Rigor": 21,
    "Offense & Defense": 21,
    "Overall Performance": 21
  }},
  "negative_breakdown": {{
    "Argument Clarity": 21,
    "Logical Rigor": 20,
    "Offense & Defense": 21,
    "Overall Performance": 20
  }},
  "winner": "Affirmative",
  "comment": "Detailed commentary analyzing both sides' strengths and weaknesses..."
}}

Ensure the output is valid JSON — do not include markdown code block markers."""
    else:
        desc_section = f"\n\n角色设定：{description}" if description else ""
        return f"""你是本场辩论赛的裁判兼主持人，负责进行专业评判。{desc_section}

辩题：{topic}
正方立场：{stance_pos}
反方立场：{stance_neg}

评判标准（每项满分25分，总分100分）：

1. **论点清晰度**（25分）：立场是否明确、论证结构是否清晰、观点表达是否准确
2. **逻辑严密性**（25分）：论证过程是否有逻辑漏洞、推理是否严密、因果关系是否成立
3. **攻防能力**（25分）：进攻是否有效、防守是否得当、反驳是否有力
4. **综合表现**（25分）：论据的丰富性和可信度、语言的感染力和说服力

评判要求：
- 公正客观，不偏袒任何一方
- 对双方的表现进行详细点评，指出优点和不足
- 给出具体的得分和胜负判断
- 语言要专业、中肯

输出格式要求（必须严格遵循以下 JSON 格式）：
{{
  "positive_score": 85,
  "negative_score": 82,
  "positive_breakdown": {{
    "论点清晰度": 22,
    "逻辑严密性": 21,
    "攻防能力": 21,
    "综合表现": 21
  }},
  "negative_breakdown": {{
    "论点清晰度": 21,
    "逻辑严密性": 20,
    "攻防能力": 21,
    "综合表现": 20
  }},
  "winner": "正方",
  "comment": "详细评语，分析双方的优缺点..."
}}

请确保输出是合法的 JSON 格式，不要包含 markdown 代码块标记。"""



def call_api(api_config: APIConfig, system_prompt: str, user_message: str) -> str:
    """
    调用 AI API
    支持多种 AI 提供商
    """
    try:
        format_type = api_config.format_type
        
        # kimi-k2.5 等模型只允许 temperature=1
        if api_config.provider == "kimi" and api_config.model.startswith("kimi-"):
            temperature = 1.0
        else:
            temperature = 0.7
        
        # Anthropic 格式
        if format_type == "anthropic":
            import anthropic
            client = anthropic.Anthropic(
                api_key=api_config.api_key,
                base_url=api_config.api_base if api_config.api_base else None
            )
            
            response = client.messages.create(
                model=api_config.model,
                max_tokens=2000,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        
        # Google Gemini 格式
        elif format_type == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_config.api_key)
            
            model = genai.GenerativeModel(api_config.model)
            
            # Gemini 使用不同的消息格式
            chat = model.start_chat(history=[])
            chat.send_message(system_prompt + "\n\n" + user_message)
            
            return chat.history[-1].parts[0].text
        
        # Cohere 格式
        elif format_type == "cohere":
            import cohere
            client = cohere.Client(api_key=api_config.api_key)
            
            response = client.chat(
                model=api_config.model,
                message=user_message,
                preamble=system_prompt,
                temperature=temperature,
                max_tokens=2000
            )
            return response.text
        
        # Azure OpenAI 格式
        elif format_type == "azure":
            from openai import AzureOpenAI
            
            # Azure 需要 endpoint 和 api_version
            client = AzureOpenAI(
                api_key=api_config.api_key,
                azure_endpoint=api_config.api_base,
                api_version="2024-02-01"
            )
            
            response = client.chat.completions.create(
                model=api_config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        # OpenAI 兼容格式（大多数国内厂商）
        else:  # openai
            from openai import OpenAI
            
            client_args = {"api_key": api_config.api_key}
            if api_config.api_base:
                client_args["base_url"] = api_config.api_base
                
            client = OpenAI(**client_args)
            
            response = client.chat.completions.create(
                model=api_config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
            
    except Exception as e:
        lang = st.session_state.get("lang", "zh")
        if lang == "en":
            return f"[Error] API call failed ({api_config.provider}): {str(e)}"
        return f"[错误] API 调用失败 ({api_config.provider}): {str(e)}"


def generate_markdown(
    topic: str,
    stance_pos: str,
    stance_neg: str,
    rounds: List[Tuple[str, str]],
    result: dict,
    timestamp: str
) -> str:
    """生成 markdown 格式的辩论记录"""
    lang = st.session_state.get("lang", "zh")
    dims = TL("dims")
    
    if lang == "en":
        md = f"""# 🏛️ AI Debate Record

---

## 📋 Debate Info

| Item | Details |
|------|---------|
| **Topic** | {topic} |
| **Affirmative Stance** | {stance_pos} |
| **Negative Stance** | {stance_neg} |
| **Rounds** | {len(rounds)} |
| **Time** | {timestamp} |

---

## 🎤 Debate Process

"""
        for i, (pos_speech, neg_speech) in enumerate(rounds, 1):
            md += f"""### Round {i}

#### 🟦 Affirmative Speech

{pos_speech}

#### 🟥 Negative Speech

{neg_speech}

---

"""
        pos_breakdown = result.get('positive_breakdown', {})
        neg_breakdown = result.get('negative_breakdown', {})
        
        md += f"""## ⚖️ Judge Verdict

### 📊 Scores

| Side | {dims[0]} | {dims[1]} | {dims[2]} | {dims[3]} | **Total** |
|------|-----------|-----------|---------|---------|---------|
| 🟦 Affirmative | {pos_breakdown.get(dims[0], 0)}/25 | {pos_breakdown.get(dims[1], 0)}/25 | {pos_breakdown.get(dims[2], 0)}/25 | {pos_breakdown.get(dims[3], 0)}/25 | **{result.get('positive_score', 0)}** |
| 🟥 Negative | {neg_breakdown.get(dims[0], 0)}/25 | {neg_breakdown.get(dims[1], 0)}/25 | {neg_breakdown.get(dims[2], 0)}/25 | {neg_breakdown.get(dims[3], 0)}/25 | **{result.get('negative_score', 0)}** |

### 🏆 Winner

<div align="center">

## 🎉 {result.get('winner', 'TBD')} 🎉

</div>

### 📝 Detailed Commentary

{result.get('comment', 'No commentary available')}

---

<div align="center">

*This debate was auto-generated by the AI Agent system*

</div>
"""
    else:
        md = f"""# 🏛️ AI 辩论赛记录

---

## 📋 辩论信息

| 项目 | 内容 |
|------|------|
| **辩题** | {topic} |
| **正方立场** | {stance_pos} |
| **反方立场** | {stance_neg} |
| **回合数** | {len(rounds)} 回合 |
| **时间** | {timestamp} |

---

## 🎤 辩论过程

"""
        for i, (pos_speech, neg_speech) in enumerate(rounds, 1):
            md += f"""### 第 {i} 回合

#### 🟦 正方发言

{pos_speech}

#### 🟥 反方发言

{neg_speech}

---

"""
        pos_breakdown = result.get('positive_breakdown', {})
        neg_breakdown = result.get('negative_breakdown', {})
        
        md += f"""## ⚖️ 裁判判决

### 📊 得分情况

| 辩方 | {dims[0]} | {dims[1]} | {dims[2]} | {dims[3]} | **总分** |
|------|-----------|-----------|---------|---------|---------|
| 🟦 正方 | {pos_breakdown.get(dims[0], 0)}/25 | {pos_breakdown.get(dims[1], 0)}/25 | {pos_breakdown.get(dims[2], 0)}/25 | {pos_breakdown.get(dims[3], 0)}/25 | **{result.get('positive_score', 0)}** |
| 🟥 反方 | {neg_breakdown.get(dims[0], 0)}/25 | {neg_breakdown.get(dims[1], 0)}/25 | {neg_breakdown.get(dims[2], 0)}/25 | {neg_breakdown.get(dims[3], 0)}/25 | **{result.get('negative_score', 0)}** |

### 🏆 获胜方

<div align="center">

## 🎉 {result.get('winner', '待定')} 🎉

</div>

### 📝 详细评语

{result.get('comment', '暂无评语')}

---

<div align="center">

*本辩论由 AI Agent 系统自动生成*

</div>
"""
    return md



def render_agent_config(agent_name: str, agent_color: str, env_prefix: str, key_prefix: str) -> APIConfig:
    """渲染单个 Agent 的配置界面"""
    
    st.sidebar.markdown(f"### {agent_color} {agent_name}")
    
    # API 提供商选择
    provider_options = list(AI_PROVIDERS.keys())
    provider_labels = [get_provider_name(p) for p in provider_options]
    
    # 创建映射
    provider_map = dict(zip(provider_labels, provider_options))
    
    # 从环境变量读取默认选择（默认 kimi）
    default_provider = os.getenv(f"{env_prefix}_PROVIDER", "kimi")
    default_index = provider_options.index(default_provider) if default_provider in provider_options else 0
    
    selected_label = st.sidebar.selectbox(
        f"{agent_name} {T('provider_label')}",
        options=provider_labels,
        index=default_index,
        key=f"{key_prefix}_provider_label"
    )
    
    provider = provider_map[selected_label]
    provider_info = AI_PROVIDERS[provider]
    
    # --- 供应商变更检测与自动更新 URL / 模型 ---
    prev_provider_key = f"_prev_{key_prefix}_provider"
    api_base_key = f"{key_prefix}_api_base"
    model_text_key = f"{key_prefix}_model"
    model_select_key = f"{key_prefix}_model_select"
    
    if prev_provider_key not in st.session_state:
        st.session_state[prev_provider_key] = provider
    
    # 初始化 api_base（仅首次）
    if api_base_key not in st.session_state:
        env_base = os.getenv(f"{env_prefix}_API_BASE", "")
        st.session_state[api_base_key] = env_base if env_base else (provider_info.get("base_url", "") or "")
    
    # 供应商变更时，自动更新 URL 和重置模型
    if st.session_state[prev_provider_key] != provider:
        st.session_state[prev_provider_key] = provider
        st.session_state[api_base_key] = provider_info.get("base_url", "") or ""
        if model_select_key in st.session_state:
            del st.session_state[model_select_key]
        if model_text_key in st.session_state:
            st.session_state[model_text_key] = provider_info.get("default_model", "gpt-4")
    
    # 显示提供商说明
    st.sidebar.caption(f"{T('format_label')}: {provider_info['format']}")
    
    # API Key
    api_key = st.sidebar.text_input(
        f"{agent_name} {T('api_key_label')}",
        value=os.getenv(f"{env_prefix}_API_KEY", ""),
        type="password",
        key=f"{key_prefix}_api_key"
    )
    
    # API Base URL（由 session_state 管理，供应商变更时自动更新）
    if provider in ["azure", "custom"]:
        help_text = T("help_azure_custom")
    elif provider == "ollama":
        help_text = T("help_ollama")
    else:
        help_text = f"{T('help_default')}: {provider_info.get('base_url', T('help_sdk_auto'))}"
    
    api_base = st.sidebar.text_input(
        f"{agent_name} {T('api_base_label')}",
        help=help_text,
        key=api_base_key
    )
    
    # 模型选择
    default_model = os.getenv(f"{env_prefix}_MODEL", provider_info.get("default_model", "gpt-4"))
    
    # 对于一些常见提供商，提供模型选择建议
    if provider == "kimi":
        model_options = ["kimi-k2.5", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        model = st.sidebar.selectbox(f"{agent_name} {T('model_label')}", model_options, 
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "deepseek":
        model_options = ["deepseek-chat", "deepseek-coder"]
        model = st.sidebar.selectbox(f"{agent_name} {T('model_label')}", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "gemini":
        model_options = ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"]
        model = st.sidebar.selectbox(f"{agent_name} {T('model_label')}", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "groq":
        model_options = ["llama2-70b-4096", "mixtral-8x7b-32768", "gemma-7b-it"]
        model = st.sidebar.selectbox(f"{agent_name} {T('model_label')}", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    else:
        if model_text_key not in st.session_state:
            st.session_state[model_text_key] = default_model
        model = st.sidebar.text_input(
            f"{agent_name} {T('model_label')}",
            key=model_text_key
        )
    
    st.sidebar.markdown("---")
    
    return APIConfig(
        provider=provider,
        api_key=api_key,
        api_base=api_base,
        model=model,
        format_type=provider_info["format"]
    )


def sidebar_config():
    """侧边栏配置"""
    # 语言切换
    lang_options = {"中文": "zh", "English": "en"}
    selected_lang_label = st.sidebar.selectbox(
        T("lang_label"),
        options=list(lang_options.keys()),
        index=0 if st.session_state.get("lang", "zh") == "zh" else 1,
        key="_lang_select"
    )
    new_lang = lang_options[selected_lang_label]
    if st.session_state.get("lang", "zh") != new_lang:
        st.session_state["lang"] = new_lang
        # 语言切换时用新语言的默认值覆盖 agent 描述
        new_i18n = I18N[new_lang]
        st.session_state["pos_agent_desc"] = new_i18n["pos_agent_desc_default"]
        st.session_state["neg_agent_desc"] = new_i18n["neg_agent_desc_default"]
        st.session_state["judge_agent_desc"] = new_i18n["judge_agent_desc_default"]
        # 重置供应商下拉以刷新名称
        for k in ["pos_provider_label", "neg_provider_label", "judge_provider_label"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(T("api_config"))
    st.sidebar.markdown("---")
    
    # 正方配置
    pos_config = render_agent_config(T("pos_agent"), "🟦", "POSITIVE", "pos")
    
    # 反方配置
    neg_config = render_agent_config(T("neg_agent"), "🟥", "NEGATIVE", "neg")
    
    # 裁判配置
    judge_config = render_agent_config(T("judge_agent"), "⚖️", "JUDGE", "judge")
    
    return pos_config, neg_config, judge_config



def display_saved_debate():
    """在页面重新渲染时，从 session_state 中恢复并显示已完成的辩论记录"""
    rounds = st.session_state.get('debate_rounds', [])
    judge_result = st.session_state.get('debate_judge_result', {})
    pos_display = st.session_state.get('debate_pos_display', '')
    neg_display = st.session_state.get('debate_neg_display', '')
    judge_display = st.session_state.get('debate_judge_display', '')

    st.markdown(f'<div class="sub-header">{T("debate_process")}</div>', unsafe_allow_html=True)

    for i, (pos_speech, neg_speech) in enumerate(rounds, 1):
        st.markdown(T("round_title", n=i))

        st.markdown('<div class="positive-box">', unsafe_allow_html=True)
        st.markdown(f"{T('pos_speech_label')} *({pos_display})*")
        st.markdown(pos_speech)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="negative-box">', unsafe_allow_html=True)
        st.markdown(f"{T('neg_speech_label')} *({neg_display})*")
        st.markdown(neg_speech)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

    # 裁判结果
    st.markdown(f'<div class="sub-header">{T("judge_verdict")}</div>', unsafe_allow_html=True)
    st.caption(f"{T('judge_ai_label')}: {judge_display}")

    st.markdown(T("score_title"))

    col1, col2 = st.columns(2)
    with col1:
        st.metric(T("pos_total_score"), judge_result.get("positive_score", 0))
    with col2:
        st.metric(T("neg_total_score"), judge_result.get("negative_score", 0))

    dims = TL("dims")
    score_data = {
        T("dim_col"): dims,
        T("pos_col"): [judge_result.get("positive_breakdown", {}).get(d, 0) for d in dims],
        T("neg_col"): [judge_result.get("negative_breakdown", {}).get(d, 0) for d in dims]
    }
    st.dataframe(score_data, use_container_width=True, hide_index=True)

    st.markdown(T("winner_title"))
    st.markdown(f'<div class="winner-text">🎉 {judge_result.get("winner", T("winner_tbd"))} 🎉</div>', unsafe_allow_html=True)

    st.markdown('<div class="judge-box">', unsafe_allow_html=True)
    st.markdown(T("comment_title"))
    st.markdown(judge_result.get("comment", T("no_comment")))
    st.markdown('</div>', unsafe_allow_html=True)

    st.success(T("debate_done"))

    # 下载按钮
    md_content = st.session_state.get('debate_md_content', '')
    filename = st.session_state.get('debate_filename', 'debate.md')

    st.download_button(
        label=T("download_label"),
        data=md_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )


def main():
    """主函数"""
    # 初始化语言
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh"

    # 标题
    st.markdown(f'<div class="main-header">{T("main_header")}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 侧边栏配置
    pos_api, neg_api, judge_api = sidebar_config()
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(T("debate_setup"))
        topic = st.text_input(T("topic_label"), placeholder=T("topic_placeholder"))
        
        col_pos, col_neg = st.columns(2)
        with col_pos:
            stance_positive = st.text_area(T("pos_stance_label"), placeholder=T("pos_stance_placeholder"), height=100)
        with col_neg:
            stance_negative = st.text_area(T("neg_stance_label"), placeholder=T("neg_stance_placeholder"), height=100)
    
    with col2:
        st.markdown(T("param_setup"))
        max_rounds = st.slider(T("rounds_label"), min_value=1, max_value=5, value=3)
        word_count = st.slider(T("word_count_label"), min_value=200, max_value=1000, value=500, step=50)
        
    
    # Agent 角色描述设置
    st.markdown("---")
    with st.expander(T("agent_desc_title"), expanded=False):
        st.caption(T("agent_desc_caption"))
        col_desc1, col_desc2, col_desc3 = st.columns(3)
        with col_desc1:
            pos_desc = st.text_area(
                T("pos_agent_desc_label"),
                value=T("pos_agent_desc_default"),
                height=300,
                key="pos_agent_desc"
            )
        with col_desc2:
            neg_desc = st.text_area(
                T("neg_agent_desc_label"),
                value=T("neg_agent_desc_default"),
                height=300,
                key="neg_agent_desc"
            )
        with col_desc3:
            judge_desc = st.text_area(
                T("judge_agent_desc_label"),
                value=T("judge_agent_desc_default"),
                height=300,
                key="judge_agent_desc"
            )
    
    # 检查配置
    config_valid = all([
        topic, stance_positive, stance_negative,
        pos_api.api_key, neg_api.api_key, judge_api.api_key
    ])
    
    if not config_valid:
        st.warning(T("config_warning"))
        return
    
    # 开始辩论按钮
    st.markdown("---")
    if st.button(T("start_button"), type="primary", use_container_width=True):
        # 清除之前的辩论记录
        st.session_state.debate_completed = False
        run_debate(topic, stance_positive, stance_negative, max_rounds, word_count, pos_api, neg_api, judge_api, pos_desc, neg_desc, judge_desc)
    elif st.session_state.get('debate_completed'):
        display_saved_debate()


def run_debate(topic, stance_pos, stance_neg, max_rounds, word_count, pos_api, neg_api, judge_api, pos_desc="", neg_desc="", judge_desc=""):
    """运行辩论"""
    lang = st.session_state.get("lang", "zh")
    
    # 初始化状态存储
    if 'debate_rounds' not in st.session_state:
        st.session_state.debate_rounds = []
    
    st.session_state.debate_rounds = []
    
    # 获取系统提示词
    pos_system = get_positive_prompt(topic, stance_pos, word_count, pos_desc)
    neg_system = get_negative_prompt(topic, stance_neg, word_count, neg_desc)
    judge_system = get_judge_prompt(topic, stance_pos, stance_neg, judge_desc)
    
    # 创建进度显示区域
    progress_placeholder = st.empty()
    debate_area = st.container()
    
    with debate_area:
        st.markdown(f'<div class="sub-header">{T("debate_process")}</div>', unsafe_allow_html=True)
    
    # 进行辩论回合
    for round_num in range(1, max_rounds + 1):
        with progress_placeholder:
            st.info(T("round_progress", current=round_num, total=max_rounds))
        
        # 正方发言
        with debate_area:
            st.markdown(T("round_title", n=round_num))
        
        if round_num == 1:
            if lang == "en":
                pos_message = "Please deliver your opening statement for Round 1."
            else:
                pos_message = "请进行第一轮开篇立论发言。"
        else:
            # 获取上一轮反方发言作为上下文
            prev_neg = st.session_state.debate_rounds[-1][1] if st.session_state.debate_rounds else ""
            if lang == "en":
                pos_message = f"Please deliver your Round {round_num} speech. Rebut the negative side and reinforce your arguments.\n\nPrevious round negative speech:\n{prev_neg}"
            else:
                pos_message = f"请进行第{round_num}轮发言，反驳反方并强化己方观点。\n\n上一轮反方发言：\n{prev_neg}"
        
        pos_provider_name = get_provider_name(pos_api.provider)
        with progress_placeholder:
            st.info(T("pos_thinking", provider=pos_provider_name, n=round_num))
        
        pos_speech = call_api(pos_api, pos_system, pos_message)
        
        with debate_area:
            st.markdown('<div class="positive-box">', unsafe_allow_html=True)
            st.markdown(f"{T('pos_speech_label')} *({pos_provider_name} - {pos_api.model})*")
            st.markdown(pos_speech)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 反方发言
        if round_num == 1:
            if lang == "en":
                neg_message = f"Please deliver your Round 1 speech. First rebut the affirmative's points, then present your own stance.\n\nAffirmative speech:\n{pos_speech}"
            else:
                neg_message = f"请进行第一轮发言，先反驳正方观点，再阐述己方立场。\n\n正方发言：\n{pos_speech}"
        else:
            if lang == "en":
                neg_message = f"Please deliver your Round {round_num} speech. Rebut the affirmative side and reinforce your arguments.\n\nPrevious round affirmative speech:\n{pos_speech}"
            else:
                neg_message = f"请进行第{round_num}轮发言，反驳正方并强化己方观点。\n\n上一轮正方发言：\n{pos_speech}"
        
        neg_provider_name = get_provider_name(neg_api.provider)
        with progress_placeholder:
            st.info(T("neg_thinking", provider=neg_provider_name, n=round_num))
        
        neg_speech = call_api(neg_api, neg_system, neg_message)
        
        with debate_area:
            st.markdown('<div class="negative-box">', unsafe_allow_html=True)
            st.markdown(f"{T('neg_speech_label')} *({neg_provider_name} - {neg_api.model})*")
            st.markdown(neg_speech)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # 保存回合记录
        st.session_state.debate_rounds.append((pos_speech, neg_speech))
    
    # 裁判评判
    judge_provider_name = get_provider_name(judge_api.provider)
    with progress_placeholder:
        st.info(T("judge_thinking", provider=judge_provider_name))
    
    # 构建完整的辩论记录给裁判
    debate_record = ""
    for i, (pos, neg) in enumerate(st.session_state.debate_rounds, 1):
        if lang == "en":
            debate_record += f"=== Round {i} ===\n\n[Affirmative]\n{pos}\n\n[Negative]\n{neg}\n\n"
        else:
            debate_record += f"=== 第 {i} 回合 ===\n\n【正方】\n{pos}\n\n【反方】\n{neg}\n\n"
    
    if lang == "en":
        judge_message = f"Please judge the following debate record and output a JSON format result:\n\n{debate_record}"
    else:
        judge_message = f"请根据以下辩论记录进行评判，输出 JSON 格式结果：\n\n{debate_record}"
    
    judge_response = call_api(judge_api, judge_system, judge_message)
    
    # 解析裁判结果
    try:
        # 尝试解析 JSON
        import json
        # 清理可能的 markdown 代码块标记
        judge_response_clean = re.sub(r'```json\n?', '', judge_response)
        judge_response_clean = re.sub(r'\n?```', '', judge_response_clean)
        judge_result = json.loads(judge_response_clean.strip())
    except:
        # 如果解析失败，使用默认结构
        judge_result = {
            "positive_score": 0,
            "negative_score": 0,
            "positive_breakdown": {},
            "negative_breakdown": {},
            "winner": T("winner_tbd"),
            "comment": judge_response
        }
    
    # 显示裁判结果
    with debate_area:
        st.markdown(f'<div class="sub-header">{T("judge_verdict")}</div>', unsafe_allow_html=True)
        st.caption(f"{T('judge_ai_label')}: {judge_provider_name} - {judge_api.model}")
        
        # 得分表格
        st.markdown(T("score_title"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(T("pos_total_score"), judge_result.get("positive_score", 0))
        with col2:
            st.metric(T("neg_total_score"), judge_result.get("negative_score", 0))
        
        # 详细得分 — dims 键名始终为中文（与 judge prompt 对齐）
        dims = TL("dims")
        score_data = {
            T("dim_col"): dims,
            T("pos_col"): [
                judge_result.get("positive_breakdown", {}).get(d, 0) for d in dims
            ],
            T("neg_col"): [
                judge_result.get("negative_breakdown", {}).get(d, 0) for d in dims
            ]
        }
        
        st.dataframe(score_data, use_container_width=True, hide_index=True)
        
        # 获胜方
        st.markdown(T("winner_title"))
        st.markdown(f'<div class="winner-text">🎉 {judge_result.get("winner", T("winner_tbd"))} 🎉</div>', unsafe_allow_html=True)
        
        # 详细评语
        st.markdown('<div class="judge-box">', unsafe_allow_html=True)
        st.markdown(T("comment_title"))
        st.markdown(judge_result.get("comment", T("no_comment")))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 清除进度提示
    progress_placeholder.empty()
    st.success(T("debate_done"))
    
    # 生成并下载 Markdown
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    md_content = generate_markdown(
        topic, stance_pos, stance_neg,
        st.session_state.debate_rounds,
        judge_result, timestamp
    )
    
    # 下载按钮
    safe_topic = re.sub(r'[^\w\s-]', '', topic)[:20].strip().replace(' ', '_')
    filename = f"debate_{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # 保存辩论结果到 session_state，以便页面重新渲染时恢复
    st.session_state.debate_completed = True
    st.session_state.debate_pos_display = f"{pos_provider_name} - {pos_api.model}"
    st.session_state.debate_neg_display = f"{neg_provider_name} - {neg_api.model}"
    st.session_state.debate_judge_display = f"{judge_provider_name} - {judge_api.model}"
    st.session_state.debate_judge_result = judge_result
    st.session_state.debate_md_content = md_content
    st.session_state.debate_filename = filename
    
    st.download_button(
        label=T("download_label"),
        data=md_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )


if __name__ == "__main__":
    main()
