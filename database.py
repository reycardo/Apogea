import sqlite3
import json


def initialize_database():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect('merchants.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            buy_tags TEXT,
            sell_items TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            weight REAL NOT NULL,
            tag TEXT NOT NULL,
            icon TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def get_connection():
    """Get database connection"""
    return sqlite3.connect('merchants.db', check_same_thread=False)


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
            "INSERT INTO merchants (name, buy_tags, sell_items) VALUES (?, ?, ?)",
            (name, json.dumps(buy_tags), json.dumps(sell_items))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


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
    conn.close()
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
            "INSERT INTO items (name, weight, tag, icon) VALUES (?, ?, ?, ?)",
            (name, weight, tag, icon)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


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
    conn.close()
    return items
    return merchants
