import streamlit as st
from tavily import TavilyClient
import re
from urllib.parse import urlparse

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Tavily Smart Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.box {
    background:#0e1117;
    padding:15px;
    border-radius:12px;
    margin-bottom:12px;
}
.title {
    font-size:18px;
    font-weight:700;
    color:#4da6ff;
}
.text {
    font-size:15px;
    line-height:1.6;
}
.source {
    font-size:13px;
    color:#9aa0a6;
}
.confidence {
    font-size:14px;
    margin-bottom:10px;
}
.compare-title {
    font-size:22px;
    font-weight:800;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def clean_text(text):
    if not text:
        return "No useful summary found."
    text = re.sub(r"#{1,6}", "", text)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"\|.*?\|", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    sentences = text.split(". ")
    return ". ".join(sentences[:3]) + "."

def source_confidence(results):
    domains = set()
    for r in results:
        url = r.get("url", "")
        if url:
            domains.add(urlparse(url).netloc.replace("www.", ""))
    count = len(domains)
    if count >= 5:
        return "High", count
    elif count >= 3:
        return "Medium", count
    else:
        return "Low", count

def run_search(client, query, depth):
    return client.search(
        query=query,
        search_depth=depth,
        max_results=5
    )

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Controls")

api_key = st.sidebar.text_input(
    "Tavily API Key",
    type="password",
    placeholder="tvly-xxxxxxxx"
)

mode = st.sidebar.radio(
    "Mode",
    ["🔍 Search", "🆚 Compare"]
)

search_type = st.sidebar.radio(
    "Search Depth",
    ["🔍 Normal", "🚀 Advanced"]
)

latest_mode = st.sidebar.checkbox("🆕 Latest / What’s New")

st.sidebar.markdown("---")
st.sidebar.info("📊 Source confidence is calculated automatically.")

# ---------------- MAIN UI ----------------
st.title("🤖 Tavily Smart Chatbot")
st.caption("Search, Compare, and Analyze using real-time web data")

if mode == "🔍 Search":
    query = st.text_input("Ask something from the web")

elif mode == "🆚 Compare":
    col1, col2 = st.columns(2)
    with col1:
        topic1 = st.text_input("Topic 1")
    with col2:
        topic2 = st.text_input("Topic 2")

search_btn = st.button("🔎 Run")

# ---------------- LOGIC ----------------
if search_btn:
    if not api_key:
        st.error("Please enter Tavily API key")
    else:
        client = TavilyClient(api_key=api_key)
        depth = "advanced" if "Advanced" in search_type else "basic"

        if mode == "🔍 Search":
            if not query:
                st.error("Please enter a query")
            else:
                final_query = (
                    f"Latest updates about {query} in the last 6 months"
                    if latest_mode
                    else query
                )

                with st.spinner("Searching..."):
                    response = run_search(client, final_query, depth)

                results = response.get("results", [])
                conf, count = source_confidence(results)

                st.markdown(
                    f"<div class='confidence'>🔍 Confidence: <b>{conf}</b> "
                    f"({count} unique sources)</div>",
                    unsafe_allow_html=True
                )

                for r in results:
                    st.markdown(f"""
                    <div class="box">
                        <div class="title">{r.get("title","")}</div>
                        <div class="text">{clean_text(r.get("content",""))}</div>
                        <div class="source">
                            🔗 <a href="{r.get("url")}" target="_blank">Source</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ---------------- COMPARE MODE ----------------
        elif mode == "🆚 Compare":
            if not topic1 or not topic2:
                st.error("Please enter both topics")
            else:
                q1 = (
                    f"Latest updates about {topic1} in the last 6 months"
                    if latest_mode
                    else f"What is {topic1}"
                )
                q2 = (
                    f"Latest updates about {topic2} in the last 6 months"
                    if latest_mode
                    else f"What is {topic2}"
                )

                with st.spinner("Comparing topics..."):
                    res1 = run_search(client, q1, depth)
                    res2 = run_search(client, q2, depth)

                results1 = res1.get("results", [])
                results2 = res2.get("results", [])

                conf1, c1 = source_confidence(results1)
                conf2, c2 = source_confidence(results2)

                st.markdown(
                    f"<div class='compare-title'>📊 {topic1} vs {topic2}</div>",
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(topic1)
                    st.markdown(
                        f"<div class='confidence'>Confidence: <b>{conf1}</b> "
                        f"({c1} sources)</div>",
                        unsafe_allow_html=True
                    )
                    for r in results1:
                        st.markdown(f"""
                        <div class="box">
                            <div class="title">{r.get("title","")}</div>
                            <div class="text">{clean_text(r.get("content",""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    st.subheader(topic2)
                    st.markdown(
                        f"<div class='confidence'>Confidence: <b>{conf2}</b> "
                        f"({c2} sources)</div>",
                        unsafe_allow_html=True
                    )
                    for r in results2:
                        st.markdown(f"""
                        <div class="box">
                            <div class="title">{r.get("title","")}</div>
                            <div class="text">{clean_text(r.get("content",""))}</div>
                        </div>
                        """, unsafe_allow_html=True)

