import random
from weapons import *
from constants import *
from ai import STORY_MODE, USE_AI
from enemy_data import enemies, enemy_freqs
from enemy_data import enemies, enemy_freqs, STEVENDORF_STATS

class WeaponConstructor(object):
    def __init__(self):
        self.dropped_shield = False
        self.dropped_bow = False
        self.dropped_sword = False

    def __call__(self, weapon, name, strength, durability):
        if not self.dropped_shield:
            self.dropped_shield = True
            return Defense("SHIELD", "Flimsy Shield", 2, ITEM_DURABILITIES['Flimsy Shield'])
        elif not self.dropped_bow:
            self.dropped_bow = True
            return RangedWeapon("BOW", "Slimy Bow", 4, ITEM_DURABILITIES['Slimy Bow'])
        elif not self.dropped_sword:
            self.dropped_sword = True
            return MeleeWeapon("SWORD", "Knife", 2, ITEM_DURABILITIES['Knife'])
        elif weapon == "SHIELD":
            return Defense(weapon, name, strength, durability)
        elif not self.dropped_bow or weapon == "BOW":
            return RangedWeapon(weapon, name, strength, durability)
        elif not self.dropped_sword or weapon == "SWORD":
            return MeleeWeapon(weapon, name, strength, durability)
        elif weapon == "CLUB":
            return MeleeWeapon(weapon, name, strength, durability)
        elif weapon == "CLAWS":
            return MeleeWeapon(weapon, name, strength, durability)
        raise Exception("Bad argument to weapon constructor!")

class BaseConstructorException(Exception):
    pass    

class Entity(object):
    def __init__(self):
        self.health = 5
        pass

    def damage(self, num):
        self.health -= min(self.health, num)

    def isDead(self):
        return not self.health

class Player(Entity):
    def __init__(self):
        self.health = PLAYER_MAX_HEALTH
        self.hiding = False;

    def hide(self):
        assert(self.hiding == False)
        self.hiding = True;

    def unhide(self):
        assert(self.hiding == True)
        self.hiding = False;

class Enemy(Entity):
    def __init__(self):
        raise BaseConstructorException()

    def __init__(self, image, name, health, item):
        self.image = image
        self.name = name
        self.health = health
        self.item = item
        self.next_attack = 0

    def description(self):
        return {
            'name': self.name,
            'health': self.health,
            'item': self.item.description(),
            'next_attack': self.next_attack
        }

class EnemyFactory(object):
    def __init__(self):
        self.weapon_constructor = WeaponConstructor()
        self.current_level = START_LEVEL
        self.next_enemies = []
        random.seed()
        self.setLevel(START_LEVEL)
        pass

    def setLevel(self, level):
        self.current_level = level
        self.next_enemies = []
        if not level % 10 and not STORY_MODE:
            self.next_enemies.append(self.generateEnemy(level, boss=True))
        else:
            self.next_enemies.append(self.generateEnemy(level))
        for i in range(4):
            self.next_enemies.append(self.generateEnemy(level))
   
    def get_next_enemy(self):
        self.next_enemies.append(self.generateEnemy(self.current_level)) 
        return self.next_enemies.pop(0)

    def generateEnemy(self, level, boss=False, dorfweap=10):
        # compute enemy event
        choice = 0
        p = 0
        event = random.uniform(0,1)
        for i in range(len(enemy_freqs)):
            p += enemy_freqs[i]
            if event <= p:
                choice = i
                break 
        # select enemy
        enemy = enemies[min(choice, level - 1)] if not boss else STEVENDORF_STATS
        item = enemy["items"][random.randint(0, len(enemy["items"])-1)] 
        
        return Enemy(
            enemy["image"], 
            enemy["name"], 
            random.randint(enemy["health"]["min"], enemy["health"]["max"]),
            self.weapon_constructor(item["type"], item["name"], (item["strength"] if not boss else dorfweap), item['durability'])
        )
            
         
