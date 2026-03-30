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
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4",
        "format": "openai"
    },
    "anthropic": {
        "name": "Anthropic（Claude）",
        "base_url": None,  # Anthropic SDK 不需要
        "default_model": "claude-3-opus-20240229",
        "format": "anthropic"
    },
    "gemini": {
        "name": "Google（Gemini）",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-pro",
        "format": "google"
    },
    "kimi": {
        "name": "Kimi（月之暗面）",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2.5",
        "format": "openai"
    },
    "deepseek": {
        "name": "DeepSeek（深度求索）",
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "format": "openai"
    },
    "azure": {
        "name": "Azure OpenAI（微软云）",
        "base_url": "",  # 需要用户填写
        "default_model": "gpt-4",
        "format": "azure"
    },
    "cohere": {
        "name": "Cohere（Command R）",
        "base_url": "https://api.cohere.ai/v1",
        "default_model": "command-r-plus",
        "format": "cohere"
    },
    "groq": {
        "name": "Groq（超高速推理）",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama2-70b-4096",
        "format": "openai"
    },
    "ollama": {
        "name": "Ollama（本地部署）",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama2",
        "format": "openai"
    },
    "openrouter": {
        "name": "OpenRouter（多模型聚合）",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-3-opus",
        "format": "openai"
    },
    "siliconflow": {
        "name": "硅基流动（SiliconFlow）",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-72B-Instruct",
        "format": "openai"
    },
    "zhipu": {
        "name": "智谱 AI（GLM）",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4",
        "format": "openai"
    },
    "baichuan": {
        "name": "百川智能（Baichuan）",
        "base_url": "https://api.baichuan-ai.com/v1",
        "default_model": "Baichuan4",
        "format": "openai"
    },
    "custom": {
        "name": "自定义 (OpenAI 兼容)",
        "base_url": "",
        "default_model": "gpt-4",
        "format": "openai"
    }
}

