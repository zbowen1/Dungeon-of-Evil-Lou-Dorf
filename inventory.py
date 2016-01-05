from weapons import *
from entities import *
from constants import STARTING_WEAPON_DURABILITY

class Inventory(object):
    def __init__(self):
        self.main_hand = RangedWeapon("BOW", "Wooden Bow", 1, STARTING_WEAPON_DURABILITY) #MeleeWeapon("SWORD", "Wooden Sword", 2)
        self.offhand = None
        self._MAX_ITEMS = 6
        # self.pack = [MeleeWeapon("SWORD", "Wooden Sword", 2, 10),Defense("SHIELD", "Wooden Shield", 2, 15),MeleeWeapon("SWORD", "Wooden Sword", 2, 10),MeleeWeapon("SWORD", "Wooden Sword", 2, 10),]
        self.pack = []
        self.next_attack = 0
        self.miscitems = {
            "Potions": ITEM_START_VALUES["Potions"],
            "Repel": ITEM_START_VALUES["Repel"],
            "Fireballs": ITEM_START_VALUES["Fireballs"],
        }

    def equip_main_hand(self, item):
        if not self.main_hand and not self.has_inventory_space():
            self.pack.pop()
        if isinstance(item, RangedWeapon):
            self.main_hand = item
            self.offhand = None
        elif isinstance(item, MeleeWeapon):
            if isinstance(self.offhand, RangedWeapon):
                self.offhand = None
            self.main_hand = item
        elif isinstance(item, Defense):
            self.equip_offhand(item)
    
        else:
            raise Exception("Equipped item has invalid type")
    
    def equip_offhand(self, item):
        if not self.offhand and not self.has_inventory_space():
            self.pack.pop()
        if isinstance(item, RangedWeapon):
            self.equip_main_hand(item)
        elif isinstance(item, MeleeWeapon):
            if isinstance(self.main_hand, RangedWeapon):
                self.main_hand = None
            self.offhand = item
        elif isinstance(item, Defense):
            if isinstance(self.main_hand, RangedWeapon):
                self.main_hand = None
            self.offhand = item
    
        else:
            raise Exception("Equipped item has invalid type")
    
    def get_main_hand(self):
        assert(not isinstance(self.main_hand, Defense))
        return self.main_hand

    def get_offhand(self):
        assert(not isinstance(self.offhand, RangedWeapon))
        return self.offhand

    def get_equipped(self):
        return [
            self.main_hand,
            self.offhand
        ]

    def get_equipped_defense(self):
        assert(not isinstance(self.main_hand, Defense))
        if isinstance(self.offhand, Defense): return self.offhand
        else: return None

    def get_equipped_melee(self):
        if isinstance(self.main_hand, MeleeWeapon): return self.main_hand
        elif isinstance(self.offhand, MeleeWeapon): return self.offhand
        else: return None

    def get_equipped_ranged(self):
        assert(not isinstance(self.offhand, RangedWeapon))
        if isinstance(self.main_hand, RangedWeapon): return self.main_hand
        else: return None

    def get_damage(self):
        damage = 0
        # ranged dmg applies * 1.5
        if isinstance(self.main_hand, RangedWeapon):
            damage += self.main_hand.strength
        elif isinstance(self.main_hand, MeleeWeapon):
            damage += self.main_hand.strength
        if isinstance(self.offhand, RangedWeapon):
            assert(0)
            damage += self.offhand.strength
        elif isinstance(self.offhand, MeleeWeapon):
            damage += self.offhand.strength * OFFHAND_FACTOR
        if self.main_hand != None: self.main_hand.durability -= 1
        if isinstance(self.offhand, MeleeWeapon): self.offhand.durability -= 1
        return max(damage, 1)
   
    def get_defense(self):
        defense = 0
        assert(not isinstance(self.main_hand, Defense))
        if isinstance(self.offhand, Defense):
            defense += self.offhand.strength
            self.offhand.durability -= 1
        return defense
 
    def get_items(self):
        return self.get_equipped()

    def add_misc(self, misc, count):
        assert(misc in self.miscitems.keys())
        self.miscitems[misc] += count

    def have_misc(self, misc):
        assert(misc in self.miscitems.keys())
        # a more verbose version for clarity
        return True if self.miscitems[misc] != 0 else False

    def use_misc(self, misc):
        assert(misc in self.miscitems.keys())
        # Note: Must return non-zero value for item, otherwise bugs will ensue
        if not self.have_misc(misc): return False
        self.miscitems[misc] -= 1
        return ITEM_STRENGTHS[misc]
    
    def check_durability(self):
        if self.main_hand != None and self.main_hand.durability <= 0: self.main_hand = None
        if self.offhand != None and self.offhand.durability <= 0 : self.offhand = None


    # Functions for 6 item inventory system
    def is_valid_item_index(self, index):
        return index >= 0 and index < len(self.pack)

    def get_inventory_size(self):
        count = 0
        if self.main_hand != None: count += 1
        if self.offhand != None: count += 1
        return len(self.pack) + count

    def has_inventory_space(self):
        return self.get_inventory_size() < self._MAX_ITEMS

    def get_pack(self):
        items = []
        for i in self.pack:
            items.append(i.description())
        return items

    def add_to_pack(self, item):
        assert self.has_inventory_space()
        self.pack.append(item)

    def swap_main_hand(self, itemIndex):
        assert self.is_valid_item_index(itemIndex)
        if isinstance(self.pack[itemIndex], Defense): 
            # assert 0
            return False

        # Place mainhand in pack if holding something
        if self.main_hand != None: 
            self.pack.append(self.main_hand)
        # Place offhand in pack if you're grabbing a bow
        if isinstance(self.pack[itemIndex], RangedWeapon) and self.offhand != None: 
            self.pack.append(self.offhand)
            self.offhand = None
        self.main_hand = self.pack.pop(itemIndex)
        return True

    def swap_offhand(self, itemIndex):
        assert self.is_valid_item_index(itemIndex)
        if isinstance(self.pack[itemIndex], RangedWeapon): return False

        if self.offhand != None: 
            self.pack.append(self.offhand)
        if isinstance(self.main_hand, RangedWeapon): 
            self.pack.append(self.main_hand)
            self.main_hand = None
        self.offhand = self.pack.pop(itemIndex)
        return True

    def replace_item(self, itemIndex, item):
        assert len(self.pack) and self.is_valid_item_index(itemIndex)
        self.pack[itemIndex] = item
