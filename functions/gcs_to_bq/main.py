import pathlib
from typing import Dict

import functions_framework
from google.cloud import bigquery

# Triggered by a change in a storage bucket.
@functions_framework.cloud_event
def save_gcs_file_to_bq(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    file_name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {file_name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    # Depending on the file name, identify the corresponding BQ table.
    if "tweets_score_hate" in file_name:
        bq_table = "tweets_score_hate"
    elif "tweets_score_irony" in file_name:
        bq_table = "tweets_score_irony"
    elif "tweets_score_offensive" in file_name:
        bq_table = "tweets_score_offensive"
    elif "users_score_hate" in file_name:
        bq_table = "users_score_hate"
    elif "users_score_irony" in file_name:
        bq_table = "users_score_irony"
    elif "users_score_offensive" in file_name:
        bq_table = "users_score_offensive"
    else:
        bq_table = "other"

    # TODO(ai): update BQ dataset name.
    # Set table_id to the ID of the table to create.
    table_id = f"fake-news-bears.staging.{bq_table}"

    # Construct a BigQuery client object.
    client = bigquery.Client()

    current_directory = pathlib.Path(__file__).parent
    schema_path = str(current_directory / f"schemas/{bq_table}.json")
    schema = client.schema_from_json(schema_path)

    # If the table already exists. then truncate and replace the data.
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=schema,
        skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
    )

    # Use a wildcard to concat multiple files in a bucket.
    uri = f"gs://{bucket}/{bq_table}/*"
    print(f"File change detected in GCS uri: {uri}...")

    # Load GCS files into a BQ table.
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    print("The GCS files were correctly loaded to BQ...")

    destination_table = client.get_table(table_id)  # Make an API request.
    print(f"Loaded {destination_table.num_rows} rows...")
