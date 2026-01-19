import sqlite3
import json
from typing import List, Dict, Optional


class MerchantDatabase:
    """Database for managing merchants and their inventory"""
    
    def __init__(self, db_name: str = "merchants.db"):
        """Initialize database connection and create tables"""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables"""
        # Merchants table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                merchant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                location TEXT,
                description TEXT
            )
        ''')
        
        # Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')
        
        # Merchant inventory - what merchants sell
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchant_sells (
                merchant_id INTEGER,
                item_id INTEGER,
                price REAL NOT NULL,
                stock INTEGER DEFAULT -1,
                FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
                FOREIGN KEY (item_id) REFERENCES items(item_id),
                PRIMARY KEY (merchant_id, item_id)
            )
        ''')
        
        # Tags for items
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER,
                tag TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(item_id),
                PRIMARY KEY (item_id, tag)
            )
        ''')
        
        # What merchants buy (with tags)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchant_buys (
                merchant_id INTEGER,
                tag TEXT NOT NULL,
                buy_price_multiplier REAL DEFAULT 0.5,
                FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
                PRIMARY KEY (merchant_id, tag)
            )
        ''')
        
        self.conn.commit()
    
    def add_merchant(self, name: str, location: str = "", description: str = "") -> int:
        """Add a new merchant to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO merchants (name, location, description) VALUES (?, ?, ?)",
                (name, location, description)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Merchant '{name}' already exists")
            return self._get_merchant_id(name)
    
    def _get_merchant_id(self, name: str) -> Optional[int]:
        """Get merchant ID by name"""
        self.cursor.execute("SELECT merchant_id FROM merchants WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def _get_item_id(self, name: str) -> Optional[int]:
        """Get item ID by name"""
        self.cursor.execute("SELECT item_id FROM items WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_item(self, name: str, description: str = "", tags: List[str] = None) -> int:
        """Add a new item to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO items (name, description) VALUES (?, ?)",
                (name, description)
            )
            item_id = self.cursor.lastrowid
            
            # Add tags
            if tags:
                for tag in tags:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO item_tags (item_id, tag) VALUES (?, ?)",
                        (item_id, tag.lower())
                    )
            
            self.conn.commit()
            return item_id
        except sqlite3.IntegrityError:
            item_id = self._get_item_id(name)
            # Update tags if provided
            if tags:
                for tag in tags:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO item_tags (item_id, tag) VALUES (?, ?)",
                        (item_id, tag.lower())
                    )
                self.conn.commit()
            return item_id
    
    def add_merchant_sells_item(self, merchant_name: str, item_name: str, 
                                 price: float, stock: int = -1):
        """Add an item that a merchant sells"""
        merchant_id = self._get_merchant_id(merchant_name)
        item_id = self._get_item_id(item_name)
        
        if not merchant_id or not item_id:
            print("Merchant or item not found")
            return
        
        self.cursor.execute(
            "INSERT OR REPLACE INTO merchant_sells (merchant_id, item_id, price, stock) VALUES (?, ?, ?, ?)",
            (merchant_id, item_id, price, stock)
        )
        self.conn.commit()
    
    def add_merchant_buys_tag(self, merchant_name: str, tag: str, 
                              buy_price_multiplier: float = 0.5):
        """Set what tags of items a merchant buys"""
        merchant_id = self._get_merchant_id(merchant_name)
        
        if not merchant_id:
            print(f"Merchant '{merchant_name}' not found")
            return
        
        self.cursor.execute(
            "INSERT OR REPLACE INTO merchant_buys (merchant_id, tag, buy_price_multiplier) VALUES (?, ?, ?)",
            (merchant_id, tag.lower(), buy_price_multiplier)
        )
        self.conn.commit()
    
    def where_to_sell(self, item_name: str) -> List[Dict]:
        """Find where you can sell an item and for how much"""
        # Get item and its tags
        item_id = self._get_item_id(item_name)
        
        if not item_id:
            print(f"Item '{item_name}' not found")
            return []
        
        # Get item tags
        self.cursor.execute("SELECT tag FROM item_tags WHERE item_id = ?", (item_id,))
        tags = [row[0] for row in self.cursor.fetchall()]
        
        if not tags:
            print(f"Item '{item_name}' has no tags, cannot determine buyers")
            return []
        
        # Find merchants who buy items with these tags
        placeholders = ','.join('?' * len(tags))
        query = f'''
            SELECT 
                m.name AS merchant_name,
                m.location,
                mb.tag,
                mb.buy_price_multiplier,
                ms.price AS base_price
            FROM merchants m
            JOIN merchant_buys mb ON m.merchant_id = mb.merchant_id
            LEFT JOIN merchant_sells ms ON m.merchant_id = ms.merchant_id AND ms.item_id = ?
            WHERE mb.tag IN ({placeholders})
            ORDER BY mb.buy_price_multiplier DESC
        '''
        
        self.cursor.execute(query, [item_id] + tags)
        results = []
        
        for row in self.cursor.fetchall():
            buy_price = row['base_price'] * row['buy_price_multiplier'] if row['base_price'] else None
            results.append({
                'merchant': row['merchant_name'],
                'location': row['location'],
                'buys_tag': row['tag'],
                'multiplier': row['buy_price_multiplier'],
                'base_price': row['base_price'],
                'estimated_buy_price': buy_price
            })
        
        return results
    
    def search_item_price(self, item_name: str) -> List[Dict]:
        """Search for merchants selling a specific item"""
        query = '''
            SELECT 
                m.name AS merchant_name,
                m.location,
                i.name AS item_name,
                ms.price,
                ms.stock
            FROM merchant_sells ms
            JOIN merchants m ON ms.merchant_id = m.merchant_id
            JOIN items i ON ms.item_id = i.item_id
            WHERE i.name LIKE ?
            ORDER BY ms.price ASC
        '''
        
        self.cursor.execute(query, (f"%{item_name}%",))
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'merchant': row['merchant_name'],
                'location': row['location'],
                'item': row['item_name'],
                'price': row['price'],
                'stock': row['stock'] if row['stock'] >= 0 else 'Unlimited'
            })
        
        return results
    
    def list_all_merchants(self) -> List[Dict]:
        """List all merchants and their basic info"""
        self.cursor.execute("SELECT * FROM merchants")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_merchant_inventory(self, merchant_name: str) -> Dict:
        """Get detailed inventory for a specific merchant"""
        merchant_id = self._get_merchant_id(merchant_name)
        
        if not merchant_id:
            print(f"Merchant '{merchant_name}' not found")
            return {}
        
        # Get what they sell
        self.cursor.execute('''
            SELECT i.name, ms.price, ms.stock, i.description
            FROM merchant_sells ms
            JOIN items i ON ms.item_id = i.item_id
            WHERE ms.merchant_id = ?
        ''', (merchant_id,))
        
        sells = [dict(row) for row in self.cursor.fetchall()]
        
        # Get what they buy
        self.cursor.execute('''
            SELECT tag, buy_price_multiplier
            FROM merchant_buys
            WHERE merchant_id = ?
        ''', (merchant_id,))
        
        buys = [dict(row) for row in self.cursor.fetchall()]
        
        return {
            'merchant': merchant_name,
            'sells': sells,
            'buys_tags': buys
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()


# Example usage
def main():
    # Initialize database
    db = MerchantDatabase()
    
    # Add some example merchants
    db.add_merchant("General Store", "Town Square", "Sells basic goods")
    db.add_merchant("Blacksmith", "Forge District", "Weapons and armor")
    db.add_merchant("Alchemist", "Magic Quarter", "Potions and ingredients")
    db.add_merchant("Jeweler", "Market Street", "Gems and jewelry")
    
    # Add items with tags
    db.add_item("Iron Sword", "A basic iron sword", ["weapon", "metal", "melee"])
    db.add_item("Health Potion", "Restores 50 HP", ["potion", "consumable"])
    db.add_item("Diamond Ring", "A beautiful diamond ring", ["jewelry", "valuable"])
    db.add_item("Cheese Wheel", "A large wheel of cheese", ["food", "consumable"])
    db.add_item("Dragon Scale", "A scale from a dragon", ["crafting", "valuable", "rare"])
    
    # Set what merchants sell
    db.add_merchant_sells_item("General Store", "Cheese Wheel", 15.0, 10)
    db.add_merchant_sells_item("General Store", "Health Potion", 50.0, 20)
    db.add_merchant_sells_item("Blacksmith", "Iron Sword", 250.0, 5)
    db.add_merchant_sells_item("Alchemist", "Health Potion", 45.0, -1)
    db.add_merchant_sells_item("Jeweler", "Diamond Ring", 1500.0, 2)
    
    # Set what tags merchants buy
    db.add_merchant_buys_tag("General Store", "food", 0.6)
    db.add_merchant_buys_tag("General Store", "consumable", 0.4)
    db.add_merchant_buys_tag("Blacksmith", "weapon", 0.5)
    db.add_merchant_buys_tag("Blacksmith", "metal", 0.6)
    db.add_merchant_buys_tag("Alchemist", "potion", 0.5)
    db.add_merchant_buys_tag("Alchemist", "crafting", 0.7)
    db.add_merchant_buys_tag("Jeweler", "jewelry", 0.65)
    db.add_merchant_buys_tag("Jeweler", "valuable", 0.6)
    
    # Example queries
    print("\n=== WHERE TO SELL: Cheese Wheel ===")
    results = db.where_to_sell("Cheese Wheel")
    for r in results:
        print(f"  {r['merchant']} ({r['location']})")
        print(f"    - Buys '{r['buys_tag']}' items at {r['multiplier']*100}% of value")
        if r['estimated_buy_price']:
            print(f"    - Estimated buy price: {r['estimated_buy_price']:.2f} gold")
    
    print("\n=== WHERE TO SELL: Dragon Scale ===")
    results = db.where_to_sell("Dragon Scale")
    for r in results:
        print(f"  {r['merchant']} ({r['location']})")
        print(f"    - Buys '{r['buys_tag']}' items at {r['multiplier']*100}% of value")
    
    print("\n=== FIND: Health Potion ===")
    results = db.search_item_price("Health Potion")
    for r in results:
        print(f"  {r['merchant']} ({r['location']}): {r['price']} gold, Stock: {r['stock']}")
    
    print("\n=== Blacksmith Inventory ===")
    inventory = db.get_merchant_inventory("Blacksmith")
    print(f"Sells:")
    for item in inventory['sells']:
        print(f"  - {item['name']}: {item['price']} gold (Stock: {item['stock']})")
    print(f"Buys tags:")
    for tag in inventory['buys_tags']:
        print(f"  - {tag['tag']}: {tag['buy_price_multiplier']*100}% of base value")
    
    db.close()


if __name__ == "__main__":
    main()