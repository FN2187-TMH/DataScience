from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# ============================
# 1) LOAD DỮ LIỆU TOÀN CỤC
# ============================
df = pd.read_csv("recommend_system.csv")

# Chuẩn hóa khi load để tránh xử lý nhiều lần
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Review Count"] = df["Review Count"].apply(
    lambda x: int(str(x).replace(",", "")) if pd.notna(x) else 0
)

df_json = df.to_json(orient="records")   # pandas tự convert NaN → null


# ============================
# 2) DASHBOARD
# ============================
@app.route("/")
def dashboard():

    total_movies = len(df)
    total_features = len(df.columns) - 2  # bỏ id + recommended_ids
    total_reviews = df["Review Count"].sum()

    # Highest rated movie
    if df["Rating"].notna().any():
        top_movie = df.loc[df["Rating"].idxmax()]
        top_movie_title = top_movie["Title"]
        top_movie_rating = top_movie["Rating"]
    else:
        top_movie_title = "Unknown"
        top_movie_rating = 0

    return render_template(
        "dashboard.html",
        total_movies=total_movies,
        total_features=total_features,
        top_movie_title=top_movie_title,
        top_movie_rating=top_movie_rating,
        total_reviews=total_reviews,
        df_json=df_json,
    )


# ============================
# 3) PAGE TRENDS (Tạm – bạn sẽ vẽ trên HTML)
# ============================
@app.route("/trends")
def trends():
    return render_template("trends.html", df_json=df_json)


# ============================
# 4) PAGE DISTRIBUTION
# ============================
@app.route("/distribution")
def distribution():
    return render_template("distribution.html", df_json=df_json)


# ============================
# 5) PAGE RECOMMEND
# ============================
@app.route("/recommend")
def recommend():
    # bạn tự tạo biến recommended_items sau
    return render_template("recommend.html", df_json=df_json)


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    app.run(debug=True)
