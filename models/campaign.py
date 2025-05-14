from db.database import (
    add_campaign as db_add_campaign,
    get_all_campaigns as db_get_all_campaigns,
    get_campaign_by_id as db_get_campaign_by_id,
    update_campaign_status as db_update_campaign_status,
    donate_to_campaign as db_donate_to_campaign
)

class Campaign:
    """
    Campaign model class to handle campaign-related operations
    and provide an interface between the UI and database
    """
    
    @staticmethod
    def create_campaign(title, description, btc_address, target_amount, owner_name):
        """
        Create a new fundraising campaign
        
        Args:
            title (str): Campaign title
            description (str): Campaign description
            btc_address (str): Bitcoin address for donations
            target_amount (float): Target amount in BTC
            owner_name (str): Name of the campaign owner
            
        Returns:
            bool: True if successful
        """
        return db_add_campaign(title, description, btc_address, target_amount, owner_name)
    
    @staticmethod
    def get_all_campaigns():
        """
        Get all campaigns from the database
        
        Returns:
            list: List of all campaigns
        """
        return db_get_all_campaigns()
    
    @staticmethod
    def get_campaign(campaign_id):
        """
        Get a specific campaign by ID
        
        Args:
            campaign_id (int): ID of the campaign to retrieve
            
        Returns:
            dict: Campaign data
        """
        return db_get_campaign_by_id(campaign_id)
    
    @staticmethod
    def update_status(campaign_id, status):
        """
        Update the status of a campaign
        
        Args:
            campaign_id (int): ID of the campaign to update
            status (str): New status ('Active', 'Funded', or 'Closed')
            
        Returns:
            bool: True if successful
        """
        return db_update_campaign_status(campaign_id, status)
    
    @staticmethod
    def donate(campaign_id, amount):
        """
        Add a donation to a campaign
        
        Args:
            campaign_id (int): ID of the campaign to donate to
            amount (float): Amount to donate in BTC
            
        Returns:
            bool: True if successful
        """
        return db_donate_to_campaign(campaign_id, amount)