import os
import sys
import uuid
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.snowflake_connection import get_connection
from snowflake.connector.pandas_tools import write_pandas

DATA_FILES = {
    "RAW_STUDENTS": "data/placement_students.csv",
    "RAW_COLLEGES": "data/placement_colleges.csv",
    "RAW_COMPANIES": "data/placement_companies.csv",
    "RAW_OFFERS":    "data/placement_offers.csv",
}

def log_audit(conn, batch_id, file_name, entity, row_count, status, error_msg=None):
    cur = conn.cursor()
    sql = """
        INSERT INTO PLACEMENT_DB.OPS.LOAD_AUDIT 
        (BATCH_ID, FILE_NAME, ENTITY, LOAD_TS, ROW_COUNT, STATUS, ERROR_MSG)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP(), %s, %s, %s)
    """
    cur.execute(sql, (batch_id, file_name, entity, row_count, status, error_msg))
    cur.close()

def main():
    batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Starting Bronze Load - Batch ID: {batch_id}")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Ensure BRONZE schema is used
    cur.execute("USE DATABASE PLACEMENT_DB")
    cur.execute("USE SCHEMA BRONZE")

    for entity, relative_path in DATA_FILES.items():
        file_path = os.path.abspath(relative_path)
        file_name = os.path.basename(file_path)
        print(f"\nProcessing {entity} from {file_name}...")
        
        try:
            df = pd.read_csv(file_path)
            
            # Add Ingestion Metadata Columns
            df["LOAD_TS"] = datetime.now()
            df["FILE_NAME"] = file_name
            df["ROW_NUMBER"] = range(1, len(df) + 1)
            df["BATCH_ID"] = batch_id
            
            # Convert column names to UPPERCASE for Snowflake compatibility
            df.columns = [c.upper() for c in df.columns]
            
            # Write to Snowflake BRONZE schema
            success, nchunks, nrows, _ = write_pandas(
                conn=conn,
                df=df,
                table_name=entity,
                schema="BRONZE",
                auto_create_table=True,
                overwrite=True
            )
            
            if success:
                print(f"  [SUCCESS] Loaded {nrows} rows into BRONZE.{entity}")
                log_audit(conn, batch_id, file_name, entity, nrows, "SUCCESS")
            else:
                print(f"  [FAILED] Could not load {entity}")
                log_audit(conn, batch_id, file_name, entity, 0, "FAILURE", "write_pandas returned False")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            log_audit(conn, batch_id, file_name, entity, 0, "FAILURE", str(e))
            
    cur.close()
    conn.close()
    print("\nPhase 5 - Bronze ingestion complete!")

if __name__ == "__main__":
    main()
