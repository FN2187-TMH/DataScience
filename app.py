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
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
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
    all_genres = set()
    for g in df['Genre'].dropna():
        for gg in g.split(','):
            all_genres.add(gg.strip())

    all_genres = sorted(list(all_genres))

    all_years = sorted([str(int(y)) for y in df['Year'].dropna() if str(y).replace('.', '', 1).isdigit()], reverse=True)
    all_years = sorted(list(set(all_years)), reverse=True)

    return render_template(
        "recommend.html",
        df_json=df_json,
        all_genres=all_genres,
        all_years=all_years
    )


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    # Lọc movie dựa vào id
    movie_row = df[df["id"] == movie_id]

    if movie_row.empty:
        # Nếu không tìm thấy movie, trả về 404 hoặc redirect
        return "Movie not found", 404

    # Lấy record dưới dạng dict
    movie = movie_row.iloc[0].to_dict()

    # Tìm phim tương đồng dựa vào recommended_ids
    similar_movies = []
    if movie.get("recommended_ids"):
        rec_ids = [int(i) for i in movie["recommended_ids"].strip("[]").split(",") if i.strip().isdigit()]
        similar_movies = df[df["id"].isin(rec_ids)].to_dict(orient="records")

    return render_template(
        "movie_detail.html",
        movie=movie,
        similar_movies=similar_movies
    )

@app.route("/correlation")
def correlation():
    return render_template("correlation.html", df_json=df_json)


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    app.run(debug=True)
