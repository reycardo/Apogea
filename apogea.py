import streamlit as st
from merchants import MerchantDatabase
import pandas as pd

# Initialize database
@st.cache_resource
def get_database():
    return MerchantDatabase()

db = get_database()

# Page config
st.set_page_config(
    page_title="Merchant Database",
    page_icon="🏪",
    layout="wide"
)

st.title("🏪 Merchant Trading Database")
st.markdown("Manage merchants, items, and find the best places to buy and sell!")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["🔍 Search Where to Sell", "💰 Find Item Prices", "➕ Add Merchant", 
     "📦 Add Item", "🏪 Set Merchant Inventory", "📊 View All Merchants"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
merchants = db.list_all_merchants()
st.sidebar.metric("Total Merchants", len(merchants))

# ========== SEARCH WHERE TO SELL ==========
if page == "🔍 Search Where to Sell":
    st.header("Find Where to Sell Your Items")
    st.markdown("Enter an item name to find which merchants will buy it and for how much.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        item_to_sell = st.text_input("Item Name:", placeholder="e.g., Cheese Wheel")
    
    if st.button("Search Buyers", type="primary"):
        if item_to_sell:
            results = db.where_to_sell(item_to_sell)
            
            if results:
                st.success(f"Found {len(results)} potential buyers for '{item_to_sell}'")
                
                # Display results in cards
                for result in results:
                    with st.expander(f"🏪 {result['merchant']} - {result['location']}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Buys Tag", result['buys_tag'])
                        with col2:
                            st.metric("Buy Rate", f"{result['multiplier']*100:.0f}%")
                        with col3:
                            if result['estimated_buy_price']:
                                st.metric("Est. Price", f"{result['estimated_buy_price']:.2f} gold")
                            else:
                                st.metric("Est. Price", "N/A")
                        
                        if result['base_price']:
                            st.info(f"💡 Base sell price: {result['base_price']:.2f} gold")
            else:
                st.warning(f"No buyers found for '{item_to_sell}'. The item may not exist or has no tags.")
        else:
            st.error("Please enter an item name")

# ========== FIND ITEM PRICES ==========
elif page == "💰 Find Item Prices":
    st.header("Find Best Prices for Items")
    st.markdown("Search for items to see which merchants sell them and compare prices.")
    
    item_search = st.text_input("Search Item:", placeholder="e.g., Health Potion")
    
    if st.button("Search Sellers", type="primary"):
        if item_search:
            results = db.search_item_price(item_search)
            
            if results:
                st.success(f"Found {len(results)} listings")
                
                # Create DataFrame for better display
                df = pd.DataFrame(results)
                df = df.rename(columns={
                    'merchant': 'Merchant',
                    'location': 'Location',
                    'item': 'Item',
                    'price': 'Price (gold)',
                    'stock': 'Stock'
                })
                
                # Highlight best price
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show best deal
                best_price = df.iloc[0]
                st.success(f"🏆 Best Price: {best_price['Merchant']} - {best_price['Price (gold)']} gold")
            else:
                st.warning(f"No sellers found for '{item_search}'")
        else:
            st.error("Please enter an item name to search")

# ========== ADD MERCHANT ==========
elif page == "➕ Add Merchant":
    st.header("Add New Merchant")
    
    with st.form("add_merchant_form"):
        merchant_name = st.text_input("Merchant Name*", placeholder="e.g., Blacksmith")
        merchant_location = st.text_input("Location", placeholder="e.g., Forge District")
        merchant_description = st.text_area("Description", placeholder="Optional description")
        
        submitted = st.form_submit_button("Add Merchant", type="primary")
        
        if submitted:
            if merchant_name:
                merchant_id = db.add_merchant(merchant_name, merchant_location, merchant_description)
                st.success(f"✅ Merchant '{merchant_name}' added successfully! (ID: {merchant_id})")
            else:
                st.error("Merchant name is required")
    
    st.markdown("---")
    st.subheader("Existing Merchants")
    merchants = db.list_all_merchants()
    if merchants:
        for merchant in merchants:
            with st.expander(f"🏪 {merchant['name']}"):
                st.write(f"**Location:** {merchant['location'] or 'Not specified'}")
                st.write(f"**Description:** {merchant['description'] or 'None'}")
    else:
        st.info("No merchants in database yet")

# ========== ADD ITEM ==========
elif page == "📦 Add Item":
    st.header("Add New Item")
    
    with st.form("add_item_form"):
        item_name = st.text_input("Item Name*", placeholder="e.g., Iron Sword")
        item_description = st.text_area("Description", placeholder="Optional description")
        item_tags = st.text_input("Tags (comma-separated)", placeholder="e.g., weapon, metal, melee")
        
        submitted = st.form_submit_button("Add Item", type="primary")
        
        if submitted:
            if item_name:
                tags_list = [tag.strip() for tag in item_tags.split(",")] if item_tags else []
                item_id = db.add_item(item_name, item_description, tags_list)
                st.success(f"✅ Item '{item_name}' added with tags: {', '.join(tags_list)}")
            else:
                st.error("Item name is required")

# ========== SET MERCHANT INVENTORY ==========
elif page == "🏪 Set Merchant Inventory":
    st.header("Manage Merchant Inventory")
    
    merchants = db.list_all_merchants()
    merchant_names = [m['name'] for m in merchants]
    
    tab1, tab2 = st.tabs(["💼 What Merchant Sells", "💰 What Merchant Buys"])
    
    with tab1:
        st.subheader("Add Items to Merchant's Inventory")
        
        with st.form("merchant_sells_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sell_merchant = st.selectbox("Select Merchant", merchant_names if merchant_names else ["No merchants"])
            with col2:
                sell_item = st.text_input("Item Name", placeholder="e.g., Health Potion")
            
            col3, col4 = st.columns(2)
            with col3:
                sell_price = st.number_input("Sell Price (gold)", min_value=0.0, value=50.0, step=0.5)
            with col4:
                sell_stock = st.number_input("Stock (-1 for unlimited)", value=-1, step=1)
            
            submitted = st.form_submit_button("Add to Inventory", type="primary")
            
            if submitted and merchant_names:
                if sell_item:
                    db.add_merchant_sells_item(sell_merchant, sell_item, sell_price, sell_stock)
                    st.success(f"✅ Added '{sell_item}' to {sell_merchant}'s inventory at {sell_price} gold")
                else:
                    st.error("Item name is required")
    
    with tab2:
        st.subheader("Set What Tags Merchant Buys")
        st.markdown("Define which item tags a merchant will purchase and at what percentage of value.")
        
        with st.form("merchant_buys_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                buy_merchant = st.selectbox("Select Merchant", merchant_names if merchant_names else ["No merchants"], key="buy_merchant")
            with col2:
                buy_tag = st.text_input("Item Tag", placeholder="e.g., weapon, food")
            
            buy_multiplier = st.slider("Buy Price (% of base value)", 0, 100, 50) / 100
            
            submitted = st.form_submit_button("Set Buy Preference", type="primary")
            
            if submitted and merchant_names:
                if buy_tag:
                    db.add_merchant_buys_tag(buy_merchant, buy_tag, buy_multiplier)
                    st.success(f"✅ {buy_merchant} now buys '{buy_tag}' items at {buy_multiplier*100}% of value")
                else:
                    st.error("Tag is required")

# ========== VIEW ALL MERCHANTS ==========
elif page == "📊 View All Merchants":
    st.header("All Merchants Overview")
    
    merchants = db.list_all_merchants()
    
    if not merchants:
        st.info("No merchants in database yet. Add some in the 'Add Merchant' page!")
    else:
        for merchant in merchants:
            with st.expander(f"🏪 {merchant['name']} - {merchant['location']}", expanded=False):
                st.markdown(f"**Description:** {merchant['description'] or 'None'}")
                
                inventory = db.get_merchant_inventory(merchant['name'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💼 Sells")
                    if inventory['sells']:
                        sells_df = pd.DataFrame(inventory['sells'])
                        st.dataframe(sells_df, hide_index=True, use_container_width=True)
                    else:
                        st.info("Not selling anything")
                
                with col2:
                    st.markdown("### 💰 Buys")
                    if inventory['buys_tags']:
                        buys_df = pd.DataFrame(inventory['buys_tags'])
                        buys_df['buy_price_multiplier'] = buys_df['buy_price_multiplier'].apply(lambda x: f"{x*100:.0f}%")
                        st.dataframe(buys_df, hide_index=True, use_container_width=True)
                    else:
                        st.info("Not buying anything")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Instructions")
st.sidebar.markdown("""
1. **Add merchants** and **items** first
2. **Set inventory** - what they sell
3. **Set buy tags** - what they buy
4. **Search** to find best deals!
""")
