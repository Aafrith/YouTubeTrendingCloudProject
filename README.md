# YouTube Trending Videos Analysis (Hadoop Streaming + Python)

This project implements a complete pipeline to analyze YouTube trending video data across multiple countries using Hadoop Streaming (MapReduce) on Windows. We compute how many days each video remained on the trending list, then merge those counts with metadata and perform exploratory analyses in Python.

---

## 1. Project Objective

- **Goal:** Count the number of days each YouTube video appeared on the trending list and identify patterns such as the top trending videos, category‐level trends, correlations with views and like ratios, and the distribution of trending durations.
- **Why:** Understanding which videos remain trending the longest helps creators, marketers, and analysts gauge sustained user engagement and identify high‐demand content areas.

---

## 2. Dataset

1. **YouTube Trending Videos (January–December 2016):**
   - **Source:** Kaggle “YouTube New” dataset  
     (https://www.kaggle.com/datasnaek/youtube-new)  
   - **Files Used (all UTF-8 encoded):**
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
   - **Columns (example):**  
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
   - **Purpose:** Map numeric `category_id` codes to human‐readable category names.

---

## 3. Technologies & Environment

- **Operating System:** Windows 10 (64-bit)  
- **Java:** OpenJDK 1.8 (e.g., Temurin 1.8.0_452)  
- **Hadoop:** 3.3.1 standalone (pseudo-distributed)  
  - HDFS + YARN running locally  
- **Python:** 3.8+  
  - Libraries: `pandas`, `matplotlib`  
- **Hadoop Streaming:** To run Python mapper/reducer  
- **Text Editor/IDE:** VS Code or Notepad++

---

---

## 4. Prerequisites

1. **Java 8 (OpenJDK 1.8)**  
   - Verify:
     ```bat
     java -version
     ```
     You should see:
     ```
     openjdk version "1.8.0_452"
     ```

2. **Hadoop 3.3.1**  
   - Extract to `C:\hadoop\`  
   - Set environment variables:
     ```
     HADOOP_HOME=C:\hadoop
     JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-8.0.452-hotspot
     PATH=%PATH%;%HADOOP_HOME%\bin
     ```
   - Edit `hadoop-env.cmd`:
     ```bat
     set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-8.0.452-hotspot
     ```

3. **Python 3.8+**  
   - Install from: https://www.python.org/downloads/  
   - Install required packages:
     ```bat
     pip install pandas matplotlib
     ```

4. **UTF-8 Encoding**  
   - Ensure all CSV and JSON files are UTF-8 encoded (no BOM).

---

## 5. Setup and Installation

1. **Start Hadoop Daemons**  
   ```bat
   cd %HADOOP_HOME%\bin
   hdfs namenode -format   # Only first time
   start-dfs.cmd
   start-yarn.cmd
   jps

You should see:
```
  nginx
  Copy
  Edit
  NameNode
  DataNode
  ResourceManager
  NodeManager
```

2. **Verify HDFS**
   ```bat
   hdfs dfs -mkdir -p /input
   hdfs dfs -mkdir -p /scripts
   hdfs dfs -ls /

3. **Copy Project to Local Folder**
   
        C:\hadoop_data\YouTubeTrendingCloudProject\

---

## 6. Running the Hadoop Streaming Job

6.1 Clean Old HDFS Data (Optional)
```
  hdfs dfs -rm -r /input/merged.csv
  hdfs dfs -rm -r /output/trending_days
  hdfs dfs -rm -r /scripts
```
6.2 Upload Data & Scripts to HDFS
```
   hdfs dfs -mkdir -p /input
   hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\data\merged.csv /input/

   hdfs dfs -mkdir -p /scripts
   hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\code\mapper.py /scripts/
   hdfs dfs -put C:\hadoop_data\YouTubeTrendingCloudProject\code\reducer.py /scripts/

   hdfs dfs -ls /input
   hdfs dfs -ls /scripts
```

6.3 Execute Hadoop Streaming
```
   hadoop jar %HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming-3.3.1.jar ^
     -files "hdfs:///scripts/mapper.py,hdfs:///scripts/reducer.py" ^
     -input /input/merged.csv ^
     -output /output/trending_days ^
     -mapper "python mapper.py" ^
     -reducer "python reducer.py"
   You should see:

   arduino

   map 100%   reduce 100%
   Job Finished successfully
```
6.4 Retrieve Streaming Output Locally
```
   hdfs dfs -get /output/trending_days/part-00000 C:\hadoop_data\YouTubeTrendingCloudProject\results\trending_days.txt
   type C:\hadoop_data\YouTubeTrendingCloudProject\results\trending_days.txt | more
   Example Output:

   n1WpP7iowLc    7
   0dBIkQ4Mz1M    5
   5qpjK5DgCt4    6
```
7. Running the Analysis Script
```
Open a new Command Prompt, then run:

   python C:\hadoop_data\YouTubeTrendingCloudProject\code\analyze.py
   This will generate output files in the results/ folder:

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

Chart:
   trending_duration_distribution.png

Summary:
   analysis_summary.txt

Open results/analysis_summary.txt to view key insights from the data analysis.
```
