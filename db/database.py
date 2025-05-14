import sqlite3
import os
import pandas as pd
from pathlib import Path

# Set the base directory to the parent of the current file
BASE_DIR = Path(__file__).parent.parent
DB_PATH = os.path.join(BASE_DIR, 'data', 'campaigns.db')
CSV_PATH = os.path.join(BASE_DIR, 'data_exports', 'campaigns.csv')

def ensure_dirs_exist():
    """Ensure the data and data_exports directories exist."""
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'data_exports'), exist_ok=True)

def get_db_connection():
    """Create a database connection and return the connection object."""
    ensure_dirs_exist()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database by creating necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create campaigns table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        btc_address TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0.0,
        owner_name TEXT NOT NULL,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize CSV export
    export_to_csv()

def add_campaign(title, description, btc_address, target_amount, owner_name):
    """Add a new campaign to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO campaigns (title, description, btc_address, target_amount, owner_name)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, description, btc_address, target_amount, owner_name))
    
    conn.commit()
    conn.close()
    
    # Export to CSV after adding a campaign
    export_to_csv()
    
    return True

def get_all_campaigns():
    """Retrieve all campaigns from the database."""
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM campaigns ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return campaigns

def get_campaign_by_id(campaign_id):
    """Retrieve a specific campaign by its ID."""
    conn = get_db_connection()
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    conn.close()
    
    return campaign

def update_campaign_status(campaign_id, status):
    """Update the status of a campaign."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE campaigns SET status = ? WHERE id = ?', (status, campaign_id))
    
    conn.commit()
    conn.close()
    
    # Export to CSV after updating campaign status
    export_to_csv()
    
    return True

def donate_to_campaign(campaign_id, amount):
    """Add a donation to a campaign and update its status if needed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current campaign info
    campaign = cursor.execute(
        'SELECT current_amount, target_amount FROM campaigns WHERE id = ?', 
        (campaign_id,)
    ).fetchone()
    
    if not campaign:
        conn.close()
        return False
    
    new_amount = campaign['current_amount'] + amount
    
    # Update current amount
    cursor.execute(
        'UPDATE campaigns SET current_amount = ? WHERE id = ?', 
        (new_amount, campaign_id)
    )
    
    # Check if campaign is now fully funded
    if new_amount >= campaign['target_amount']:
        cursor.execute(
            'UPDATE campaigns SET status = ? WHERE id = ?', 
            ('Funded', campaign_id)
        )
    
    conn.commit()
    conn.close()
    
    # Export to CSV after donation
    export_to_csv()
    
    return True

def export_to_csv():
    """Export all campaigns data to a CSV file."""
    conn = get_db_connection()
    
    # Check if there are any campaigns in the database
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'")
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Query all campaigns
    campaigns_df = pd.read_sql_query("SELECT * FROM campaigns", conn)
    conn.close()
    
    # Save to CSV
    ensure_dirs_exist()
    campaigns_df.to_csv(CSV_PATH, index=False)
    
    return True

# Initialize the database when this module is imported
init_db()