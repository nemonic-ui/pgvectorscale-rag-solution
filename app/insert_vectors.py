from datetime import datetime

import pandas as pd
from cook.postgres.app.database.vector_store import VectorStore
from timescale_vector.client import uuid_from_time

# Initialize VectorStore
vec = VectorStore()

# Read the CSV file
df = pd.read_csv("/home/debian/pgvector/cook/postgres/data/servers.csv", sep=",", encoding="utf-8")
df.columns = df.columns.str.strip()
print(df.columns)


# Prepare data for insertion
def prepare_record(row):
    """Prepare a record for insertion into the vector store.

    This function creates a record with a UUID version 1 as the ID, which captures
    the current time or a specified time.

    Note:
        - By default, this function uses the current time for the UUID.
        - To use a specific time:
          1. Import the datetime module.
          2. Create a datetime object for your desired time.
          3. Use uuid_from_time(your_datetime) instead of uuid_from_time(datetime.now()).

        Example:
            from datetime import datetime
            specific_time = datetime(2023, 1, 1, 12, 0, 0)
            id = str(uuid_from_time(specific_time))

        This is useful when your content already has an associated datetime.
    """
    content = f"Facility: {row['Facility']}\nFunction: {row['Function']}\nName: {row['Name']}\nIP Address: {row['IP Address']}\nOperating System: {row['Operating System']}\nMake/Model: {row['Make/Model']}\nAsset Tag: {row['Asset Tag']}\nSerial: {row['Serial']}\nNotes: {row['Notes']}"
    
    embedding = vec.get_embedding(content)
    return pd.Series(
        {
            "id": str(uuid_from_time(datetime.now())),
            "metadata": {
                "category": "Server Data",
                "created_at": datetime.now().isoformat(),
            },
            "contents": content,
            "embedding": embedding,
        }
    )


records_df = df.apply(prepare_record, axis=1)

# Create tables and insert data
vec.create_tables()
vec.create_index()  # DiskAnnIndex
vec.upsert(records_df)
