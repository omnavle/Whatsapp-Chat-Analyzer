import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# ---------------- CUSTOM CLEAN UI ----------------
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F5F7FA;
}

/* Main Title */
.main-title {
    font-size: 40px;
    font-weight: 700;
    color: #1F2937;
    text-align: center;
    margin-bottom: 30px;
}

/* Section headings */
.section-title {
    font-size: 26px;
    font-weight: 600;
    color: #111827;
    margin-top: 30px;
    margin-bottom: 15px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1E3A8A;
    color: white;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Button styling */
div.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">💬 WhatsApp Chat Analyzer Dashboard</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Upload Chat File")

uploaded_file = st.sidebar.file_uploader("Choose WhatsApp Chat File")

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Select User", user_list)

    if st.sidebar.button("Analyze Chat"):

        # ---------------- TOP STATS ----------------
        st.markdown('<div class="section-title">📊 Top Statistics</div>', unsafe_allow_html=True)

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media_messages)
        col4.metric("Links Shared", num_links)

        # ---------------- MONTHLY TIMELINE ----------------
        st.markdown('<div class="section-title">📅 Monthly Timeline</div>', unsafe_allow_html=True)

        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(12,5))
        ax.plot(timeline['date'], timeline['message'], marker='o')
        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")
        ax.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig)

        # ---------------- DAILY TIMELINE ----------------
        st.markdown('<div class="section-title">📆 Daily Timeline</div>', unsafe_allow_html=True)

        daily_timeline = helper.daily_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(12,5))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'])
        plt.xticks(rotation=45)
        ax.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig)

        # ---------------- ACTIVITY MAP ----------------
        st.markdown('<div class="section-title">🗺 Activity Map</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # ---------------- HEATMAP ----------------
        st.markdown('<div class="section-title">🔥 Weekly Activity Heatmap</div>', unsafe_allow_html=True)

        user_heatmap = helper.activity_heatmap(selected_user, df)

        fig, ax = plt.subplots(figsize=(10,6))
        sns.heatmap(user_heatmap, cmap="Blues")
        st.pyplot(fig)

        # ---------------- MOST BUSY USERS ----------------
        if selected_user == "Overall":
            st.markdown('<div class="section-title">👥 Most Busy Users</div>', unsafe_allow_html=True)

            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ---------------- WORDCLOUD ----------------
        st.markdown('<div class="section-title">☁ Wordcloud</div>', unsafe_allow_html=True)

        df_wc = helper.create_wordcloud(selected_user, df)

        fig, ax = plt.subplots(figsize=(10,5))
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # ---------------- MOST COMMON WORDS ----------------
        st.markdown('<div class="section-title">📝 Most Common Words</div>', unsafe_allow_html=True)

        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots(figsize=(10,5))
        ax.barh(most_common_df['word'], most_common_df['count'])
        st.pyplot(fig)