import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Product Hunt Dashboard", layout="wide")
st.title("Trending Product Hunt Insights")

token = st.text_input("🔑 Enter your Product Hunt Developer Token", type="password")

if token:
    query = """
    {
      posts(order: VOTES, first: 15) {
        edges {
          node {
            name
            tagline
            votesCount
            commentsCount
            topics {
              edges {
                node {
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    res = requests.post("https://api.producthunt.com/v2/api/graphql", headers=headers, json={"query": query})

    if res.status_code == 200:
        posts = res.json()["data"]["posts"]["edges"]
        data = []

        for post in posts:
            node = post["node"]
            data.append({
                "Name": node["name"],
                "Tagline": node["tagline"],
                "Upvotes": node["votesCount"],
                "Comments": node["commentsCount"],
                "Tags": ", ".join(t["node"]["name"] for t in node["topics"]["edges"])
            })

        df = pd.DataFrame(data)

        # ---- Filter by Tag ----
        all_tags = sorted({tag for row in df['Tags'] for tag in row.split(", ")})
        selected_tags = st.multiselect("🏷️ Filter by Tag(s)", options=all_tags)

        if selected_tags:
            df = df[df["Tags"].apply(lambda x: any(tag in x for tag in selected_tags))]

        # ---- Display Table ----
        st.subheader("📋 Trending Products")
        st.dataframe(df, use_container_width=True)

        # ---- Visualizations ----
        st.subheader("📊 Upvotes & Comments")
        st.bar_chart(df.set_index("Name")[["Upvotes", "Comments"]])

        # ---- Download ----
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "producthunt_trending.csv", "text/csv")

        import nltk
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        from collections import Counter

        nltk.download("stopwords")
        stopwords = set(nltk.corpus.stopwords.words("english"))

        # --- Tagline Keyword Analysis ---
        st.subheader("Common Keywords in Taglines")

        all_taglines = " ".join(df["Tagline"].tolist()).lower()
        words = [word for word in all_taglines.split() if word.isalpha() and word not in stopwords]
        word_freq = Counter(words)
        most_common_words = pd.DataFrame(word_freq.most_common(10), columns=["Word", "Frequency"])
        st.dataframe(most_common_words)

        # --- Word Cloud ---
        st.subheader("☁️ Tagline Word Cloud")
        fig, ax = plt.subplots()
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # --- Most Common Tags ---
        st.subheader("🏷️ Most Common Tags")
        tag_series = df["Tags"].str.split(", ").explode()
        tag_counts = tag_series.value_counts().reset_index()
        tag_counts.columns = ["Tag", "Count"]
        st.bar_chart(tag_counts.set_index("Tag"))
    else:
        st.error(f"Error {res.status_code}: {res.text}")


       
