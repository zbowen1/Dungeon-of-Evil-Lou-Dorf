from constants import ITEM_DURABILITIES
enemy_freqs = [0.08, 0.10, 0.10, 0.12, 0.12, 0.15, 0.15, 0.18]

enemies = [
    {
        "name": "Cave Rat",
        "image": "RAT",
        "health": {
            "min": 1,
            "max": 3,
        },
        "items": [
            {"name": "Knife","type": "SWORD", "strength": 2, 'durability': ITEM_DURABILITIES['Knife']},
            {"name": "Flimsy Shield", "type": "SHIELD", "strength": 3, 'durability': ITEM_DURABILITIES['Flimsy Shield']},
        ]
    },
    {
        "name": "Cave Goblin",
        "image": "GOBLIN",
        "health": {
            "min": 5,
            "max": 8,
        },
        "items": [
            {"name": "Smelly Dagger","type": "SWORD", "strength": 5, 'durability': ITEM_DURABILITIES['Smelly Dagger']},
            {"name": "Slimy Bow", "type": "BOW", "strength": 4, 'durability': ITEM_DURABILITIES['Slimy Bow']},
            {"name": "Moldy Shield", "type": "SHIELD", "strength": 5, 'durability': ITEM_DURABILITIES['Moldy Shield']},
        ]
    },
    {
        "name": "Big Goblin",
        "image": "GOBLIN",
        "health": {
            "min": 8,
            "max": 10,
        },
        "items": [
            {"name": "Rusty Dagger","type": "SWORD", "strength": 6, 'durability': ITEM_DURABILITIES['Rusty Dagger']},
            {"name": "Grimy Bow", "type": "BOW", "strength": 5, 'durability': ITEM_DURABILITIES['Grimy Bow']},
            {"name": "Old Shield", "type": "SHIELD", "strength": 6, 'durability': ITEM_DURABILITIES['Old Shield']},
        ]
    },
    {
        "name": "Skeleton",
        "image": "SKELETON",
        "health": {
            "min": 20,
            "max": 30,
        },
        "items": [
            {"name": "Plain Sword","type": "SWORD", "strength": 7, 'durability': ITEM_DURABILITIES['Plain Sword']},
            {"name": "Plain Bow", "type": "BOW", "strength": 6, 'durability': ITEM_DURABILITIES['Plain Bow']},
            {"name": "Buckler", "type": "SHIELD", "strength": 7, 'durability': ITEM_DURABILITIES['Buckler']},
        ]
    },
    {
        "name": "Big Skeleton",
        "image": "SKELETON",
        "health": {
            "min": 30,
            "max": 45,
        },
        "items": [
            {"name": "Good Sword","type": "SWORD", "strength": 8, 'durability': ITEM_DURABILITIES['Good Sword']},
            {"name": "Strong Bow", "type": "BOW", "strength": 7, 'durability': ITEM_DURABILITIES['Strong Bow']},
            {"name": "Big Shield", "type": "SHIELD", "strength": 8, 'durability': ITEM_DURABILITIES['Big Shield']},
        ]
    },
    {
        "name": "Mud Troll",
        "image": "TROLL",
        "health": {
            "min": 50,
            "max": 60,
        },
        "items": [
            {"name": "Club of Whacking","type": "CLUB", "strength": 9, 'durability': ITEM_DURABILITIES['Club of Whacking']},
            {"name": "Powerful Bow", "type": "BOW", "strength": 8, 'durability': ITEM_DURABILITIES['Powerful Bow']},
            {"name": "Brawny Shield", "type": "SHIELD", "strength": 9, 'durability': ITEM_DURABILITIES['Brawny Shield']},
        ]
    },
    {
        "name": "Three-Headed Wolf",
        "image": "DOG",
        "health": {
            "min": 60,
            "max": 100,
        },
        "items": [
            {"name": "Wolf Claws","type": "CLAWS", "strength": 14, 'durability': ITEM_DURABILITIES['Wolf Claws']},
        ]
    },
    {
        "name": "Ancient Dragon",
        "image": "DRAGON",
        "health": {
            "min": 80,
            "max": 100,
        },
        "items": [
            {"name": "Dragon Claws","type": "CLAWS", "strength": 18, 'durability': ITEM_DURABILITIES['Dragon Claws']},
            {"name": "Dragonhide Shield","type": "SHIELD", "strength": 10, 'durability': ITEM_DURABILITIES['Dragonhide Shield']},
        ]
    },
]


STEVENDORF_STATS = {
        "name": "Evil Steve-n-Dorf",
        "image": "STEVENDORF",
        "health": {
            "min": 130,
            "max": 130,
        },
        "items": [
            {"name": "Autograder","type": "SWORD", "strength": 15, 'durability': ITEM_DURABILITIES['Autograder']},
        ]
    }
