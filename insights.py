import requests
import pandas as pd

DEV_TOKEN = "1v3uOw5OtUb-nMgFnLuJOuylAiP-kJ0wtN-n8k_QOhs"

headers = {
    "Authorization": f"Bearer {DEV_TOKEN}",
    "Content-Type": "application/json"
}

query = """
{
  posts(order: VOTES, first: 10) {
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

response = requests.post(
    "https://api.producthunt.com/v2/api/graphql",
    headers=headers,
    json={"query": query}
)

if response.status_code == 200:
    result = response.json()
    posts = result["data"]["posts"]["edges"]

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
    print(df)

    df.to_csv("producthunt_trending.csv", index=False)
    print("\nData saved to producthunt_trending.csv")
else:
    print("Request failed:", response.status_code)
    print(response.text)