# 页面配置
st.set_page_config(
    page_title="AI 辩论赛",
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

| 辩方 | 论点清晰度 | 逻辑严密性 | 攻防能力 | 综合表现 | **总分** |
|------|-----------|-----------|---------|---------|---------|
| 🟦 正方 | {pos_breakdown.get('论点清晰度', 0)}/25 | {pos_breakdown.get('逻辑严密性', 0)}/25 | {pos_breakdown.get('攻防能力', 0)}/25 | {pos_breakdown.get('综合表现', 0)}/25 | **{result.get('positive_score', 0)}** |
| 🟥 反方 | {neg_breakdown.get('论点清晰度', 0)}/25 | {neg_breakdown.get('逻辑严密性', 0)}/25 | {neg_breakdown.get('攻防能力', 0)}/25 | {neg_breakdown.get('综合表现', 0)}/25 | **{result.get('negative_score', 0)}** |

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
    provider_labels = [AI_PROVIDERS[p]["name"] for p in provider_options]
    
    # 创建映射
    provider_map = dict(zip(provider_labels, provider_options))
    
    # 从环境变量读取默认选择（默认 kimi）
    default_provider = os.getenv(f"{env_prefix}_PROVIDER", "kimi")
    default_index = provider_options.index(default_provider) if default_provider in provider_options else 0
    
    selected_label = st.sidebar.selectbox(
        f"{agent_name} API 提供商",
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
    st.sidebar.caption(f"格式: {provider_info['format']}")
    
    # API Key
    api_key = st.sidebar.text_input(
        f"{agent_name} API Key",
        value=os.getenv(f"{env_prefix}_API_KEY", ""),
        type="password",
        key=f"{key_prefix}_api_key"
    )
    
    # API Base URL（由 session_state 管理，供应商变更时自动更新）
    if provider in ["azure", "custom"]:
        help_text = "请输入你的 Azure Endpoint 或自定义 API URL"
    elif provider == "ollama":
        help_text = "默认使用本地地址，如使用远程请修改"
    else:
        help_text = f"默认: {provider_info.get('base_url', 'SDK 自动处理')}"
    
    api_base = st.sidebar.text_input(
        f"{agent_name} API Base URL",
        help=help_text,
        key=api_base_key
    )
    
    # 模型选择
    default_model = os.getenv(f"{env_prefix}_MODEL", provider_info.get("default_model", "gpt-4"))
    
    # 对于一些常见提供商，提供模型选择建议
    if provider == "kimi":
        model_options = ["kimi-k2.5", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        model = st.sidebar.selectbox(f"{agent_name} 模型", model_options, 
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "deepseek":
        model_options = ["deepseek-chat", "deepseek-coder"]
        model = st.sidebar.selectbox(f"{agent_name} 模型", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "gemini":
        model_options = ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"]
        model = st.sidebar.selectbox(f"{agent_name} 模型", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    elif provider == "groq":
        model_options = ["llama2-70b-4096", "mixtral-8x7b-32768", "gemma-7b-it"]
        model = st.sidebar.selectbox(f"{agent_name} 模型", model_options,
                                     index=model_options.index(default_model) if default_model in model_options else 0,
                                     key=model_select_key)
    else:
        if model_text_key not in st.session_state:
            st.session_state[model_text_key] = default_model
        model = st.sidebar.text_input(
            f"{agent_name} 模型",
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
    st.sidebar.markdown("## ⚙️ API 配置")
    st.sidebar.markdown("---")
    
    # 正方配置
    pos_config = render_agent_config("正方 Agent", "🟦", "POSITIVE", "pos")
    
    # 反方配置
    neg_config = render_agent_config("反方 Agent", "🟥", "NEGATIVE", "neg")
    
    # 裁判配置
    judge_config = render_agent_config("裁判 Agent", "⚖️", "JUDGE", "judge")
    
    return pos_config, neg_config, judge_config



def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-header">🏛️ AI 辩论赛</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 侧边栏配置
    pos_api, neg_api, judge_api = sidebar_config()
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 辩论设置")
        topic = st.text_input("辩题", placeholder="例如：人工智能是否会取代人类工作")
        
        col_pos, col_neg = st.columns(2)
        with col_pos:
            stance_positive = st.text_area("正方立场", placeholder="正方支持的观点", height=100)
        with col_neg:
            stance_negative = st.text_area("反方立场", placeholder="反方反对的观点", height=100)
    
    with col2:
        st.markdown("### 🔧 参数设置")
        max_rounds = st.slider("辩论回合数", min_value=1, max_value=5, value=3)
        word_count = st.slider("每轮发言字数", min_value=200, max_value=1000, value=500, step=50)
        
    
    # Agent 角色描述设置
    st.markdown("---")
    with st.expander("🎭 Agent 角色描述（可自定义）", expanded=False):
        st.caption("自定义三位 AI Agent 的角色和风格描述，会注入到系统提示词中影响辩论行为")
        col_desc1, col_desc2, col_desc3 = st.columns(3)
        with col_desc1:
            pos_desc = st.text_area(
                "🟦 正方 Agent",
                value="你是一位经验丰富的正方辩手，性格坚定果断、充满自信。\n\n"
                      "【思维方式】善于从政治、经济、社会、技术、伦理等多维度构建完整的论证体系，"
                      "注重论点之间的逻辑递进和相互支撑，能够快速识别并利用对方论证中的逻辑漏洞。\n\n"
                      "【进攻风格】犀利而有层次，善于用反问、归谬法和类比推理瓦解对方观点，"
                      "每次反驳都紧扣对方核心论点，避免纠缠细枝末节。\n\n"
                      "【防守策略】面对对方质疑时从不回避，善于将对方的攻击转化为己方论证的资源，"
                      "能够灵活调整论证重心，在防守中寻找反击机会。\n\n"
                      "【语言风格】表达有力、措辞精准，善用数据和案例增强说服力，"
                      "语言节奏感强，关键论点掷地有声，具有较强的感染力和号召力。",
                height=300,
                key="pos_agent_desc"
            )
        with col_desc2:
            neg_desc = st.text_area(
                "🟥 反方 Agent",
                value="你是一位深思熟虑的反方辩手，性格沉稳冷静、思维缜密。\n\n"
                      "【思维方式】擅长逆向思维和批判性分析，善于从对方看似完美的论证中发现隐含的假设和逻辑跳跃，"
                      "注重从根本前提上质疑对方的论证基础。\n\n"
                      "【进攻风格】以精准打击见长，善于抓住对方论证的关键薄弱环节进行集中攻破，"
                      "常运用具体反例、统计数据和权威引用来拆解对方论点，攻击时直击要害、一针见血。\n\n"
                      "【防守策略】论据扎实有力，善于提前预判对方可能的攻击方向并做好准备，"
                      "面对质疑时能够从容应对，通过补充论据和细化论证来加固己方立场。\n\n"
                      "【语言风格】措辞严谨、逻辑清晰，偏好使用结构化的论证方式，"
                      "语言冷静有力，善于用对比和事实说话，以理服人而非以势压人。",
                height=300,
                key="neg_agent_desc"
            )
        with col_desc3:
            judge_desc = st.text_area(
                "⚖️ 裁判 Agent",
                value="你是一位资深的辩论赛裁判兼主持人，以公正客观、专业严谨著称。\n\n"
                      "【评判原则】严格依据论点清晰度、逻辑严密性、攻防能力、综合表现四大维度进行评判，"
                      "对每个维度都有明确的评判标准和扣分依据，做到有理有据。\n\n"
                      "【分析能力】目光敏锐，善于捕捉双方辩论中的关键转折点和胜负手，"
                      "能够准确识别哪些论点被有效反驳、哪些攻击真正动摇了对方立场，"
                      "不被华丽的修辞所迷惑，只关注论证的实质质量。\n\n"
                      "【评语风格】评语专业中肯、详略得当，先总后分地呈现评判结果，"
                      "对双方的优点给予充分肯定，对不足之处给出建设性的点评，"
                      "最终判决有充分的理由支撑，令双方信服。\n\n"
                      "【公正性】不因某方语言更华丽或气势更强就偏袒，"
                      "重点关注论证逻辑的完整性和反驳的有效性，确保评判结果经得起推敲。",
                height=300,
                key="judge_agent_desc"
            )
    
    # 检查配置
    config_valid = all([
        topic, stance_positive, stance_negative,
        pos_api.api_key, neg_api.api_key, judge_api.api_key
    ])
    
    if not config_valid:
        st.warning("⚠️ 请填写完整的辩论信息和 API 配置（侧边栏）")
        return
    
    # 开始辩论按钮
    st.markdown("---")
    if st.button("🚀 开始辩论", type="primary", use_container_width=True):
        run_debate(topic, stance_positive, stance_negative, max_rounds, word_count, pos_api, neg_api, judge_api, pos_desc, neg_desc, judge_desc)


def run_debate(topic, stance_pos, stance_neg, max_rounds, word_count, pos_api, neg_api, judge_api, pos_desc="", neg_desc="", judge_desc=""):
    """运行辩论"""
    
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
        st.markdown('<div class="sub-header">🎤 辩论过程</div>', unsafe_allow_html=True)
    
    # 进行辩论回合
    for round_num in range(1, max_rounds + 1):
        with progress_placeholder:
            st.info(f"⏳ 正在进行第 {round_num}/{max_rounds} 回合...")
        
        # 正方发言
        with debate_area:
            st.markdown(f"### 第 {round_num} 回合")
        
        if round_num == 1:
            pos_message = "请进行第一轮开篇立论发言。"
        else:
            # 获取上一轮反方发言作为上下文
            prev_neg = st.session_state.debate_rounds[-1][1] if st.session_state.debate_rounds else ""
            pos_message = f"请进行第{round_num}轮发言，反驳反方并强化己方观点。\n\n上一轮反方发言：\n{prev_neg}"
        
        with progress_placeholder:
            st.info(f"🟦 正方 [{AI_PROVIDERS.get(pos_api.provider, {}).get('name', pos_api.provider)}] 正在思考... (第 {round_num} 回合)")
        
        pos_speech = call_api(pos_api, pos_system, pos_message)
        
        with debate_area:
            st.markdown('<div class="positive-box">', unsafe_allow_html=True)
            st.markdown(f"**🟦 正方发言** *({AI_PROVIDERS.get(pos_api.provider, {}).get('name', pos_api.provider)} - {pos_api.model})*")
            st.markdown(pos_speech)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 反方发言
        if round_num == 1:
            neg_message = f"请进行第一轮发言，先反驳正方观点，再阐述己方立场。\n\n正方发言：\n{pos_speech}"
        else:
            neg_message = f"请进行第{round_num}轮发言，反驳正方并强化己方观点。\n\n上一轮正方发言：\n{pos_speech}"
        
        with progress_placeholder:
            st.info(f"🟥 反方 [{AI_PROVIDERS.get(neg_api.provider, {}).get('name', neg_api.provider)}] 正在思考... (第 {round_num} 回合)")
        
        neg_speech = call_api(neg_api, neg_system, neg_message)
        
        with debate_area:
            st.markdown('<div class="negative-box">', unsafe_allow_html=True)
            st.markdown(f"**🟥 反方发言** *({AI_PROVIDERS.get(neg_api.provider, {}).get('name', neg_api.provider)} - {neg_api.model})*")
            st.markdown(neg_speech)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # 保存回合记录
        st.session_state.debate_rounds.append((pos_speech, neg_speech))
    
    # 裁判评判
    with progress_placeholder:
        st.info(f"⚖️ 裁判 [{AI_PROVIDERS.get(judge_api.provider, {}).get('name', judge_api.provider)}] 正在评判...")
    
    # 构建完整的辩论记录给裁判
    debate_record = ""
    for i, (pos, neg) in enumerate(st.session_state.debate_rounds, 1):
        debate_record += f"=== 第 {i} 回合 ===\n\n【正方】\n{pos}\n\n【反方】\n{neg}\n\n"
    
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
            "winner": "无法判定",
            "comment": judge_response
        }
    
    # 显示裁判结果
    with debate_area:
        st.markdown('<div class="sub-header">⚖️ 裁判判决</div>', unsafe_allow_html=True)
        st.caption(f"裁判 AI: {AI_PROVIDERS.get(judge_api.provider, {}).get('name', judge_api.provider)} - {judge_api.model}")
        
        # 得分表格
        st.markdown("### 📊 得分情况")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🟦 正方总分", judge_result.get("positive_score", 0))
        with col2:
            st.metric("🟥 反方总分", judge_result.get("negative_score", 0))
        
        # 详细得分
        score_data = {
            "维度": ["论点清晰度", "逻辑严密性", "攻防能力", "综合表现"],
            "正方": [
                judge_result.get("positive_breakdown", {}).get("论点清晰度", 0),
                judge_result.get("positive_breakdown", {}).get("逻辑严密性", 0),
                judge_result.get("positive_breakdown", {}).get("攻防能力", 0),
                judge_result.get("positive_breakdown", {}).get("综合表现", 0)
            ],
            "反方": [
                judge_result.get("negative_breakdown", {}).get("论点清晰度", 0),
                judge_result.get("negative_breakdown", {}).get("逻辑严密性", 0),
                judge_result.get("negative_breakdown", {}).get("攻防能力", 0),
                judge_result.get("negative_breakdown", {}).get("综合表现", 0)
            ]
        }
        
        st.dataframe(score_data, use_container_width=True, hide_index=True)
        
        # 获胜方
        st.markdown("### 🏆 获胜方")
        st.markdown(f'<div class="winner-text">🎉 {judge_result.get("winner", "待定")} 🎉</div>', unsafe_allow_html=True)
        
        # 详细评语
        st.markdown('<div class="judge-box">', unsafe_allow_html=True)
        st.markdown("### 📝 详细评语")
        st.markdown(judge_result.get("comment", "暂无评语"))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 清除进度提示
    progress_placeholder.empty()
    st.success("✅ 辩论结束！")
    
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
    
    st.download_button(
        label="📥 下载辩论记录 (Markdown)",
        data=md_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )


if __name__ == "__main__":
    main()
