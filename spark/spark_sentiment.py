from pyspark.sql import SparkSession
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from pyspark.sql.functions import when, col, concat_ws
from pyspark.sql.functions import sum as spark_sum
import math

kote_labels = [
  '불평/불만','환영/호의','감동/감탄','지긋지긋','고마움','슬픔',
  '화남/분노','존경','기대감','우쭐댐/무시함','안타까움/실망','비장함',
  '의심/불신','뿌듯함','편안/쾌적','신기함/관심','아껴주는','부끄러움',
  '공포/무서움','절망','한심함','역겨움/징그러움','짜증','어이없음',
  '없음','패배/자기혐오','귀찮음','힘듦/지침','즐거움/신남','깨달음',
  '죄책감','증오/혐오','흐뭇함(귀여움/예쁨)','당황/난처','경악',
  '부담/안_내킴','서러움','재미없음','불쌍함/연민','놀람','행복',
  '불안/걱정','기쁨','안심/신뢰'
]

positive = [
    '환영/호의',
    '감동/감탄',
    '고마움',
    '존경',
    '기대감',
    '뿌듯함',
    '편안/쾌적',
    '신기함/관심',
    '아껴주는',
    '즐거움/신남',
    '깨달음',
    '흐뭇함(귀여움/예쁨)',
    '행복',
    '기쁨',
    '안심/신뢰'
]

negative = [
    '불평/불만',
    '지긋지긋',
    '슬픔',
    '화남/분노',
    '안타까움/실망',
    '의심/불신',
    '공포/무서움',
    '절망',
    '한심함',
    '역겨움/징그러움',
    '짜증',
    '어이없음',
    '패배/자기혐오',
    '귀찮음',
    '힘듦/지침',
    '죄책감',
    '증오/혐오',
    '당황/난처',
    '경악',
    '부담/안_내킴',
    '서러움',
    '재미없음',
    '불쌍함/연민',
    '불안/걱정'
]


# ----------------------------
# 1. Spark Session (SQLite JDBC 포함)
# ----------------------------

spark = SparkSession.builder \
    .appName("MabinogiSentiment") \
    .config("spark.jars", "/opt/jars/sqlite-jdbc.jar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ----------------------------
# 2. SQLite 데이터 로드
# ----------------------------

inven_df = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlite:/data/identifier.sqlite") \
    .option("dbtable", "inven_comment") \
    .option("driver", "org.sqlite.JDBC") \
    .load() \
    .select("id", "articlecode", "comment")

dc_df = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlite:/data/identifier.sqlite") \
    .option("dbtable", "dc_comment") \
    .option("driver", "org.sqlite.JDBC") \
    .load() \
    .select("id", "articlecode", "comment")

inven_post_df = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlite:/data/identifier.sqlite") \
    .option("dbtable", "inven_post") \
    .option("driver", "org.sqlite.JDBC") \
    .load() \
    .select(col("articlecode").alias("id"),
            "articlecode",
            concat_ws(" ", col("title"), col("article")).alias("comment"))

dc_post_df = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlite:/data/identifier.sqlite") \
    .option("dbtable", "dc_post") \
    .option("driver", "org.sqlite.JDBC") \
    .load() \
    .select(col("articlecode").alias("id"),
            "articlecode",
            concat_ws(" ", col("title"), col("article")).alias("comment"))

comments_df = inven_df.unionByName(dc_df).na.drop()
# comments_df = comments_df.unionByName(inven_post_df).na.drop()
# comments_df = comments_df.unionByName(dc_post_df).na.drop()

reward_df = spark.read.format("jdbc") \
    .option("url", "jdbc:sqlite:/data/identifier.sqlite") \
    .option("dbtable", "inspection_reward") \
    .option("driver", "org.sqlite.JDBC") \
    .load().select("item_name")

# ----------------------------
# 3. Spark → Pandas
# ----------------------------

pdf = comments_df.toPandas()
reward_items = reward_df.toPandas()["item_name"].unique().tolist()

# ----------------------------
# 4. HuggingFace 감정 분석
# ----------------------------

classifier = pipeline(
    "text-classification",
    model="tobykim/koelectra-44emotions",
    batch_size=16,
    truncation=True,
    max_length=128
)
# label_map = classifier.model.config.id2label

results = classifier(
    pdf["comment"].tolist()
)

pdf["emotion"] = [
    kote_labels[int(r["label"].replace("LABEL_", ""))]
    for r in results
]

# ----------------------------
# 5. 감정 그룹화
# ----------------------------

pdf["sentiment"] = "neutral"
pdf.loc[pdf["emotion"].isin(positive), "sentiment"] = "positive"
pdf.loc[pdf["emotion"].isin(negative), "sentiment"] = "negative"

# =====================
# 5. 점검 전체 감정
# =====================

overall = (
    pdf.groupby("sentiment")
       .size()
       .reset_index(name="count")
)

overall["ratio"] = overall["count"] / overall["count"].sum()

print("\n=== 점검 전체 감정 ===")
print(overall)

id_sentiment = (
    pdf[pdf["sentiment"].isin(["positive", "negative"])]
    .groupby(["articlecode", "sentiment"])
    .size()
    .reset_index(name="count")
)

top_positive = (
    id_sentiment[id_sentiment["sentiment"] == "positive"]
    .sort_values("count", ascending=False)
    .head(10)
)

print("\n=== 긍정 TOP10 ID ===")
print(top_positive)

top_negative = (
    id_sentiment[id_sentiment["sentiment"] == "negative"]
    .sort_values("count", ascending=False)
    .head(10)
)

print("\n=== 부정 TOP10 ID ===")
print(top_negative)

# # =====================
# # 6. 보상 언급 추출
# # =====================
#
# def find_rewards(text):
#     return [r for r in reward_items if r in text]
#
# pdf["item_name"] = pdf["comment"].apply(find_rewards)
#
# mentioned = pdf[pdf["item_name"].str.len() > 0].explode("item_name")
#
# # =====================
# # 7. 보상별 감정 분석
# # =====================
#
# reward_counts = (
#     mentioned.groupby(["item_name", "sentiment"])
#     .size()
#     .reset_index(name="count")
# )
#
# total = mentioned.groupby("item_name").size().reset_index(name="total")
#
# ratio = reward_counts.merge(total, on="item_name")
# ratio["ratio"] = ratio["count"] / ratio["total"]
#
# print("\n=== 보상별 감정 분포 ===")
# print(reward_counts)
#
# print("\n=== 보상별 감정 비율 ===")
# print(ratio)

# =====================
# 8. 저장
# =====================

overall.to_csv("/data/output/overall_sentiment.csv", index=False)
top_positive.to_csv("/data/output/top_positive_sentiment.csv", index=False)
top_negative.to_csv("/data/output/top_negative_sentiment.csv", index=False)
# reward_counts.to_csv("/data/output/reward_sentiment_raw.csv", index=False)
# ratio.to_csv("/data/output/reward_sentiment_ratio.csv", index=False)

print("\n✅ 분석 완료")

spark.stop()