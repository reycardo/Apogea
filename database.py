import psycopg2
from psycopg2 import pool
import json
import streamlit as st


# Connection pool for efficient database connections
connection_pool = None

def get_connection_pool():
    """Initialize and return the connection pool"""
    global connection_pool
    if connection_pool is None:
        # Get database URL from Streamlit secrets
        database_url = st.secrets.get("DATABASE_URL", "")
        if not database_url:
            st.error("⚠️ DATABASE_URL not found in secrets. Please configure your database connection.")
            st.stop()
        
        connection_pool = pool.SimpleConnectionPool(
            1, 10,  # min and max connections
            database_url
        )
    return connection_pool

def initialize_database():
    """Create database and tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            buy_tags TEXT,
            sell_items TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            weight REAL NOT NULL,
            tag TEXT NOT NULL,
            icon TEXT
        )
    ''')
    
    conn.commit()
    cursor.close()
    return_connection(conn)


def get_connection():
    """Get database connection from pool"""
    pool = get_connection_pool()
    return pool.getconn()

def return_connection(conn):
    """Return connection to pool"""
    pool = get_connection_pool()
    pool.putconn(conn)


def add_merchant(name, buy_tags, sell_items):
    """Add a merchant to the database
    
    Args:
        name: Merchant name
        buy_tags: List of tags the merchant buys
        sell_items: List of [item_name, price] pairs
        
    Returns:
        True if successful, False if merchant already exists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO merchants (name, buy_tags, sell_items) VALUES (%s, %s, %s)",
            (name, json.dumps(buy_tags), json.dumps(sell_items))
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.close()
        return_connection(conn)
        return False

def delete_merchant(name):
    """Delete a merchant from the database by its unique name

    Args:
        name: The name of the merchant to delete

    Returns:
        True if a merchant was deleted, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM merchants WHERE name = %s", (name,))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    return_connection(conn)
    return deleted

def get_all_merchants():
    """Get all merchants from database
    
    Returns:
        List of merchant dictionaries with id, name, buy tags, and sell items
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, buy_tags, sell_items FROM merchants")
    merchants = []
    for row in cursor.fetchall():
        merchants.append({            
            'name': row[0],
            'buy': json.loads(row[1]),
            'sell': json.loads(row[2])
        })
    cursor.close()
    return_connection(conn)
    return merchants


def add_item(name, weight, tag, icon=""):
    """Add an item to the database
    
    Args:
        name: Item name
        weight: Item weight
        tag: Item tag/category
        icon: Optional icon/emoji for the item
        
    Returns:
        True if successful, False if item already exists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO items (name, weight, tag, icon) VALUES (%s, %s, %s, %s)",
            (name, weight, tag, icon)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.close()
        return_connection(conn)
        return False

def delete_item(name):
    """Delete an item from the database by its unique name

    Args:
        name: The name of the item to delete

    Returns:
        True if an item was deleted, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE name = %s", (name,))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    return_connection(conn)
    return deleted

def get_all_items():
    """Get all items from database
    
    Returns:
        List of item dictionaries with id, name, weight, tag, and icon
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, weight, tag, icon FROM items")
    items = []
    for row in cursor.fetchall():
        items.append({
            'id': row[0],
            'name': row[1],
            'weight': row[2],
            'tag': row[3],
            'icon': row[4]
        })
    cursor.close()
    return_connection(conn)
    return items    

def get_all_tags():
    """Get all unique tags from items in the database

    Returns:
        List of unique tag strings
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tag FROM items")
    tags = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return_connection(conn)
    return tags