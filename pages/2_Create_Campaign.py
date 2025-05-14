import streamlit as st
from models.campaign import Campaign
import re
import os
import pandas as pd
import time

# Set page configuration
st.set_page_config(
    page_title="OpenFunds - Create Campaign",
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
    /* Style for similar campaigns section */
    .similar-campaign {
        background-color: rgba(124, 77, 255, 0.1);
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to validate BTC address format (simplified for testnet)
def is_valid_btc_address(address):
    # This is a simplified check for testnet addresses
    pattern = re.compile(r'^[123][a-km-zA-HJ-NP-Z1-9]{25,34}$')
    return bool(pattern.match(address))

# Custom function to check for similar campaigns
def find_similar_campaigns(title, description):
    try:
        from models.dl_similarity import get_similar_campaigns
        similar = get_similar_campaigns(title, description)
        return similar
    except Exception as e:
        print(f"Error in similarity check: {e}")
        return []

# Initialize session state if not already done
if "step" not in st.session_state:
    st.session_state.step = 1
if "title" not in st.session_state:
    st.session_state.title = ""
if "description" not in st.session_state:
    st.session_state.description = ""
if "btc_address" not in st.session_state:
    st.session_state.btc_address = ""
if "target_amount" not in st.session_state:
    st.session_state.target_amount = 1.0
if "owner_name" not in st.session_state:
    st.session_state.owner_name = ""

# Title
st.title("Create a New Fundraising Campaign")
st.write("Fill out the form below to create a new fundraising campaign. All campaigns are stored locally and can be viewed on the 'View Campaigns' page.")

# Display campaign form inputs
st.subheader("Campaign Details")

# Simple form - no st.form wrapper
title = st.text_input("Campaign Title", value=st.session_state.title)
st.session_state.title = title

description = st.text_area("Campaign Description", value=st.session_state.description, height=150)
st.session_state.description = description

col1, col2 = st.columns(2)
with col1:
    btc_address = st.text_input("Bitcoin Address (Testnet)", value=st.session_state.btc_address)
    st.session_state.btc_address = btc_address
with col2:
    target_amount = st.number_input("Target Amount (BTC)", min_value=0.001, value=st.session_state.target_amount, step=0.1)
    st.session_state.target_amount = target_amount

owner_name = st.text_input("Campaign Owner", value=st.session_state.owner_name)
st.session_state.owner_name = owner_name

# Buttons
col1, col2 = st.columns(2)
with col1:
    check_similar = st.button("Check for Similar Campaigns")
with col2:
    create_campaign = st.button("Create Campaign")

# Show similar campaigns
if check_similar:
    if not title or not description:
        st.warning("Please enter a title and description first")
    elif len(title.strip()) <= 3 or len(description.strip()) <= 10:
        st.warning("Title should be at least 4 characters and description at least 11 characters")
    else:
        with st.spinner("Searching for similar campaigns..."):
            similar_campaigns = find_similar_campaigns(title, description)
            
            if similar_campaigns and len(similar_campaigns) > 0:
                st.subheader("Similar Campaigns You Might Want to Review")
                for sim in similar_campaigns:
                    st.markdown(f"""
                    <div class="similar-campaign">
                        <strong>{sim['title']}</strong> – <em>{sim['score'] * 100:.2f}% match</em><br/>
                        {sim['description'][:250]}...
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add warning to help user understand
                st.warning("Please review these similar campaigns before creating yours to avoid duplication.")
            else:
                st.info("No similar campaigns found for your title and description")

# Create campaign
if create_campaign:
    # Validation
    if not title:
        st.error("Campaign title is required.")
    elif not description:
        st.error("Campaign description is required.")
    elif not btc_address:
        st.error("Bitcoin address is required.")
    elif not is_valid_btc_address(btc_address):
        st.error("Please enter a valid Bitcoin address format.")
    elif target_amount <= 0:
        st.error("Target amount must be greater than 0.")
    elif not owner_name:
        st.error("Campaign owner name is required.")
    else:
        # Create campaign if all fields are valid
        with st.spinner("Creating campaign..."):
            # Create data directory if it doesn't exist
            os.makedirs("data_exports", exist_ok=True)
            
            # Create campaign
            success = Campaign.create_campaign(
                title=title,
                description=description,
                btc_address=btc_address,
                target_amount=float(target_amount),
                owner_name=owner_name
            )

        if success:
            st.success("Campaign created successfully! ")

            # Train model and update embeddings
            with st.spinner("Updating ML models..."):
                try:
                    from models.ml_predictor import train_model
                    from models.dl_similarity import update_embeddings
                    train_model()
                    update_embeddings()
                except Exception as e:
                    st.error(f"Could not update models: {str(e)}")
            
            # Predict campaign success
            try:
                from models.ml_predictor import predict_success
                success_score, suggestion = predict_success(title, description, target_amount)
                st.success(f"Predicted Success Likelihood: {success_score * 100:.2f}%")
                st.markdown(f"**Feedback:** {suggestion}")
            except Exception as e:
                st.error(f"Could not predict success: {str(e)}")

            if st.button("View All Campaigns"):
                st.switch_page("pages/3_View_Campaigns.py")
        else:
            st.error("An error occurred while creating the campaign. Please try again.")

# Debug info (hidden by default)
with st.expander("Info", expanded=False):
    st.write("Current session state values:")
    st.json({
        "title": st.session_state.title,
        "description": st.session_state.description,
        "btc_address": st.session_state.btc_address,
        "target_amount": st.session_state.target_amount,
        "owner_name": st.session_state.owner_name
    })
    
    # Check for campaigns.csv
    csv_path = "data_exports/campaigns.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            st.write(f"Found campaigns.csv with {len(df)} rows")
            if not df.empty:
                st.dataframe(df[['title', 'description']].head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.warning("campaigns.csv not found")

# Tips section
st.subheader("Tips for a Successful Campaign")
with st.expander("See Tips"):
    st.markdown("### How to Create a Successful Fundraising Campaign")
    
    st.markdown("**1. Choose a Clear Title**")
    st.write("Your title should be concise and describe what you're raising funds for.")
    
    st.markdown("**2. Write a Compelling Description**")
    st.write("Explain why your campaign matters and how the funds will be used.")
    
    st.markdown("**3. Set a Realistic Goal**")
    st.write("Choose a target amount that makes sense for your needs.")
    
    st.markdown("**4. Share Your Campaign**")
    st.write("Promote your campaign through social media and personal networks.")
    
    st.markdown("**5. Be Transparent**")
    st.write("Keep supporters updated on your progress and how funds are being used.")

# Example campaign
st.subheader("Example Campaign")
with st.expander("See Example"):
    st.markdown("### Community Garden Restoration Project")
    
    st.markdown("**Title:** Community Garden Restoration Project")
    
    st.markdown("**Description:** Our neighborhood garden needs restoration after recent storm damage. Funds will go toward new plants, soil, and irrigation equipment to make our shared space beautiful again.")
    
    st.markdown("**Target Amount:** 0.5 BTC")
    
    st.markdown("**Campaign Owner:** Jane Smith, Garden Committee")
    
    st.markdown("**Bitcoin Address:** 2N7DoD1edbhWw1Z1rN7HbpvzjPvF9LKjPbE")

# Sidebar
st.sidebar.title("OpenFunds")
st.sidebar.markdown("💰 Decentralized Fundraising")

# Navigation
st.sidebar.subheader("Navigation")
if st.sidebar.button("🏠 Home"):
    st.switch_page("1_Home.py")
if st.sidebar.button("➕ Create Campaign", disabled=True):
    pass
if st.sidebar.button("👁️ View Campaigns"):
    st.switch_page("pages/3_View_Campaigns.py")

# Footer
st.markdown("---")
st.write("© 2025 OpenFunds - A Decentralized Fundraising Platform")