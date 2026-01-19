from creatures import *

class Player:
    def __init__(self):
        self.weapon_dmg = 22
        self.ability = 14

    def dmg_dealt(self, target: Creature):
        """Calculate damage dealt to a single target"""
        return ((self.weapon_dmg * (1 + self.ability / 100)) - target.defense) / (1 + target.armor / 100)
    
    def dmg_to_all_creatures(self):
        """Calculate damage dealt to all registered creatures"""
        results = {}
        for creature in Creature.get_all_creatures():
            damage = self.dmg_dealt(creature)
            results[creature.name] = {
                'damage': round(damage, 2),
                'hits_to_kill': round(creature.hp / damage, 2) if damage > 0 else float('inf'),
                'creature': creature
            }
        return results
    
    def print_damage_report(self):
        """Print a formatted damage report for all creatures"""
        results = self.dmg_to_all_creatures()
        
        print(f"\n{'='*80}")
        print(f"Damage Report - Weapon DMG: {self.weapon_dmg}, Ability: {self.ability}")
        print(f"{'='*80}")
        print(f"{'Creature':<25} {'DMG/Hit':<12} {'Hits to Kill':<15} {'HP':<8} {'Armor':<8} {'Defense':<8}")
        print(f"{'-'*80}")
        
        # Sort by damage dealt (highest first)
        sorted_results = sorted(results.items(), key=lambda x: x[1]['damage'], reverse=True)
        
        for name, data in sorted_results:
            creature = data['creature']
            print(f"{name:<25} {data['damage']:<12.2f} {data['hits_to_kill']:<15.2f} {creature.hp:<8} {creature.armor:<8} {creature.defense:<8}")
        
        print(f"{'='*80}\n")
        
        return results


# Usage
if __name__ == "__main__":
    player = Player()
    
    # Calculate and display damage to all creatures
    results = player.print_damage_report()    