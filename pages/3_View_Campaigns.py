import streamlit as st
import pandas as pd
from models.campaign import Campaign
import os
from pathlib import Path
from models.ml_predictor import predict_success


# Set page configuration
st.set_page_config(
    page_title="OpenFunds - View Campaigns",
    page_icon="💰",
    layout="wide",
)

# Add simple CSS
st.markdown("""
<style>
    .stApp {
        background-color: #111133;
    }
    h1, h2, h3, h4, h5, p, li, div {
        color: white;
    }
    .stButton button {
        background-color: #7C4DFF;
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("View Fundraising Campaigns")
st.write("Browse all active fundraising campaigns and support the ones you like.")

# Function to get progress percentage
def get_progress(current, target):
    if target <= 0:
        return 0
    progress = (current / target) * 100
    return min(progress, 100)  # Cap at 100%

# Function to format BTC amount
def format_btc(amount):
    return f"{amount:.8f} BTC"

# Refresh button
if st.button("🔄 Refresh Campaigns"):
    st.experimental_rerun()

# Get all campaigns
campaigns = Campaign.get_all_campaigns()

if not campaigns:
    st.info("No campaigns found. Create a new campaign to get started!")
    if st.button("Create New Campaign"):
        st.switch_page("pages/2_Create_Campaign.py")
else:
    # Convert to list of dicts for easier handling
    campaign_list = []
    for campaign in campaigns:
        campaign_dict = dict(campaign)
        campaign_list.append(campaign_dict)
    
    # Show as a DataFrame first for overview
    df = pd.DataFrame(campaign_list)
    # Select and rename columns for display
    df_display = df[['id', 'title', 'owner_name', 'target_amount', 'current_amount', 'status']].copy()
    df_display.columns = ['ID', 'Campaign', 'Owner', 'Target (BTC)', 'Current (BTC)', 'Status']
    
    # Display the table
    st.subheader("All Campaigns")
    st.dataframe(df_display, use_container_width=True)
    
    # Filter functionality
    st.subheader("Filter Campaigns")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Active", "Funded", "Closed"],
            index=0
        )
    
    with filter_col2:
        sort_by = st.selectbox(
            "Sort By",
            options=["Newest", "Highest Funded", "Closest to Goal"],
            index=0
        )
    
    with filter_col3:
        search_term = st.text_input("Search", placeholder="Campaign title or owner...")
    
    # Apply filters
    filtered_campaigns = campaign_list.copy()
    
    if status_filter != "All":
        filtered_campaigns = [c for c in filtered_campaigns if c['status'] == status_filter]
    
    if search_term:
        search_term = search_term.lower()
        filtered_campaigns = [c for c in filtered_campaigns if search_term in c['title'].lower() or search_term in c['owner_name'].lower()]
    
    # Apply sorting
    if sort_by == "Newest":
        # Already sorted by created_at DESC from database
        pass
    elif sort_by == "Highest Funded":
        filtered_campaigns = sorted(filtered_campaigns, key=lambda x: x['current_amount'], reverse=True)
    elif sort_by == "Closest to Goal":
        filtered_campaigns = sorted(filtered_campaigns, key=lambda x: (x['current_amount'] / x['target_amount']) if x['target_amount'] > 0 else 0, reverse=True)
    
    # Display filtered results count
    st.write(f"Displaying {len(filtered_campaigns)} of {len(campaign_list)} campaigns")
    
    # Divider
    st.markdown("---")
    st.subheader("Campaign Details")
    
    # Create columns for displaying campaigns
    col1, col2 = st.columns(2)
    
    # Display each campaign in a card
    for i, campaign in enumerate(filtered_campaigns):
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            # Create a container for each campaign
            with st.container():
                st.markdown(f"### {campaign['title']}")
                
                # Status indicator
                status_color = "green" if campaign['status'] == "Active" else "blue" if campaign['status'] == "Funded" else "gray"
                st.markdown(f"**Status:** {campaign['status']}")
                
                # Campaign details
                st.markdown(f"**Owner:** {campaign['owner_name']}")
                st.markdown(f"**Description:** {campaign['description']}")
                # ML Prediction
                score, feedback = predict_success(
                        campaign['title'],
                        campaign['description'],
                        campaign['target_amount']
                           )
                st.markdown(f"🔮 **Predicted Success Likelihood:** {score * 100:.2f}%")
                st.markdown(f"💬 **AI Feedback:** {feedback}")
                st.markdown(f"**Bitcoin Address:** `{campaign['btc_address']}`")
                
                # Progress bar
                progress = get_progress(campaign['current_amount'], campaign['target_amount'])
                st.progress(progress / 100)
                
                # Amount display
                st.markdown(f"**{format_btc(campaign['current_amount'])}** of **{format_btc(campaign['target_amount'])}** ({progress:.1f}%)")
                
                # Donation and status controls
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Only allow donations for active campaigns
                    if campaign['status'] == 'Active':
                        # Create a unique key for each donation input
                        donation_key = f"donation_{campaign['id']}"
                        donation_amount = st.number_input(
                            "Donation Amount (BTC)", 
                            min_value=0.0001,
                            max_value=float(campaign['target_amount']),
                            value=0.01,
                            step=0.01,
                            key=donation_key
                        )
                        
                        # Create a unique key for each donate button
                        if st.button("Donate", key=f"donate_{campaign['id']}"):
                            success = Campaign.donate(campaign['id'], donation_amount)
                            if success:
                                st.success(f"Donated {format_btc(donation_amount)} successfully!")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to process donation. Please try again.")
                    else:
                        st.info("This campaign is not accepting donations")
                
                with col_b:
                    # Allow changing status for demo purposes
                    status_options = ["Active", "Funded", "Closed"]
                    new_status = st.selectbox(
                        "Status", 
                        options=status_options,
                        index=status_options.index(campaign['status']),
                        key=f"status_{campaign['id']}"
                    )
                    
                    # Update status if changed
                    if new_status != campaign['status']:
                        if st.button("Update Status", key=f"update_{campaign['id']}"):
                            success = Campaign.update_status(campaign['id'], new_status)
                            if success:
                                st.success(f"Status updated to {new_status}!")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update status. Please try again.")
                
                # Add a divider between campaigns
                st.markdown("---")

# Bottom section - show CSV export info
st.subheader("Campaign Data Export")
with st.expander("View CSV Data"):
    # Check if CSV file exists
    BASE_DIR = Path(__file__).parent.parent
    CSV_PATH = os.path.join(BASE_DIR, 'data_exports', 'campaigns.csv')
    
    if os.path.exists(CSV_PATH):
        st.write("All campaign data is automatically exported to CSV at:")
        st.code(CSV_PATH)
        
        # Show CSV data
        try:
            csv_data = pd.read_csv(CSV_PATH)
            st.dataframe(csv_data)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
    else:
        st.info("CSV export file will be created after campaigns are added.")

# Sidebar
st.sidebar.title("OpenFunds")
st.sidebar.markdown("💰 Decentralized Fundraising")

# Navigation
st.sidebar.subheader("Navigation")
if st.sidebar.button("🏠 Home"):
    st.switch_page("1_Home.py")
if st.sidebar.button("➕ Create Campaign"):
    st.switch_page("pages/2_Create_Campaign.py")
if st.sidebar.button("👁️ View Campaigns", disabled=True):
    pass

# Footer
st.markdown("---")
st.write("© 2025 OpenFunds - A Decentralized Fundraising Platform")