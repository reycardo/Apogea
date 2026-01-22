import streamlit as st
import pandas as pd
import os
from database import (
    add_merchant, get_all_merchants, add_item, get_all_items, 
    delete_item, get_all_tags, add_location, get_all_locations
)


def render_add_merchant_form():
    """Render the form to add a new merchant"""
    st.header("➕ Add Merchant")
    
    items = get_all_items()
    item_names = [item['name'] for item in items]
    tags = get_all_tags()
    locations = get_all_locations()
    
    # Initialize form counter in session state
    if 'merchant_form_key' not in st.session_state:
        st.session_state.merchant_form_key = 0

    with st.form(f"add_merchant_form_{st.session_state.merchant_form_key}", clear_on_submit=True):
        merchant_name = st.text_input("Merchant Name", placeholder="e.g., Erastus")
        
        # Location dropdown with option to add new
        location_options = ["<Add new location>"] + sorted(locations)
        location_option = st.selectbox(
            "Location",
            options=location_options,
            index=0,
            key=f"location_selector_{st.session_state.merchant_form_key}"
        )
        
        if location_option == "<Add new location>":
            merchant_location = st.text_input("Enter New Location", placeholder="e.g., Magnimar, Old Town", key=f"new_location_input_{st.session_state.merchant_form_key}")
        else:
            merchant_location = location_option
        
        st.subheader("What Merchant Buys (Tags)")
        buy_tags = st.multiselect(
            "Select Tags the Merchant Buys",
            options=tags,
            key=f"buy_tags_{st.session_state.merchant_form_key}"
        )
        new_tag = st.text_input("Or add a new tag for buying (optional)", key=f"new_tag_{st.session_state.merchant_form_key}")
        if new_tag and new_tag not in buy_tags:
            buy_tags.append(new_tag)
        
        st.subheader("What Merchant Sells")
        st.markdown("Select items and set prices.")

        sell_items = []
        selected_items = st.multiselect(
            "Select Items to Sell",
            options=item_names,
            key=f"selected_items_{st.session_state.merchant_form_key}"
        )
        
        # Display price inputs for each selected item
        if selected_items:
            st.markdown("**Set Prices:**")
            for item in selected_items:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.text(item)
                with col2:
                    price = st.number_input(
                        "Price",
                        min_value=0.0,
                        value=1.0,
                        step=1.0,
                        key=f"price_{item}_{st.session_state.merchant_form_key}",
                        label_visibility="collapsed"
                    )
                sell_items.append([item, price])

        submitted = st.form_submit_button("Add Merchant", type="primary", width='stretch')
        
        if submitted:
            if not merchant_name:
                st.error("Please enter a merchant name")
            elif not merchant_location:
                st.error("Please enter a merchant location")
            else:
                # Remove empty tags and duplicates
                buy_tags_clean = list({tag.strip() for tag in buy_tags if tag.strip()})
                
                # Add location to database if it's new
                if location_option == "<Add new location>":
                    add_location(merchant_location)
                
                # Add to database
                success = add_merchant(merchant_name, merchant_location, buy_tags_clean, sell_items)
                
                if success:
                    st.success(f"✅ Merchant '{merchant_name}' added successfully!")
                    # Increment form key to reset the form
                    st.session_state.merchant_form_key += 1
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
                # Display Location
                if merchant.get('location'):
                    st.markdown(f"**📍 Location:** {merchant['location']}")
                    st.markdown("---")
                
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
                    st.dataframe(df, hide_index=True, width='stretch')
                else:
                    st.text("Nothing")
                
                # Delete merchant button
                if st.button(f"🗑️ Delete '{merchant['name']}'", key=f"delete_merchant_{merchant['name']}"):
                    from database import delete_merchant
                    if delete_merchant(merchant['name']):
                        st.success(f"Deleted merchant '{merchant['name']}'")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete merchant '{merchant['name']}'")

def render_add_item_form():
    """Render the form to add a new item"""
    st.header("➕ Add Item")
    
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name", placeholder="e.g., Iron Sword")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight", min_value=0.0, value=1.0, step=0.1)
        
        with col2:
            tags = get_all_tags()
            # Always show existing tags first in dropdown
            tag_options = ["<Create new tag>"] + sorted(tags)
            tag_option = st.selectbox(
                "Tag/Category",
                options=tag_options,
                index=0,
                key="tag_selector"
            )
            
            # Only show text input when creating new tag
            if tag_option == "<Create new tag>":
                tag = st.text_input("Enter New Tag", placeholder="e.g., Weapon", key="new_tag_input")
            else:
                tag = tag_option
        
        submitted = st.form_submit_button("Add Item", type="primary", width='stretch')
        
        if submitted:
            if not item_name:
                st.error("Please enter an item name")
            elif not tag:
                st.error("Please enter a tag")
            else:
                success = add_item(item_name, weight, tag)
                
                if success:
                    st.success(f"✅ Item '{item_name}' added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Item '{item_name}' already exists")


def render_items_list():
    """Render the list of all items, grouped by tag"""
    st.header("📦 All Items")
    
    items = get_all_items()
    
    if not items:
        st.info("No items in database yet. Add one to get started!")
    else:
        # Group items by tag
        from collections import defaultdict
        items_by_tag = defaultdict(list)
        for item in items:
            items_by_tag[item['tag']].append(item)
        
        # Sort tags alphabetically
        for tag in sorted(items_by_tag.keys()):
            st.subheader(f"🏷️ {tag}")
            for item in items_by_tag[tag]:
                with st.expander(f"{item['name']}", expanded=False):
                    col1, col2 = st.columns([2, 5])
                    with col1:
                        st.markdown(f"**Weight:** {item['weight']}")
                        st.markdown(f"**Tag:** {item['tag']}")
                    with col2:
                        if st.button(f"🗑️ Delete '{item['name']}'", key=f"delete_{item['name']}"):
                            if delete_item(item['name']):
                                st.success(f"Deleted item '{item['name']}'")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete item '{item['name']}'")

def render_merchants_selling_item_tab():
    """Tab to query which merchants sell a specific item and at what price"""
    st.header("🔎 Find Merchants Selling an Item")
    items = get_all_items()
    item_names = [item['name'] for item in items]

    selected_item = st.selectbox("Select Item to Search", options=item_names)
    if selected_item:
        merchants = get_all_merchants()
        results = []
        for merchant in merchants:
            # merchant['sell'] is expected to be a list of [item_name, price]
            for sell_item in merchant.get('sell', []):
                if sell_item[0] == selected_item:
                    results.append({
                        "Merchant": merchant['name'],
                        "Price": sell_item[1]
                    })
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True, width='stretch')
        else:
            st.info(f"No merchants currently sell '{selected_item}'.")