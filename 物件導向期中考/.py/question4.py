"""
第四題：程式閱讀與電影評分資料分析（20 分）
讀取本機 q4_sample_page.html（由 IMDb 官方非商業資料集整理而成）。
本程式不連線網路，不需安裝第三方套件。
資料來源：IMDb Non-Commercial Datasets（title.basics.tsv.gz、title.ratings.tsv.gz；資料快照 2026-11-07）
僅供非商業教學使用，請遵守 IMDb 非商業資料集使用條款。
"""

import html
import pathlib


def read_movies(filename):
    """
    讀取本機 HTML 檔，篩選出平均評分 >= 8.8 且票數 >= 1,000,000 的電影。

    Args:
        filename: HTML 檔案路徑（pathlib.Path 或字串）

    Returns:
        list of tuple: 每部符合條件的電影為 (title, year, rating, votes)
    """
    movies = []
    with open(filename, encoding="utf-8") as page:
        for line in page:
            if "<li data-rating=" in line:
                values = line.split('"')
                rating, votes, year = float(values[1]), int(values[3]), values[5]
                title = html.unescape(line.split(">", 1)[1].split("</li>", 1)[0])
                if rating >= 8.8 and votes >= 1_000_000:
                    movies.append((title, year, rating, votes))
    return movies


# ===== 執行 =====
filename = pathlib.Path(__file__).parent / "q4_sample_page" / "q4_sample_page.html"
movies = read_movies(filename)
for title, year, rating, votes in movies:
    print(f"{title} ({year}) - {rating} ({votes:,} votes)")
print("符合電影數量：", len(movies))

# ===== 加分：改變門檻示範（rating >= 9.0）=====
print()
print("--- 若評分門檻改為 9.0 ---")
movies_90 = []
with open(filename, encoding="utf-8") as page:
    for line in page:
        if "<li data-rating=" in line:
            values = line.split('"')
            rating, votes, year = float(values[1]), int(values[3]), values[5]
            title = html.unescape(line.split(">", 1)[1].split("</li>", 1)[0])
            if rating >= 9.0 and votes >= 1_000_000:
                movies_90.append((title, year, rating, votes))
for title, year, rating, votes in movies_90:
    print(f"{title} ({year}) - {rating} ({votes:,} votes)")
print("符合電影數量（rating>=9.0）：", len(movies_90))
