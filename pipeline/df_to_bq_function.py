# Access BQ client credentials.
BQ = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
print("BigQuery Client Connection... opened")

# TODO(rc): add if/then logic depending on the df (users vs tweets).
BQ_TABLE = "tweets_something"


def append_df_to_bq(df: pd.DataFrame(), bq_table: str):
    """After merging user/tweets tables into a single DF, load that DF into the specified BQ table."""
    print(f"Appending {len(df)} results to {bq_table}...")

    try:
        # WRITE_TRUNCATE: If the table already exists, BQ overwrites the table data and uses the schema from the load.
        # WRITE_APPEND: If the table already exists, BQ appends the data to the table.
        job = BQ.load_table_from_dataframe(
            df, bq_table, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"),
        )
        print(job.result())

    except Exception as e:
        print(f"WARNING: Handling error during BQ upload - {e}")

    print(f"Job Completed.")
