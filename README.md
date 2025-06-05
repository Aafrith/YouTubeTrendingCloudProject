# YouTube Trending Videos Analysis (Hadoop Streaming + Python)

This project implements a complete pipeline to analyze YouTube trending video data across multiple countries using Hadoop Streaming (MapReduce) on Windows. We compute how many days each video remained on the trending list, then merge those counts with metadata and perform exploratory analyses in Python.

---

## 1. Project Objective

- **Goal:** Count the number of days each YouTube video appeared on the trending list and identify patterns such as the top Trending videos, category‐level trends, correlations with views and like ratios, and distribution of trending durations.
- **Why:** Understanding which videos remain trending the longest helps creators, marketers, and analysts gauge sustained user engagement and identify high‐demand content areas.

---

## 2. Dataset

1. **YouTube Trending Videos (January 2016 – December 2016):**
   - **Source:** Kaggle “YouTube New” dataset  
     (https://www.kaggle.com/datasnaek/youtube-new)  
   - **Files Used:**
     ```
     USvideos.csv
     CAvideos.csv
     DEvideos.csv
     FRvideos.csv
     GBvideos.csv
     INvideos.csv
     JPvideos.csv
     KRvideos.csv
     MXvideos.csv
     RUvideos.csv
     ```
   - **Format:** Comma‐separated CSV (UTF-8)  
   - **Columns (example):  
     ```
     video_id, trending_date, title, channel_title, category_id,
     publish_time, tags, views, likes, dislikes, comment_count,
     thumbnail_link, comments_disabled, ratings_disabled,
     video_error_or_removed, description
     ```
   - **Purpose:** Each row represents a daily snapshot of a video on that country’s trending list.

2. **Category Lookup JSONs:**
   - **Source:** YouTube Data API  
     - `US_category_id.json` (from `https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=US`)  
     - Likewise for `CA`, `DE`, `FR`, `GB`, `IN`, `JP`, `KR`, `MX`, `RU`.  
   - **Format:** JSON  
   - **Fields of Interest:**  
     ```
     items[].id                → category_id
     items[].snippet.title     → category_name
     ```
   - **Purpose:** Map `category_id` numeric codes to human‐readable category names.

---

## 3. Technologies & Environment

- **Operating System:** Windows 10 (64-bit)
- **Java:** OpenJDK 1.8 (e.g. Temurin 1.8.0_452)
- **Hadoop:** 3.3.1 standalone (pseudo‐distributed)  
  - HDFS + YARN running locally
- **Python:** 3.8+  
  - Libraries: `pandas`, `matplotlib`
- **Hadoop Streaming:** To run Python mapper/reducer
- **Text Editor/IDE:** VS Code or Notepad++

---

## 4. Project Structure

YouTubeTrendingCloudProject/
├── code/
│ ├── mapper.py # Hadoop Streaming Mapper
│ ├── reducer.py # Hadoop Streaming Reducer
│ ├── analyze.py # Python analysis script (Pandas + Matplotlib)
│ └── merge_csvs.py* # (Optional) Script to merge country CSVs into merged.csv
├── data/
│ ├── merged.csv # Final merged dataset (all countries) (Large file to upload on github)
│ └── yt/
│ ├── US_category_id.json
│ ├── CA_category_id.json
│ ├── DE_category_id.json
│ ├── FR_category_id.json
│ ├── GB_category_id.json
│ ├── IN_category_id.json
│ ├── JP_category_id.json
│ ├── KR_category_id.json
│ ├── MX_category_id.json
│ └── RU_category_id.json
├── results/
│ ├── trending_days.txt
│ ├── merged_with_counts.csv # (Large file to upload on github)
│ ├── top5_longest.csv
│ ├── avg_days_by_category.csv
│ ├── channels_long_trending.csv
│ ├── avg_views_by_bucket.csv
│ ├── avg_days_by_like_bucket.csv
│ ├── trending_duration_dist_head.csv
│ ├── trending_duration_dist_tail.csv
│ ├── top1percent_outliers.csv
│ ├── trending_duration_distribution.png
│ └── analysis_summary.txt
├── docs/
│ └── README.md # (This file)
├── screenshots/
│ 
└── video/
  └── run_hadoop_and_analysis.mp4

> Files marked with `*` are optional if you used them.

---

## 5. Prerequisites

1. **Java 8 (OpenJDK 1.8)**  
   - Verify:
     ```bat
     java -version
     ```
     Should output:  
     ```
     openjdk version "1.8.0_452"
     ```

2. **Hadoop 3.3.1**  
   - Extract to `C:\hadoop\` (or similar).  
   - Set environment variables:
     ```
     HADOOP_HOME=C:\hadoop
     JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-8.0.452-hotspot
     PATH=%PATH%;%HADOOP_HOME%\bin
     ```
   - Edit `hadoop-env.cmd` (`C:\hadoop\etc\hadoop\hadoop-env.cmd`):
     ```
     set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-8.0.452-hotspot
     ```

3. **Python 3.8+**  
   - Install from python.org.  
   - Install required packages:
     ```bat
     pip install pandas matplotlib
     ```

4. **UTF-8 Encoding**  
   - Ensure all CSV files (`*.csv`) and JSON files (`*.json`) are saved in UTF-8 (no BOM). Use Notepad++/VS Code → “Save with Encoding → UTF-8”.

---

## 6. Setup and Installation

1. **Start Hadoop Daemons**  
   - Open a new Command Prompt as Administrator.  
   - Format the NameNode (only first time):
     ```bat
     cd %HADOOP_HOME%\bin
     hdfs namenode -format
     ```
   - Start HDFS and YARN:
     ```bat
     start-dfs.cmd
     start-yarn.cmd
     ```
   - Verify all daemons are running:
     ```bat
     jps
     ```
     You should see:
     ```
     NameNode
     DataNode
     ResourceManager
     NodeManager
     ```

2. **Verify HDFS**  
   - Create base directories:
     ```bat
     hdfs dfs -mkdir -p /input
     hdfs dfs -mkdir -p /scripts
     ```
   - List root directory:
     ```bat
     hdfs dfs -ls /
     ```
     You should see `/input` and `/scripts`.

3. **Copy Project to Local Folder**  
   - Place the `YouTubeTrendingCloudProject/` folder under `C:\hadoop_data\`.  
   - Working directory:
     ```
     C:\hadoop_data\YouTubeTrendingCloudProject\
     ```

---

## 7. Running the Hadoop Streaming Job

### 7.1 Clean Old HDFS Data (if re‐running)
```bat
hdfs dfs -rm -r /input/merged.csv
hdfs dfs -rm -r /output/trending_days
hdfs dfs -rm -r /scripts

### 7.2 Upload Data & Scripts to HDFS
```bat
hdfs dfs -mkdir -p /input
hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\data\merged.csv /input/

hdfs dfs -mkdir -p /scripts
hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\code\mapper.py /scripts/
hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\code\reducer.py /scripts/

Verify:

```bat
hdfs dfs -ls /input
hdfs dfs -ls /scripts

### 7.3 Execute Hadoop Streaming
```bat
hadoop jar %HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.1.jar ^
  -files "hdfs:///scripts/mapper.py,hdfs:///scripts/reducer.py" ^
  -input /input/merged.csv ^
  -output /output/trending_days ^
  -mapper "python mapper.py" ^
  -reducer "python reducer.py"

Wait for:

map  100%   reduce  100%
Job Finished successfully

### 7.4 Retrieve Streaming Output Locally
```bat
hdfs dfs -get /output/trending_days/part-00000 C:\hadoop_data\YouTubeTrendingCloudProject\results\trending_days.txt

Verify:

```bat
type C:\hadoop_data\YouTubeTrendingCloudProject\results\trending_days.txt | more

## 8. Running the Analysis Script
From a new Command Prompt:

```bat
python C:\hadoop_data\YouTubeTrendingCloudProject\code\analyze.py
This produces in results/:

CSV Files:

merged_with_counts.csv

top5_longest.csv

avg_days_by_category.csv

channels_long_trending.csv

avg_views_by_bucket.csv

avg_days_by_like_bucket.csv

trending_duration_dist_head.csv

trending_duration_dist_tail.csv

top1percent_outliers.csv

PNG Chart:

  trending_duration_distribution.png

Text Summary:

  analysis_summary.txt

