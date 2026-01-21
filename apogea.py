import streamlit as st
from database import initialize_database
from ui_components import (
    render_add_merchant_form,
    render_merchants_list,
    render_add_item_form,
    render_items_list,
    render_merchants_selling_item_tab
)

# Initialize database on first run
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = True
    initialize_database()

# Streamlit UI
st.set_page_config(page_title="Merchant Database", page_icon="🏪", layout="wide")

st.title("🏪 Merchant Database")
st.markdown("Add merchants and track what they buy and sell")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📦 Items", "🏪 Merchants", "🔎 Who Sells?"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        render_add_item_form()
    with col2:
        render_items_list()

with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        render_add_merchant_form()
    with col2:
        render_merchants_list()

with tab3:
    render_merchants_selling_item_tab()