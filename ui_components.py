import streamlit as st
import pandas as pd
import os
import base64
from database import add_merchant, get_all_merchants, add_item, get_all_items


def save_uploaded_image(uploaded_file, item_name):
    """Save uploaded image and return the filename"""
    if uploaded_file is None:
        return ""
    
    # Create icons directory if it doesn't exist
    os.makedirs("icons", exist_ok=True)
    
    # Create safe filename
    safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{safe_name}{ext}"
    filepath = os.path.join("icons", filename)
    
    # Save file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filename


def render_add_merchant_form():
    """Render the form to add a new merchant"""
    st.header("➕ Add Merchant")
    
    with st.form("add_merchant_form", clear_on_submit=True):
        merchant_name = st.text_input("Merchant Name", placeholder="e.g., Erastus")
        
        st.subheader("What Merchant Buys (Tags)")
        buy_input = st.text_area(
            "Buy Tags (one per line)", 
            placeholder="Distance Weapons\nLight Helmets\nRed Spellbooks",
            height=150
        )
        
        st.subheader("What Merchant Sells")
        st.markdown("Enter items as: `Item Name, Price` (one per line)")
        sell_input = st.text_area(
            "Sell Items", 
            placeholder="Arrow, 1\nWooden Bow, 65",
            height=150
        )
        
        submitted = st.form_submit_button("Add Merchant", type="primary", use_container_width=True)
        
        if submitted:
            if not merchant_name:
                st.error("Please enter a merchant name")
            else:
                # Parse buy tags
                buy_tags = [tag.strip() for tag in buy_input.split('\n') if tag.strip()]
                
                # Parse sell items
                sell_items = []
                if sell_input.strip():
                    for line in sell_input.split('\n'):
                        if ',' in line:
                            parts = line.split(',')
                            if len(parts) >= 2:
                                item_name = parts[0].strip()
                                try:
                                    price = float(parts[1].strip())
                                    sell_items.append([item_name, price])
                                except ValueError:
                                    st.warning(f"Skipped invalid price for: {line}")
                
                # Add to database
                success = add_merchant(merchant_name, buy_tags, sell_items)
                
                if success:
                    st.success(f"✅ Merchant '{merchant_name}' added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Merchant '{merchant_name}' already exists")


def render_merchants_list():
    """Render the list of all merchants"""
    st.header("📋 All Merchants")
    
    merchants = get_all_merchants()
    
    if not merchants:
        st.info("No merchants in database yet. Add one to get started!")
    else:
        for merchant in merchants:
            with st.expander(f"🏪 {merchant['name']}", expanded=False):
                
                # Display Buy tags
                st.subheader("💰 Buys")
                if merchant['buy']:
                    for tag in merchant['buy']:
                        st.markdown(f"- {tag}")
                else:
                    st.text("Nothing")
                
                st.markdown("---")
                
                # Display Sell items
                st.subheader("💼 Sells")
                if merchant['sell']:
                    df = pd.DataFrame(merchant['sell'], columns=['Item', 'Price'])
                    df['Price'] = df['Price'].apply(lambda x: f"{int(x)}")
                    st.dataframe(df, hide_index=True, use_container_width=True)
                else:
                    st.text("Nothing")


def render_add_item_form():
    """Render the form to add a new item"""
    st.header("➕ Add Item")
    
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name", placeholder="e.g., Iron Sword")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight", min_value=0.0, value=1.0, step=0.1)
        
        with col2:
            tag = st.text_input("Tag/Category", placeholder="e.g., Weapon")
        
        st.subheader("Icon")
        icon_type = st.radio("Choose icon type:", ["Emoji/Text", "Upload Image"], horizontal=True)
        
        if icon_type == "Emoji/Text":
            icon = st.text_input("Icon", placeholder="e.g., ⚔️", max_chars=10)
            uploaded_file = None
        else:
            icon = ""
            uploaded_file = st.file_uploader("Upload icon image", type=["jpg", "jpeg", "png", "gif"], help="You can paste images from clipboard after clicking 'Browse files'")
        
        submitted = st.form_submit_button("Add Item", type="primary", use_container_width=True)
        
        if submitted:
            if not item_name:
                st.error("Please enter an item name")
            elif not tag:
                st.error("Please enter a tag")
            else:
                # Handle image upload if provided
                if uploaded_file:
                    icon = save_uploaded_image(uploaded_file, item_name)
                
                success = add_item(item_name, weight, tag, icon)
                
                if success:
                    st.success(f"✅ Item '{item_name}' added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Item '{item_name}' already exists")


def render_items_list():
    """Render the list of all items"""
    st.header("📦 All Items")
    
    items = get_all_items()
    
    if not items:
        st.info("No items in database yet. Add one to get started!")
    else:
        for item in items:
            with st.expander(f"{item['icon'] if len(item['icon']) < 10 else ''} {item['name']}", expanded=False):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Display image if it's a file path
                    if item['icon'] and len(item['icon']) > 10 and os.path.exists(os.path.join("icons", item['icon'])):
                        st.image(os.path.join("icons", item['icon']), width=100)
                    elif item['icon']:
                        st.markdown(f"### {item['icon']}")
                
                with col2:
                    st.markdown(f"**Weight:** {item['weight']}")
                    st.markdown(f"**Tag:** {item['tag']}")
