import streamlit as st
import os
import pandas as pd
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set page configuration
st.set_page_config(
    page_title="OpenFunds - Debug Similarity",
    page_icon="🔍",
    layout="wide",
)

st.title("Similar Campaigns Debug Tool")
st.write("This tool will help diagnose why similar campaigns aren't showing in your app.")

# Step 1: Check imports
st.header("Step 1: Check Module Imports")
try:
    from sentence_transformers import SentenceTransformer, util
    st.success("✅ Successfully imported sentence_transformers")
except ImportError as e:
    st.error(f"❌ Failed to import sentence_transformers: {e}")
    st.info("Run: pip install sentence-transformers")
    
# Step 2: Check if model can be loaded
st.header("Step 2: Check Model Loading")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    st.success("✅ Successfully loaded the model")
except Exception as e:
    st.error(f"❌ Failed to load model: {e}")

# Step 3: Check for campaigns.csv
st.header("Step 3: Check Campaigns Data")
csv_path = "data_exports/campaigns.csv"
if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path)
        st.success(f"✅ Found campaigns.csv with {len(df)} campaigns")
        
        # Display sample data
        st.subheader("Sample Campaign Data:")
        st.dataframe(df.head(3)[['title', 'description']])
    except Exception as e:
        st.error(f"❌ Error reading campaigns.csv: {e}")
else:
    st.error(f"❌ campaigns.csv not found at {csv_path}")
    
# Step 4: Test similarity function
st.header("Step 4: Test Similarity Function")

# Input fields to test
col1, col2 = st.columns(2)
with col1:
    test_title = st.text_input("Test Title", value="Books for remote colleges and schools")
with col2:
    test_description = st.text_input("Test Description", value="Help us raise funds to donate learning materials to underfunded schools and colleges in remote areas.")

if st.button("Test Similarity"):
    if not os.path.exists(csv_path):
        st.error("Cannot test similarity: campaigns.csv doesn't exist")
    else:
        # Load the get_similar_campaigns function
        try:
            from models.dl_similarity import get_similar_campaigns
            st.success("✅ Successfully imported get_similar_campaigns")
            
            # Test the function with provided inputs
            st.info("Running similarity check...")
            
            try:
                similar = get_similar_campaigns(test_title, test_description)
                
                if similar:
                    st.success(f"✅ Found {len(similar)} similar campaigns!")
                    
                    # Display results
                    for i, sim in enumerate(similar):
                        st.markdown(f"""
                        <div style='background-color:rgba(0,100,0,0.1);padding:10px;border-radius:5px;margin-bottom:10px'>
                            <strong>{sim['title']}</strong> - {sim['score']*100:.2f}% match<br/>
                            {sim['description'][:200]}...
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No similar campaigns found. This could be normal if there are no similar campaigns.")
                    
            except Exception as e:
                st.error(f"❌ Error running get_similar_campaigns: {e}")
                st.error(f"Error type: {type(e).__name__}")
                import traceback
                st.code(traceback.format_exc(), language="python")
                
        except ImportError as e:
            st.error(f"❌ Failed to import get_similar_campaigns: {e}")

# Step 5: Check the application code
st.header("Step 5: Debug our Streamlit App")

st.code("""
# This is the section that should show similar campaigns
if title and description and len(title.strip()) > 3 and len(description.strip()) > 10:
    # Get list of existing campaigns
    csv_path = "data_exports/campaigns.csv"
    if os.path.exists(csv_path):
        try:
            # Only do the similarity check if we have campaigns
            df = pd.read_csv(csv_path)
            if not df.empty:
                with st.spinner("Checking for similar campaigns..."):
                    similar_campaigns = get_similar_campaigns(title, description)
                
                if similar_campaigns and len(similar_campaigns) > 0:
                    st.subheader("🔍 Similar Campaigns You Might Want to Review")
                    for sim in similar_campaigns:
                        st.markdown(f'''
                        <div class="similar-campaign">
                            <strong>{sim['title']}</strong> – <em>{sim['score'] * 100:.2f}% match</em><br/>
                            {sim['description'][:250]}...
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    # Add warning to help user understand
                    st.warning("Please review these similar campaigns before creating yours to avoid duplication.")
        except Exception as e:
            # Silent error in production
            pass
""", language="python")

st.info("""
➡️ Key things to check:
1. Are the title and description fields meeting the minimum length requirements?
2. Is the campaigns.csv file found?
3. Are there campaigns in the CSV file?
4. Is the similarity function running without errors?
5. Is anything returned by the similarity function?
""")

# Get Python path and environment info
st.header("Step 6: Environment Information")
st.subheader("Python Path:")
st.code("\n".join(sys.path))

st.subheader("Python Version:")
st.code(sys.version)

st.subheader("Working Directory:")
st.code(os.getcwd())

st.subheader("Directory Contents:")
try:
    st.code("\n".join(os.listdir()))
except:
    st.error("Could not list directory contents")

# Check models directory
st.subheader("Models Directory Contents:")
try:
    models_path = os.path.join(os.getcwd(), "models")
    if os.path.exists(models_path):
        st.code("\n".join(os.listdir(models_path)))
    else:
        st.error("Models directory not found")
except:
    st.error("Could not list models directory contents")