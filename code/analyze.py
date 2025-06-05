import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import sys

# Paths (adjust if needed)
td_path = r"C:\hadoop_data\output\trending_days.txt"
merged_path = r"C:\hadoop_data\input\merged.csv"
category_dir = r"C:\hadoop_data\yt"  # folder containing all *_category_id.json files
output_dir = r"C:\hadoop_data\output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Open a summary file for writing (this will capture all “print” output)
summary_path = os.path.join(output_dir, "analysis_summary.txt")
summary_file = open(summary_path, "w", encoding="utf-8")

def log(msg=""):
    """
    Write `msg` to both stdout and the summary file.
    """
    print(msg)
    summary_file.write(msg + "\n")

# 1) Load trending-days counts
trending_df = pd.read_csv(td_path, sep="\t", names=["video_id", "days_trended"])

# 2) Load merged metadata
meta_df = pd.read_csv(merged_path, dtype=str)

# Deduplicate: keep the first occurrence of each video_id
meta_unique = meta_df.drop_duplicates(subset=["video_id"], keep="first")

# 3) Merge on video_id
merged_all = pd.merge(trending_df, meta_unique, on="video_id", how="left")

# 4) Convert numeric columns
merged_all["days_trended"] = merged_all["days_trended"].astype(int)
merged_all["views"] = pd.to_numeric(merged_all["views"], errors="coerce").fillna(0).astype(int)
merged_all["likes"] = pd.to_numeric(merged_all["likes"], errors="coerce").fillna(0).astype(int)
merged_all["dislikes"] = pd.to_numeric(merged_all["dislikes"], errors="coerce").fillna(0).astype(int)
merged_all["comment_count"] = pd.to_numeric(merged_all["comment_count"], errors="coerce").fillna(0).astype(int)

# 5) Map category_id to category_name by scanning all JSON files in category_dir
cat_map = {}
for fname in os.listdir(category_dir):
    if fname.endswith("_category_id.json"):
        full_path = os.path.join(category_dir, fname)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f).get("items", [])
                for item in data:
                    cid = str(item.get("id", "")).strip()
                    title = item.get("snippet", {}).get("title", "").strip()
                    if cid and title:
                        cat_map[cid] = title
        except Exception as e:
            log(f"Warning: failed to load {full_path}: {e}")

merged_all["category_name"] = merged_all["category_id"].map(cat_map).fillna("Unknown")

# 6) Save full merged result
merged_all.to_csv(os.path.join(output_dir, "merged_with_counts.csv"), index=False)

# 7) Top 5 longest-trending videos
top5 = merged_all.sort_values("days_trended", ascending=False).head(5)
top5.to_csv(os.path.join(output_dir, "top5_longest.csv"), index=False)

# 8) Average days_trended per category
avg_by_cat = merged_all.groupby("category_name")["days_trended"].mean().reset_index()
avg_by_cat = avg_by_cat.sort_values("days_trended", ascending=False)
avg_by_cat.to_csv(os.path.join(output_dir, "avg_days_by_category.csv"), index=False)

# 9) Channels with most >= 5-day trending videos
long_trends = merged_all[merged_all["days_trended"] >= 5]
channel_counts = long_trends.groupby("channel_title")["video_id"].count().reset_index()
channel_counts.columns = ["channel_title", "long_trending_count"]
channel_counts = channel_counts.sort_values("long_trending_count", ascending=False)
channel_counts.to_csv(os.path.join(output_dir, "channels_long_trending.csv"), index=False)

# 10) Correlation: days_trended vs views
corr_views = merged_all[["days_trended", "views"]].corr().loc["days_trended", "views"]

# Bucket by days_trended
def bucket_days(x):
    if x <= 2:
        return "short (1-2)"
    elif x <= 5:
        return "medium (3-5)"
    else:
        return "long (6+)"
merged_all["trend_bucket"] = merged_all["days_trended"].apply(bucket_days)

avg_views_by_bucket = merged_all.groupby("trend_bucket")["views"].mean().reset_index()
avg_views_by_bucket = avg_views_by_bucket.sort_values("views", ascending=False)
avg_views_by_bucket.to_csv(os.path.join(output_dir, "avg_views_by_bucket.csv"), index=False)

# 11) Like ratio and correlation
merged_all["like_ratio"] = merged_all["likes"] / (merged_all["likes"] + merged_all["dislikes"] + 1e-9)
corr_like = merged_all[["days_trended", "like_ratio"]].corr().loc["days_trended", "like_ratio"]

# Bucket by like_ratio
def bucket_like(x):
    if x >= 0.90:
        return "high (>= 0.90)"
    elif x >= 0.70:
        return "medium (0.70-0.90)"
    else:
        return "low (< 0.70)"
merged_all["ratio_bucket"] = merged_all["like_ratio"].apply(bucket_like)

avg_days_by_ratio = merged_all.groupby("ratio_bucket")["days_trended"].mean().reset_index()
avg_days_by_ratio = avg_days_by_ratio.sort_values("days_trended", ascending=False)
avg_days_by_ratio.to_csv(os.path.join(output_dir, "avg_days_by_like_bucket.csv"), index=False)

# 12) Distribution of days_trended
dist = merged_all["days_trended"].value_counts().sort_index()
dist.head(10).to_csv(os.path.join(output_dir, "trending_duration_dist_head.csv"), header=["count"])
dist.tail(5).to_csv(os.path.join(output_dir, "trending_duration_dist_tail.csv"), header=["count"])

# Outliers: top 1%
threshold = merged_all["days_trended"].quantile(0.99)
outliers = merged_all[merged_all["days_trended"] >= threshold]
outliers.to_csv(os.path.join(output_dir, "top1percent_outliers.csv"), index=False)

# Bar chart for first 10 duration bins
plt.figure(figsize=(8, 4))
dist.iloc[:10].plot(kind="bar")
plt.title("Number of Videos by Days Trended (1–10 days)")
plt.xlabel("Days Trended")
plt.ylabel("Number of Videos")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "trending_duration_distribution.png"))
plt.close()

# -- Now write all summary text to analysis_summary.txt via log() --

log("=== Top 5 Longest-Trending Videos ===")
log(top5[["video_id", "title", "channel_title", "category_name", "days_trended"]].to_string(index=False))

log("\n=== Correlation (days_trended vs. views) ===")
log(f"{corr_views:.3f}")

log("\n=== Average Views by Trending-Duration Bucket ===")
log(avg_views_by_bucket.to_string(index=False))

log("\n=== Correlation (days_trended vs. like_ratio) ===")
log(f"{corr_like:.3f}")

log("\n=== Average Days_Trended by Like-Ratio Bucket ===")
log(avg_days_by_ratio.to_string(index=False))

log("\n=== Trending-Duration Distribution (First 10 Bins) ===")
log(dist.head(10).to_string())

log(f"\n=== Trending-Duration Threshold for Top 1%: {threshold} ===")
log("\n=== Outlier Videos (Top 1% by Days_Trended) ===")
log(outliers[["video_id", "title", "channel_title", "days_trended"]].to_string(index=False))

# Close the summary file
summary_file.close()
