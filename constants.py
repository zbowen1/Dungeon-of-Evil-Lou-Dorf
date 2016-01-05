#####################################
# Game mechanics and const globals 
#####################################

# Play speed
GAME_SPEED = 0.05
AMULET_LEVEL = 5

START_LEVEL = 1

# Map ratios
MAP_WIDTH = 80
MAP_HEIGHT = 38
VISIBLE_TILES = ['X', ' ', '@', '+']

# Health
PLAYER_MAX_HEALTH = 250

# Foresight constants
ADVANCE_LEN = 9

# Globals
MAX_STEPS = 2500
NUM_ESCAPES = 10
RIGHT_HAND = 1
LEFT_HAND = 0
STRENGTHNAMES = {
    0: "",
    1: "Very Weak",
    2: "Weak",
    3: "Average",
    4: "Strong",
    5: "Very Strong"
}

PROBS = [
    'N/A',
    'Very Low',
    'Low',
    'Average',
    'High',
    'Very High'
]

DANGERS = {
    0: "Totally Safe!",
    1: "Extremely Safe",
    2: "Very Safe",
    3: "Safe",
    4: "Average",
    5: "Risky",
    6: "Very Risky",
    7: "Extremely Risky",
    8: "Dangerous",
    9: "Very Dangerous",
    10: "Extreme Danger!",
}

#####################################
# Probabilities and balancing factors
#####################################

# Misc Items
ITEM_STRENGTHS = {
    "Potions": 250, #25,
    "Repel": 10,
    "Fireballs": 25,
}

ITEM_START_VALUES = {
    "Potions": 15,
    "Repel": 10,
    "Fireballs": 7,
}

STARTING_WEAPON_DURABILITY = 75
ITEM_DURABILITIES = {
    # Base lvl items
    "Knife": 45,
    "Flimsy Shield": 40,
    # Low lvl items
    "Smelly Dagger": 40,
    "Slimy Bow": 40,
    "Moldy Shield": 40,
    # Low medium items
    "Rusty Dagger": 35,
    "Grimy Bow": 35,
    "Old Shield": 35,
    # Medium items
    "Plain Sword": 30,
    "Plain Bow": 30,
    "Buckler": 30,
    # Medium high items
    "Good Sword": 25,
    "Strong Bow": 25,
    "Big Shield": 25,
    # High items
    "Club of Whacking": 25,
    "Powerful Bow": 25,
    "Brawny Shield": 25,
    # Wolf items
    "Wolf Claws": 20,
    # Dragon items
    "Dragon Claws": 15,
    "Dragonhide Shield": 20,
    # Steve-n-Dorf items
    "Autograder": 20
}

# Enemies
ENEMY_DAMAGE_CONSTANT = 0.5

# Ranged damage bonus
RANGE_COMBAT_FACTOR = 1 #2
OFFHAND_FACTOR = 0.5    

# Defense
SHIELD_BASE_CHANCE = 0.50
SHIELD_LEVEL_BONUS = 0.05

# Event Probabilities
DANGER_MODIFIER = 0.3
ITEM_DROP_PROBABILITY = 0.5
BASE_ENEMY_ENCOUNTER_CHANCE = .03 #10 / 187.5
BASE_HIDE_ENCOUNTER_CHANCE = .03

#####################################
# Custom game exceptions 
#####################################

class Defeat(Exception):
    pass

class Victory(Exception):
    pass

class Quit(Exception):
    pass

HIDING_MSGS = [
    "You hide behind a dusty statue!",
    "You hide in a nearby closet!",
    "You crouch behind some dusty crates!",
    "You disguise yourself using dirt and vegetation!",
    "You crouch in the shadows.",
    "You carefully evade a patrolling guard!",
    "You take a quick nap in a nearby closet.",
    "You use your ninja skills to hang from the ceiling!",
    "You are almost caught, but the troll has bad eyesight and mistakes you for a wall.",
    "Hiding is for cowards!... and for people who like winning.",
]
