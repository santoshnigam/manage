import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("https://uxsgnyakxvbslsxuujup.supabase.co")
SUPABASE_KEY = os.getenv("sb_secret_yX_7M4BIzSPL3NYs4Y62wQ_Qz7_GRwG")

# Check credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase URL or Key is missing in .env file")
    st.stop()

# Connect Supabase
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("Supabase + Streamlit App")

# Insert data
name = st.text_input("Enter your name")
email = st.text_input("Enter your email")

if st.button("Save"):
    if name and email:
        try:
            data = {
                "name": name,
                "email": email
            }

            response = supabase.table("students").insert(data).execute()

            st.success("Data saved successfully!")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter name and email")

# Read data
st.subheader("Student Records")

try:
    response = supabase.table("students").select("*").execute()

    if response.data:
        st.dataframe(response.data)
    else:
        st.info("No records found.")

except Exception as e:
    st.error(f"Error loading data: {e}")