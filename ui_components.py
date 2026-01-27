import streamlit as st
import pandas as pd
import os
from database import (
    add_merchant, add_item, get_all_items, 
    delete_item, get_all_tags, add_location, delete_merchant,
    update_merchant_sell_items,
    get_cached_merchants, get_cached_items, get_cached_locations
)

def render_add_merchant_form():
    """Render the form to add a new merchant"""
    st.header("➕ Add Merchant")
    
    items = get_cached_items()
    item_names = [item['name'] for item in items]
    tags = get_all_tags()  # tags are dynamic, so keep querying
    locations = get_cached_locations()
    
    # Initialize form counter in session state
    if 'merchant_form_key' not in st.session_state:
        st.session_state.merchant_form_key = 0
    
    # Initialize merchant items list for this form
    merchant_items_key = f'merchant_items_{st.session_state.merchant_form_key}'
    if merchant_items_key not in st.session_state:
        st.session_state[merchant_items_key] = []
    
    # Initialize form data preservation
    form_data_key = f'merchant_form_data_{st.session_state.merchant_form_key}'
    if form_data_key not in st.session_state:
        st.session_state[form_data_key] = {
            'name': '',
            'location_option': 0,
            'location_text': '',
            'buy_tags': [],
            'new_tag': ''
        }

    with st.form(f"add_merchant_form_{st.session_state.merchant_form_key}"):
        merchant_name = st.text_input(
            "Merchant Name", 
            placeholder="e.g., Erastus",
            value=st.session_state[form_data_key]['name']
        )
        
        # Location dropdown with option to add new
        location_options = ["<Add new location>"] + sorted(locations)
        location_option = st.selectbox(
            "Location",
            options=location_options,
            index=st.session_state[form_data_key]['location_option'],
            key=f"location_selector_{st.session_state.merchant_form_key}"
        )
        
        if location_option == "<Add new location>":
            merchant_location = st.text_input(
                "Enter New Location", 
                placeholder="e.g., Magnimar, Old Town", 
                value=st.session_state[form_data_key]['location_text'],
                key=f"new_location_input_{st.session_state.merchant_form_key}"
            )
        else:
            merchant_location = location_option
        
        st.subheader("What Merchant Buys (Tags)")
        buy_tags = st.multiselect(
            "Select Tags the Merchant Buys",
            options=tags,
            default=st.session_state[form_data_key]['buy_tags'],
            key=f"buy_tags_{st.session_state.merchant_form_key}"
        )
        new_tag = st.text_input(
            "Or add a new tag for buying (optional)", 
            value=st.session_state[form_data_key]['new_tag'],
            key=f"new_tag_{st.session_state.merchant_form_key}"
        )
        if new_tag and new_tag not in buy_tags:
            buy_tags.append(new_tag)
        
        st.subheader("What Merchant Sells")
        
        # Item selection - multiselect
        items_to_add = st.multiselect(
            "Select Items to Add",
            options=item_names,
            key=f"items_select_{st.session_state.merchant_form_key}"
        )
        
        add_items_btn = st.form_submit_button("➕ Add Items", type="secondary")
        
        # Add items to list when button is clicked
        if add_items_btn and items_to_add:
            # Save form data before rerun
            st.session_state[form_data_key]['name'] = merchant_name
            st.session_state[form_data_key]['location_option'] = location_options.index(location_option)
            st.session_state[form_data_key]['location_text'] = merchant_location if location_option == "<Add new location>" else ''
            st.session_state[form_data_key]['buy_tags'] = buy_tags
            st.session_state[form_data_key]['new_tag'] = new_tag
            
            # Add items
            existing_items = [item[0] for item in st.session_state[merchant_items_key]]
            for item_name in items_to_add:
                if item_name not in existing_items:
                    st.session_state[merchant_items_key].append([item_name, 1.0])
            st.rerun()
        
        # Display added items with price inputs
        sell_items = []
        if st.session_state[merchant_items_key]:
            st.markdown("**Items to Sell:**")
            items_to_remove = []
            
            for idx, (item, default_price) in enumerate(st.session_state[merchant_items_key]):
                col1, col2, col3 = st.columns([2, 1, 0.5])
                with col1:
                    st.text(item)
                with col2:
                    price = st.number_input(
                        "Price",
                        min_value=0,
                        value=int(default_price),
                        step=1,
                        key=f"price_{item}_{idx}_{st.session_state.merchant_form_key}",
                        label_visibility="collapsed"
                    )
                with col3:
                    if st.form_submit_button("🗑️", key=f"remove_{item}_{idx}_{st.session_state.merchant_form_key}"):
                        items_to_remove.append(idx)
                
                # Update price in session state
                st.session_state[merchant_items_key][idx][1] = price
                sell_items.append([item, price])
            
            # Remove items marked for deletion
            for idx in sorted(items_to_remove, reverse=True):
                st.session_state[merchant_items_key].pop(idx)
                st.rerun()

        submitted = st.form_submit_button("✅ Add Merchant", type="primary", use_container_width=True)
        
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
                    # Clear items list, form data, and increment form key to reset the form
                    if merchant_items_key in st.session_state:
                        del st.session_state[merchant_items_key]
                    if form_data_key in st.session_state:
                        del st.session_state[form_data_key]
                    st.session_state.merchant_form_key += 1
                    st.rerun()
                else:
                    st.error(f"❌ Merchant '{merchant_name}' already exists")

