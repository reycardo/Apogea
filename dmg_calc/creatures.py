class Creature:
    """Base class for creatures with combat stats"""
    
    # Class variable to track all creatures
    all_creatures = []
    
    def __init__(self, name, hp, xp, armor, defense):
        """
        Initialize a creature
        
        Args:
            name: Creature name
            hp: Hit points
            xp: Experience points reward
            armor: Armor value
            defense: Defense value
        """
        self.name = name
        self.hp = hp
        self.xp = xp
        self.armor = armor
        self.defense = defense
        
        # Register this creature
        Creature.all_creatures.append(self)
    
    def __repr__(self):
        return f"Creature('{self.name}', HP={self.hp}, XP={self.xp}, Armor={self.armor}, Defense={self.defense})"
    
    def __str__(self):
        return f"{self.name}: HP={self.hp}, XP={self.xp}, Armor={self.armor}, Defense={self.defense}"
    
    @classmethod
    def get_all_creatures(cls):
        """Get list of all registered creatures"""
        return cls.all_creatures
        

# Example creatures
Imp = Creature(
    name="Imp",
    hp=300,
    xp=220,
    armor=25,
    defense=22
)

# Add more creatures as needed
Occultist_Apprentice = Creature(
    name="Occultist Apprentice",
    hp=95,
    xp=45,
    armor=10,
    defense=8
)

Cave_Spider = Creature(
    name="Cave Spider",
    hp=100,
    xp=50,
    armor=8,
    defense=8
)



