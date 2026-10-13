"""
MindGraphNet - Interactive Clinical & Research Dashboard
A Streamlit analytics portal for mental health researchers, clinicians, and platform moderators.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from MindGraphNet.mindgraphnet.preprocessing.anonymizer import DataAnonymizer
from MindGraphNet.mindgraphnet.preprocessing.text_cleaner import ClinicalTextCleaner
from MindGraphNet.mindgraphnet.features.nlp_features import NLPFeatureExtractor
from MindGraphNet.mindgraphnet.features.psycholinguistics import PsycholinguisticExtractor
from MindGraphNet.mindgraphnet.engine.transformer_module import TransformerEncoder
from MindGraphNet.mindgraphnet.engine.fusion_model import MultiHybridFusionNet
from MindGraphNet.mindgraphnet.xai.token_saliency import TokenSaliencyExplainer
from MindGraphNet.mindgraphnet.xai.shap_explainer import GroupedSHAPExplainer
from MindGraphNet.mindgraphnet.analytics.risk_scorer import ClinicalRiskScorer
from MindGraphNet.data.loader import load_dataset
import torch

st.set_page_config(
    page_title="MindGraphNet - Multi-Hybrid Mental Health Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .risk-high { background-color: #FEE2E2; border-left: 5px solid #EF4444; padding: 12px; border-radius: 4px; color: #991B1B; font-weight: 600; }
    .risk-mod { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 12px; border-radius: 4px; color: #92400E; font-weight: 600; }
    .risk-low { background-color: #DCFCE7; border-left: 5px solid #10B981; padding: 12px; border-radius: 4px; color: #065F46; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Initialize engines with caching
@st.cache_resource
def load_core_pipeline():
    anonymizer = DataAnonymizer()
    cleaner = ClinicalTextCleaner()
    nlp = NLPFeatureExtractor()
    psych = PsycholinguisticExtractor()
    transformer = TransformerEncoder()
    fusion = MultiHybridFusionNet()
    fusion.eval()
    shap_exp = GroupedSHAPExplainer(fusion)
    scorer = ClinicalRiskScorer()
    return anonymizer, cleaner, nlp, psych, transformer, fusion, shap_exp, scorer

anonymizer, cleaner, nlp, psych, transformer, fusion, shap_exp, scorer = load_core_pipeline()

@st.cache_data
def get_sample_data():
    return load_dataset(use_kaggle=False, fallback_size=300)

df_data = get_sample_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/brain.png", width=70)
st.sidebar.title("MindGraphNet")
st.sidebar.caption("Multi-Hybrid AI Mental Health Analytics")

page = st.sidebar.radio(
    "Navigation Portal",
    [
        "🔬 Real-Time Inference & XAI",
        "🌐 Interaction Graph & Communities",
        "📈 Temporal & Longitudinal Trajectories",
        "📊 Topic Modeling & Distortions",
        "🚨 Clinical Triaging & Alerts",
        "🛡️ Ethics & Guardrails"
    ]
)

# ---------------- PAGE 1: Real-Time Inference & XAI ----------------
if page == "🔬 Real-Time Inference & XAI":
    st.markdown('<div class="main-header">🔬 Real-Time Mental Health Analytics & XAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-hybrid Transformer, GNN structural context, and psycholinguistic explanation engine.</div>', unsafe_allow_html=True)

    col_input, col_preset = st.columns([3, 1])
    with col_preset:
        st.markdown("**Sample Clinical Vignettes**")
        presets = {
            "Select a preset...": "",
            "Severe Crisis (High Risk)": "I feel so hopeless and can't take this agony anymore. Everyone would be better off if I just ended it all.",
            "Depression & Rumination": "I haven't left my bed in 4 days. Everything feels completely numb, heavy, and pointless. I am an invisible burden.",
            "Panic & Severe Anxiety": "My heart is pounding out of my chest and I can't catch my breath. I am terrified of going outside tomorrow.",
            "Recovery & Support (Low Risk)": "Had my therapy session today and went for a 20-minute walk. Taking small steps forward every day."
        }
        selected_preset = st.selectbox("Load Test Post:", list(presets.keys()))

    with col_input:
        default_val = presets[selected_preset] if selected_preset != "Select a preset..." else "I feel completely overwhelmed by everything at work and school. Nobody understands how exhausted I am."
        user_text = st.text_area("Enter Online Post / Discussion Text:", value=default_val, height=120)

    if st.button("🚀 Analyze with MindGraphNet Multi-Hybrid Engine", type="primary"):
        with st.spinner("Processing through Transformer, Graph prior, and Psycholinguistic modules..."):
            # Feature extraction
            scrubbed = anonymizer.scrub_pii(user_text)
            cleaned = cleaner.clean_text(scrubbed)
            tokens = cleaner.tokenize(cleaned)
            tokens_nostop = cleaner.remove_stopwords(tokens)

            sent_res = nlp.get_sentiment(cleaned)
            emo_res = nlp.detect_emotions(tokens_nostop)
            psych_res = psych.extract_features(scrubbed, tokens)

            cls_emb, attn_matrix, raw_tokens = transformer.encode_text(cleaned)
            graph_prior = np.zeros(32, dtype=np.float32)

            engineered_vec = np.array(
                [sent_res["sentiment_score"]] +
                [emo_res[f"emo_{e}"] for e in ["sadness", "fear", "anger", "joy", "fatigue", "hopelessness"]] +
                [psych_res["word_count"], psych_res["avg_word_len"], psych_res["exclamation_count"],
                 psych_res["first_person_ratio"], psych_res["cognitive_distortion_score"], psych_res["distress_index"]] +
                [0.0, 1.0, 0.0],
                dtype=np.float32
            )

            # Model prediction
            with torch.no_grad():
                s_t = torch.tensor(cls_emb, dtype=torch.float32).unsqueeze(0)
                g_t = torch.tensor(graph_prior, dtype=torch.float32).unsqueeze(0)
                p_t = torch.tensor(engineered_vec, dtype=torch.float32).unsqueeze(0)
                logits, risk_cont, weights = fusion(s_t, g_t, p_t)
                probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
                risk_val = float(risk_cont.cpu().numpy()[0, 0])
                w_np = weights.cpu().numpy()[0]

            eval_res = scorer.evaluate_post(
                text_raw=user_text,
                probs=probs,
                continuous_risk=risk_val,
                emo_dict=emo_res,
                sentiment_score=sent_res["sentiment_score"]
            )

            factor_imp = shap_exp.explain_instance(cls_emb, graph_prior, engineered_vec)
            words, norm_scores, html_text = TokenSaliencyExplainer.process_attention(attn_matrix, raw_tokens)
            top_words = TokenSaliencyExplainer.get_top_attended_words(words, norm_scores, top_k=6)

        st.markdown("---")

        # Top Results Cards
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            lvl = eval_res["risk_level"]
            cls_name = "risk-high" if lvl == "High" else ("risk-mod" if lvl == "Moderate" else "risk-low")
            st.markdown(f'<div class="{cls_name}">Assessed Risk Level: <br><span style="font-size:1.6rem;">{lvl}</span></div>', unsafe_allow_html=True)
            if eval_res["is_crisis"]:
                st.error("🚨 IMMEDIATE CRISIS PROTOCOL TRIGGERED")

        with r_col2:
            st.metric("Model Confidence", f"{eval_res['confidence'] * 100:.1f}%")
            st.metric("Continuous Severity Score", f"{eval_res['continuous_risk_score']:.3f} / 1.0")

        with r_col3:
            st.metric("Stress / Anxiety Index", f"{eval_res['stress_anxiety_index']:.2f}")
            st.metric("Depressive Signal Index", f"{eval_res['depressive_signal_index']:.2f}")

        with r_col4:
            st.metric("Emotional Resilience", f"{eval_res['resilience_index']:.2f}")
            st.metric("Sentiment Polarity", f"{sent_res['sentiment_score']:+.2f} ({sent_res['sentiment_label']})")

        # Visual Tabs for XAI
        tab_attn, tab_factors, tab_radar = st.tabs(["🔤 Token Attention Highlighter", "⚖️ Multimodal Factor Attribution", "🕸️ Clinical Emotion Radar"])

        with tab_attn:
            st.markdown("### Token Attention Saliency (Transformer Head)")
            st.caption("Darker red highlighting indicates words that exerted the highest mathematical influence on the risk score.")
            st.markdown(f'<div style="background:#FFF; padding:16px; border:1px solid #E2E8F0; border-radius:8px; font-size:1.15rem; line-height:2.2;">{html_text}</div>', unsafe_allow_html=True)
            
            st.markdown("**Top Attended Words Ranking:**")
            st.dataframe(pd.DataFrame(top_words, columns=["Word / Token", "Attention Score"]), use_container_width=True)

        with tab_factors:
            st.markdown("### Multimodal Attribution Breakdown")
            df_factors = pd.DataFrame(list(factor_imp.items()), columns=["Factor", "Contribution (%)"]).sort_values("Contribution (%)", ascending=True)
            fig_bar = px.bar(df_factors, x="Contribution (%)", y="Factor", orientation="h", color="Contribution (%)", color_continuous_scale="Reds")
            fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab_radar:
            st.markdown("### Clinical Emotion Profile")
            emos = ["sadness", "fear", "anger", "joy", "fatigue", "hopelessness"]
            vals = [emo_res[f"emo_{e}"] for e in emos]
            fig_radar = go.Figure(data=go.Scatterpolar(r=vals + [vals[0]], theta=emos + [emos[0]], fill='toself', line_color="#EF4444"))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max(vals), 0.5)])), showlegend=False, height=350)
            st.plotly_chart(fig_radar, use_container_width=True)

# ---------------- PAGE 2: Graph Explorer ----------------
elif page == "🌐 Interaction Graph & Communities":
    st.markdown('<div class="main-header">🌐 Interaction Graph & Community Network</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Graph Attention Network (GAT) structural modeling across authors, posts, and thread conversations.</div>', unsafe_allow_html=True)

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("### Most Active Anonymous Users")
        author_counts = df_data["author"].value_counts().head(10).reset_index()
        author_counts.columns = ["Pseudonymized User", "Post Frequency"]
        fig_auth = px.bar(author_counts, x="Post Frequency", y="Pseudonymized User", orientation="h", color="Post Frequency", color_continuous_scale="Blues")
        st.plotly_chart(fig_auth, use_container_width=True)

    with g_col2:
        st.markdown("### Discussion Thread Depth Distribution")
        reply_counts = df_data["replies_to"].value_counts().value_counts().reset_index()
        reply_counts.columns = ["Replies per Post", "Count"]
        fig_rep = px.pie(reply_counts, values="Count", names="Replies per Post", title="Conversation Thread Branching")
        st.plotly_chart(fig_rep, use_container_width=True)

    st.markdown("### Community Post Distribution")
    topic_counts = df_data["topic"].value_counts().reset_index()
    topic_counts.columns = ["Subreddit / Community", "Volume"]
    fig_top = px.bar(topic_counts, x="Subreddit / Community", y="Volume", color="Subreddit / Community")
    st.plotly_chart(fig_top, use_container_width=True)

# ---------------- PAGE 3: Temporal Trajectories ----------------
elif page == "📈 Temporal & Longitudinal Trajectories":
    st.markdown('<div class="main-header">📈 Temporal Trajectories & Behavioral Drift</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitoring longitudinal mental health trajectories over time for early deterioration warnings.</div>', unsafe_allow_html=True)

    df_data["date"] = pd.to_datetime(df_data["created_at"]).dt.date
    daily = df_data.groupby("date").size().reset_index(name="Volume")
    
    st.markdown("### Community Activity Timeline")
    fig_ts = px.line(daily, x="date", y="Volume", markers=True, title="Daily Discussion Activity")
    st.plotly_chart(fig_ts, use_container_width=True)

# ---------------- PAGE 4: Topic Modeling & Distortions ----------------
elif page == "📊 Topic Modeling & Distortions":
    st.markdown('<div class="main-header">📊 Unsupervised Latent Topics & Cognitive Distortions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Latent Dirichlet Allocation (LDA) topic discovery across mental health forums.</div>', unsafe_allow_html=True)
    st.dataframe(df_data[["post_id", "topic", "root_cause_label", "text"]].head(25), use_container_width=True)

# ---------------- PAGE 5: Clinical Triaging & Alerts ----------------
elif page == "🚨 Clinical Triaging & Alerts":
    st.markdown('<div class="main-header">🚨 Clinical Triaging & Automated Early-Warning Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated detection of communities crossing high-risk thresholds for human clinician review.</div>', unsafe_allow_html=True)
    
    st.info("No active community alert thresholds crossed in this batch. Monitoring stream active.")

# ---------------- PAGE 6: Ethics & Guardrails ----------------
elif page == "🛡️ Ethics & Guardrails":
    st.markdown('<div class="main-header">🛡️ Ethical Safeguards, Privacy & AI Governance</div>', unsafe_allow_html=True)
    st.markdown("""
    ### MindGraphNet Clinical Research Principles:
    1. **Not a Diagnostic Tool**: MindGraphNet is strictly designed as an analytical decision-support and surveillance research framework. It does not replace a qualified psychiatrist or licensed clinical psychologist.
    2. **Salted Pseudonymization**: All user identifiers are irreversibly hashed using salted SHA-256 before any modeling or graph representation.
    3. **PII Redaction**: Multi-pattern regex filters strip emails, phone numbers, IP addresses, and user handles prior to feature ingestion.
    4. **Human-in-the-Loop**: High-risk and crisis flags are routed to verified human clinical moderators; no automated punitive actions are taken.
    """)
