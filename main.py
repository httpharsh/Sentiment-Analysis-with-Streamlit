import streamlit as st
import asyncio
import plotly.express as px
from scrapper import load_tweets, analyze_sentiment

st.set_page_config(page_title="Twitter Sentiment Analysis", layout="wide")

st.markdown("<h1 style='text-align: center;'>Twitter Sentiment Analyzer</h1>", unsafe_allow_html=True)

st.markdown("""
    <style>
        div[data-testid="stTextInput"] > div > div > input {
            width: 300px;
            margin: auto;   
        }
        div[data-testid="stTextInput"] > div > div > input {
            text-align: center; /* Center text inside input */
            font-size: 14px; /* Adjust font size */
            padding: 8px;
        }
        div[data-testid="stButton"] > button {
            width: 150px;
            display: block;
            margin: auto;
            font-size: 14px;
            padding: 5px;
        }
    </style>
""", unsafe_allow_html=True)

if "tweets_df" not in st.session_state:
    st.session_state.tweets_df = None
if "username" not in st.session_state:
    st.session_state.username = ""

username = st.text_input("", placeholder="Enter Twitter Username", key="username_input")

if st.button("Analyze"):
    if username:
        st.session_state.username = username
        st.info("Fetching and analyzing tweets... Please wait.")

        df = asyncio.run(load_tweets(username))

        if df.empty:
            st.warning("No tweets found or an error occurred.")
        else:
            df["Sentiment"] = df["tweets"].apply(analyze_sentiment)

            st.session_state.tweets_df = df
    else:
        st.error("Please enter a valid Twitter username.")

if st.session_state.tweets_df is not None:
    df = st.session_state.tweets_df  

    sentiment_count = df["Sentiment"].value_counts().to_dict()

    st.subheader(f"Sentiment Analysis of @{st.session_state.username}'s Tweets")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Sentiment Distribution")
        fig = px.pie(
            names=sentiment_count.keys(),
            values=sentiment_count.values(),
            title="Sentiment Distribution",
            color=sentiment_count.keys(),
            color_discrete_map={"Positive": "#2ecc71", "Negative": "#e74c3c", "Neutral": "#f1c40f"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Total Tweets", len(df))
        st.metric("Positive", sentiment_count.get("Positive", 0))
        st.metric("Negative", sentiment_count.get("Negative", 0))
        st.metric("Neutral", sentiment_count.get("Neutral", 0))

    tweets_per_page = 10
    total_pages = max(1, -(-len(df) // tweets_per_page))

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = 1

    if total_pages > 1:
        st.session_state.selected_page = st.radio("Select Page", options=list(range(1, total_pages + 1)), horizontal=True)

    page = st.session_state.selected_page
    start_idx = (page - 1) * tweets_per_page
    end_idx = start_idx + tweets_per_page

    st.write(f"### Showing Page {page} of {total_pages}")

    sentiment_color = {
        "Positive": "🟢",
        "Negative": "🔴",
        "Neutral": "🟡"
    }

    for _, row in df.iloc[start_idx:end_idx].iterrows():
        sentiment_icon = sentiment_color.get(row["Sentiment"], "⚪")
        st.write(f"{sentiment_icon} **{row['Sentiment']}**: {row['tweets']}")
