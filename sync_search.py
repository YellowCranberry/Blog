# sync_search.py
import os
from dev.core.engine import HybridSearchEngine 

# 1. Connect to the empty Search Engine (Postgres)
search_engine = HybridSearchEngine(
    db_url="postgresql+psycopg://postgres:1234@localhost:5433/vectordb"   
)

print("Starting the sync process...")

# 2. Pull data from your existing blog database (SQLite)
# IMPORTANT: Change 'sqlite:///blog.db' to the actual name of your SQLite file!
search_engine.ingest_from_db(
    source_db_url="sqlite:///user_data.sqlite", 
    table_name="blogs",           # Fixed: Matches your __tablename__
    content_col="description",    # Fixed: Matches your column name
    meta_cols=["id", "title", "slug"]  # Bonus: Added slug for easy URL routing!
)