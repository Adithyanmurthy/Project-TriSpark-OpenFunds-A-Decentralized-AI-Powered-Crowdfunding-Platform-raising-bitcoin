import pandas as pd
import os
from pathlib import Path
from db.database import get_db_connection

def export_campaigns_to_csv():
    """
    Export all campaigns from SQLite database to a CSV file
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    # Set paths
    BASE_DIR = Path(__file__).parent.parent
    CSV_PATH = os.path.join(BASE_DIR, 'data_exports', 'campaigns.csv')
    
    # Ensure the data_exports directory exists
    os.makedirs(os.path.join(BASE_DIR, 'data_exports'), exist_ok=True)
    
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Check if campaigns table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'")
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Export all campaigns to DataFrame
        query = "SELECT * FROM campaigns"
        campaigns_df = pd.read_sql_query(query, conn)
        
        # Close connection
        conn.close()
        
        # Save to CSV
        campaigns_df.to_csv(CSV_PATH, index=False)
        
        print(f"Exported {len(campaigns_df)} campaigns to {CSV_PATH}")
        return True
        
    except Exception as e:
        print(f"Error exporting campaigns to CSV: {e}")
        return False