def render_merchants_list():
    """Render the list of all merchants"""
    st.header("📋 All Merchants")
    
    merchants = get_cached_merchants()
    merchants.sort(key=lambda x: x["name"])
    
    if not merchants:
        st.info("No merchants in database yet. Add one to get started!")
    else:
        # Get all items for the dropdown
        items = get_all_items()
        item_names = [item['name'] for item in items]
        
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
                
                # Add item to merchant section
                st.markdown("---")
                st.subheader("➕ Add Item to Inventory")
                
                with st.form(f"add_item_to_{merchant['name']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Filter out items already sold by this merchant
                        existing_item_names = [item[0] for item in merchant['sell']]
                        available_items = [item for item in item_names if item not in existing_item_names]
                        
                        if available_items:
                            new_item = st.selectbox(
                                "Select Item",
                                options=available_items,
                                key=f"new_item_select_{merchant['name']}"
                            )
                        else:
                            st.info("All items are already in this merchant's inventory")
                            new_item = None
                    
                    with col2:
                        if available_items:
                            new_price = st.number_input(
                                "Price",
                                min_value=0,
                                value=1,
                                step=1,
                                key=f"new_price_{merchant['name']}"
                            )
                    
                    if available_items:
                        submitted = st.form_submit_button("➕ Add Item", type="secondary")
                        
                        if submitted and new_item:
                            # Add the new item to the merchant's sell list
                            updated_sell_items = merchant['sell'] + [[new_item, new_price]]
                            if update_merchant_sell_items(merchant['name'], updated_sell_items):
                                st.success(f"Added '{new_item}' to {merchant['name']}'s inventory")
                                st.rerun()
                            else:
                                st.error(f"Failed to add item to {merchant['name']}'s inventory")
                
                st.markdown("---")
                
                # Delete merchant button
                if st.button(f"🗑️ Delete '{merchant['name']}'", key=f"delete_merchant_{merchant['name']}"):                    
                    if delete_merchant(merchant['name']):
                        st.success(f"Deleted merchant '{merchant['name']}'")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete merchant '{merchant['name']}'")

def render_add_item_form():
    """Render the form to add a new item"""
    st.header("➕ Add Item")
    
    # Initialize form counter in session state
    if 'item_form_key' not in st.session_state:
        st.session_state.item_form_key = 0
    
    with st.form(f"add_item_form_{st.session_state.item_form_key}", clear_on_submit=True):
        item_name = st.text_input("Item Name", placeholder="e.g., Iron Sword")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight", min_value=0.0, value=1.0, step=0.1)
        
        with col2:
            tags = get_all_tags()
            # Use selectbox that filters as you type
            tag_options = sorted(tags)
            tag = st.selectbox(
                "Tag/Category",
                options=tag_options,
                index=len(tag_options) - 1 if not tags else 0,
                help="Start typing to filter existing tags",
                key=f"tag_selector_{st.session_state.item_form_key}",
                accept_new_options=True
            )
        
        submitted = st.form_submit_button("Add Item", type="primary", width='stretch')
        
        if submitted:
            if not item_name:
                st.error("Please enter an item name")
            elif not tag or tag == "+ Create New Tag":
                st.error("Please enter a tag")
            else:
                success = add_item(item_name, weight, tag.strip())
                
                if success:
                    st.success(f"✅ Item '{item_name}' added successfully!")
                    # Increment form key to fully reset the form
                    st.session_state.item_form_key += 1
                    st.rerun()
                else:
                    st.error(f"❌ Item '{item_name}' already exists")


def render_items_list():
    """Render the list of all items, grouped by tag"""
    st.header("📦 All Items")
    
    items = get_cached_items()
    
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
    items = get_cached_items()
    item_names = [item['name'] for item in items]

    selected_item = st.selectbox("Select Item to Search", options=item_names)
    if selected_item:
        merchants = get_cached_merchants()
        results = []
        for merchant in merchants:
            # merchant['sell'] is expected to be a list of [item_name, price]
            for sell_item in merchant.get('sell', []):
                if sell_item[0] == selected_item:
                    results.append({
                        "Merchant": merchant['name'],
                        "Location": merchant.get('location', 'N/A'),
                        "Price": sell_item[1]
                    })
        if results:
            results.sort(key=lambda x: x["Merchant"])
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True, width='stretch')
        else:
            st.info(f"No merchants currently sell '{selected_item}'.")