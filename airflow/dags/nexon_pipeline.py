from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "nexon",
    "start_date": datetime(2025, 1, 1),
    "retries": 1
}

with DAG(
    dag_id="scraping_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    scrape_news = BashOperator(
        task_id="scrape_news",
        bash_command="python /opt/project/scraping/nexon_news_scraping.py"
    )

    scrape_rewards = BashOperator(
        task_id="scrape_rewards",
        bash_command="python /opt/project/scraping/nexon_reward_scraping.py"
    )

    scrape_inven_posts = BashOperator(
        task_id="scrape_inven_posts",
        bash_command="python /opt/project/scraping/inven_post_scraping.py"
    )

    scrape_inven_comments = BashOperator(
        task_id="scrape_inven_comments",
        bash_command="python /opt/project/scraping/inven_comment_scraping.py"
    )

    scrape_dc_posts = BashOperator(
        task_id="scrape_dc_posts",
        bash_command="python /opt/project/scraping/dc_post_scraping.py"
    )

    scrape_dc_comments = BashOperator(
        task_id="scrape_dc_comments",
        bash_command="python /opt/project/scraping/dc_comment_scraping.py"
    )


    scrape_news >> scrape_inven_posts >> scrape_inven_comments \
                >> scrape_dc_posts >> scrape_dc_comments
