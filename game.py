import sys
import asciiart
import random
from weapons import *
from entities import Player, Enemy, EnemyFactory
from maps import *
from utils import *
from maps import *
from inventory import Inventory
from getch import getch
from ai import User, USE_AI, STORY_MODE
 
class Escape(Exception): pass

class SeerData(object):
    def __init__(self):
        self.shield_level = 0
        self.escape_chance = 0
        self.current_escape = 0
        self.current_enemy_attack = 0
        self.current_player_attack = 0
        self.current_block =  0

    def generate_encounter(self, shield_level, escape_chance, items_dropped, is_dorf=False):
        self.shield_level = shield_level
        self.escape_chance = escape_chance
        self.enemy_attacks = [random.randint(1,5) for i in range(9)]
        self.player_attacks = [random.randint(1,5) for i in range(9)]
        self.blocks = [(random.uniform(0, 1) <= shield_level * SHIELD_LEVEL_BONUS + SHIELD_BASE_CHANCE) for i in range(9)]
        self.escapes = [(random.uniform(0, 1) <= .1 + .15 * escape_chance) for i in range(9)]
        self.will_drop = random.uniform(0, 1) <= ITEM_DROP_PROBABILITY or items_dropped < 3 or is_dorf

    def get_info(self, event_type, enemy_factory, map_dangers, hide_dangers, escapes):
        if event_type == "COMBAT": 
            return {
                "escapes": [bool(self.current_escape)] + self.escapes,
                "enemy_attacks": [self.current_enemy_attack] + self.enemy_attacks,
                "player_attacks": [self.current_player_attack] + self.player_attacks,
                "blocks": [bool(self.current_block)] + self.blocks,
                "will_drop": self.will_drop,
            }
        elif event_type == "MOVE": return {
                "enemies": [x.description() for x in enemy_factory.next_enemies],
                "map_danger": map_dangers,
                "hide_danger": hide_dangers,
                "escapes": escapes,
                # TODO need other data here?
            }

    def get_enemy_attack(self):
        self.enemy_attacks.append(random.randint(1,5))
        self.current_enemy_attack = self.enemy_attacks.pop(0)
        return self.current_enemy_attack

    def get_player_attack(self):
        self.player_attacks.append(random.randint(1,5))
        self.current_player_attack = self.player_attacks.pop(0)
        return self.current_player_attack

    def get_block(self):
        self.blocks.append(random.uniform(0, 1) <= self.shield_level * SHIELD_LEVEL_BONUS + SHIELD_BASE_CHANCE)
        self.current_block = self.blocks.pop(0)
        return self.current_block

    def get_escape(self):
        self.escapes.append(random.uniform(0, 1) <= .1 + .15 * self.escape_chance)
        self.current_escape = self.escapes.pop(0)
        return self.current_escape

    def get_drop_chance(self):
        return self.will_drop


class Game(object):

    def __init__(self):
        self.map = Map(START_LEVEL)
        # Enforce that a path does exist in the map
        while self.map.findPath() == None:
            self.map = Map(START_LEVEL)
        self.player = Player()
        self.inventory = Inventory()
        self.enemy_factory = EnemyFactory()
        self.user = User()

        self.invuln_turns = 0

        self.swap_weapon_to = None

        self.current_enemy = None
        self.level = START_LEVEL
        self.danger = 5
        self.hide_danger = 5
        self.escape_chance = 3
        self.items_dropped = 0 # a counter so we make sure they get shield, sword and bow chances first
        self.steps_left = MAX_STEPS
        self.escapes_remaining = NUM_ESCAPES
        self.encounter_sdorf = False

        self.dangers = []
        self.escape_chances = []
        self.hide_dangers = []

        self.seerdata = SeerData()
        self.init_dangers()

    def init_dangers(self):
        self.dangers.append(self._update(self.danger, 0, 10, 2))
        self.escape_chances.append(self._update(self.escape_chance, 1, 4, 3))
        self.hide_dangers.append(self._update(self.hide_danger, 0, 10, 2))

        for i in range(8):
            self.dangers.append(self._update(self.dangers[-1], 0, 10, 2))
            self.escape_chances.append(self._update(self.escape_chances[-1], 1, 4, 3))
            self.hide_dangers.append(self._update(self.hide_dangers[-1], 0, 10, 2))

    def levelUp(self):
        self.level += 1
        self.enemy_factory.setLevel(self.level)

    def takeStep(self):
        self.steps_left -= 1
        if self.steps_left <= 0: raise Defeat("You have failed to defeat the Fortress of Dorf.")

    def getDataForAI(self, moveType):
        itemStart = 1
        if self.inventory.get_main_hand():
            itemStart += 1
        if self.inventory.get_offhand():
            itemStart += 1
        if moveType == "ITEM":
            itemStart = 3
        items = self.inventory.get_pack()
        items_dict = {}
        # Map item numbers to weapons in the pack
        for i in range(len(items)):
            items_dict[str(itemStart + i)] = items[i]
        return {
            "situation": moveType,
            "enemy": None if not self.current_enemy else self.current_enemy.description(),
            "player": {
                "health": self.player.health,
                "next_attack": self.inventory.next_attack,
                "swap_weapon_to_hand": self.swap_weapon_to,
            },
            "inventory": {
                "main_hand": self.inventory.get_main_hand().description() if self.inventory.get_main_hand() else None,
                "off_hand": self.inventory.get_offhand().description() if self.inventory.get_offhand() else None,
                "backpack_weapons": items_dict,
                "backpack_has_space": self.inventory.has_inventory_space(),
                "potions": self.inventory.miscitems["Potions"],
                "repels": self.inventory.miscitems["Repel"],
                "fireballs": self.inventory.miscitems["Fireballs"],
                "candles": self.escapes_remaining,
            },
            "level": self.level,
            "map_danger": self.danger,
            "hide_danger": self.hide_danger,
            "escape_chance": self.escape_chance,
            "steps_left": self.steps_left,
            "invuln_steps": self.invuln_turns,
            "future": self.seerdata.get_info(moveType, self.enemy_factory, [self.danger] + self.dangers, [self.hide_danger] + self.hide_dangers, [self.escape_chance] + self.escape_chances),
        }

    def _inventoryData(self):
        # returns a list of 14 strings used to populate the bottom-right corner
        # of the war screen
        data = []
        for i in range(15):
            data.append("")
        data[0] = "Type: {0}".format(self.current_enemy.name)
        #data[1] = "Element: {0}".format(self.current_enemy.element)
        data[1] = "Weapon: {0}".format(self.current_enemy.item.name)
        data[2] = "Weapon Strength: {}".format(self.current_enemy.item.strength)
        data[3] = "Next Attack: {0}".format(
            STRENGTHNAMES[
                self.current_enemy.next_attack])
        data[4] = "- " * 25 + "-"
        data[5] = "EQUIPMENT"

        data[6] = (
            "Main Hand: {0}".format(
                self.inventory.get_main_hand().name \
                if self.inventory.get_main_hand()
                else "Nothing"
                )
        )
        data[7] = (
            "Off-Hand: {0}".format(
                self.inventory.get_offhand().name \
                if self.inventory.get_offhand()
                else "Nothing"
            )
        )
        data[8] = (
            "Player Next Attack: {0}".format(
                STRENGTHNAMES[self.inventory.next_attack]
            )
        )
        data[9] = "- " * 25 + "-"
        data[10] = "INVENTORY"
        data[11] = (
            "Potions: {0}".format(
                self.inventory.miscitems['Potions'])) 
        data[12] =  (
            "Repel: {0}".format(
                self.inventory.miscitems['Repel'])) 
        data[13] = (
            "Fireballs: {0}".format(
                self.inventory.miscitems['Fireballs'])) 
        data[14] = (
            "Candles: {0:<10} Escape Chance: {1:>16}".format(
                self.escapes_remaining, PROBS[self.escape_chance]))
        return data

    def printItems(self):  # TODO: list enemy weapon in case we want it?
        # populate list
        main_hand = self.inventory.get_main_hand()
        offhand = self.inventory.get_offhand()

        main_hand_image = getattr(asciiart, main_hand.image).split('\n') if main_hand else None
        offhand_image = getattr(asciiart, offhand.image).split('\n') if offhand else None

        miscItems = self._inventoryData()
        # fill the next 14 lines

        main_hand_stats = ["Name: " + str(main_hand.name), "Strength: " + str(main_hand.strength), 'Durability: ' + str(main_hand.durability)] if main_hand else None
        offhand_stats = ["Name: " + str(offhand.name), "Strength: " + str(offhand.strength), 'Durability: ' + str(offhand.durability)] if offhand else None
        
        # Gather inventory, including main hand and offhand
        items = []
        item_images = []
        if main_hand:
            items.append(main_hand_stats)
            item_images.append(getattr(asciiart, main_hand.image).split('\n')[1:])
        if offhand:
            items.append(offhand_stats)
            item_images.append(getattr(asciiart, offhand.image).split('\n')[1:])
        # Get weapon data and images
        for item in self.inventory.get_pack():
            items.append(["Name: " + item['name'], "Strength: " + str(item['strength']), 'Durability: ' + str(item['durability'])])
            item_images.append(getattr(asciiart, item['type']).split('\n')[1:]) # Remove the first new line of the items

        lines = []
        offhandText = 'Off-Hand' if offhand else '2.'
        numSpaces = 26 if offhand else 32
        lines.append("| {0:34s}".format('Main Hand' if main_hand else (offhandText if offhand else '1.')) +
                     "| {0:34s}".format(offhandText if main_hand else '2.') +
                     '| {0:34s}'.format('3.') +
                     "| " + "{0:52s}".format(miscItems[0]) + "|")
        lines.append("| " + " " * 22 + '{0:12s}'.format(item_images[0][0] if 0 < len(item_images) else "") +
                     "| " + " " * 22 + '{0:12s}'.format(item_images[1][0] if 1 < len(item_images) else "") +
                     '| ' + ' ' * 22 + '{0:12s}'.format(item_images[2][0] if 2 < len(item_images) else "") +
                     "| " + "{0:52s}".format(miscItems[1]) + "|")

        # print len(item_images), item_images
        for i in range(5):
            lines.append("| " + "{0:22s}".format(items[0][i % 3] if 0 < len(items) and items[0] and i < 3 else "") + '{0:12s}'.format(item_images[0][(i + 1) % 6] if 0 < len(item_images) and item_images[0] else "") +
                         "| " + "{0:22s}".format(items[1][i % 3] if 1 < len(items) and items[1] and i < 3 else "") + '{0:12s}'.format(item_images[1][(i + 1) % 6] if 1 < len(item_images) and item_images[1] else "") +
                         '| ' + "{0:22s}".format(items[2][i % 3] if 2 < len(items) and items[2] and i < 3 else "") + '{0:12s}'.format(item_images[2][(i + 1) % 6] if 2 < len(item_images) and item_images[2] else "") +
                         '| ' + '{0:52s}'.format(miscItems[i+2]) + '|')
        # Index 4 and 5
        lines.append('|' + '-' * 35 + '|' + '-' * 35 + '|' + "-" * 35 + '| ' + '{0:52s}'.format(miscItems[7]) + '|')
        lines.append('| {0:34s}'.format('4.') + '| {0:34s}'.format('5.') + '| {0:34s}'.format('6.') + '| {0:52s}'.format(miscItems[8]) + '|')
        lines.append("| " + " " * 22 + '{0:12s}'.format(item_images[3][0] if 3 < len(item_images) else "") + 
                     "| " + " " * 22 + '{0:12s}'.format(item_images[4][0] if 4 < len(item_images) else "") + 
                     '| ' + ' ' * 22 + '{0:12s}'.format(item_images[5][0] if 5 < len(item_images) else "") + 
                     "| " + "{0:52s}".format(miscItems[9]) + "|")
        for i in range(7, 12):
            lines.append("| " + "{0:22s}".format(items[3][(i-1) % 3] if 3 < len(items) and items[3] and i-1 < 9 else "") + '{0:12s}'.format(item_images[3][i % 6] if 3 < len(item_images) and item_images[3] else "") +
                         "| " + "{0:22s}".format(items[4][(i-1) % 3] if 4 < len(items) and items[4] and i-1 < 9 else "") + '{0:12s}'.format(item_images[4][i % 6] if 4 < len(item_images) and item_images[4] else "") +
                         '| ' + "{0:22s}".format(items[5][(i-1) % 3] if 5 < len(items) and items[5] and i-1 < 9 else "") + '{0:12s}'.format(item_images[5][i % 6] if 5 < len(item_images) and item_images[5] else "") +
                         '| ' + '{0:52s}'.format(miscItems[i+3]) + '|')
        
        lines.append("- " * 82)
        for line in lines:
            print line

    def printScreen(self):
        for i in range(3): print
        # update to remove old messages
        while len(self.messages) > 8:
            self.messages.pop(0)
        message = "\n".join(self.messages)

        print
        # print the message box
        printMessageBox(message)
        # print battlefield
        printBattlefield(
            CHARACTER3,
            getattr(
                asciiart,
                self.current_enemy.image),
            162,
            15)
        # print info bar
        print SCREEN.format(hp=str(self.player.health) + "/" + str(PLAYER_MAX_HEALTH), ehp=str(self.current_enemy.health))
        # print equipment and items
        self.printItems()

    def _getUserMove(self):
        self.messages.append("What will you do?")
        self.printScreen()

        print "What will you do? ('o' for help)",
        decision = self.user.__move__(self.getDataForAI("COMBAT"))
        while decision[0] not in ['x', 'c', 'i', 'e', '1', 'f', '2']:
            # TODO review logic here for bugs
            if decision == 'q':
                print
                raise Quit()
            if decision == 'p':
                printSeerData(self.seerdata.get_info("COMBAT", self.enemy_factory, [self.danger] + self.dangers, [self.hide_danger] + self.hide_dangers, [self.escape_chance] + self.escape_chances))
                while getch() != 'p': print "Press 'p' to return to the game!"
            elif decision == 'o':
                printHelpScreen(self.getDataForAI("COMBAT"))
                while getch() != 'o': print "Press 'o' to return to the game!"
            else:
                self.messages.append("That's not a valid command - what will you do?")
            self.printScreen()
            decision = self.user.__move__(self.getDataForAI("COMBAT"))
        return decision

    def playerTurn(self):
        # set environment variables
        self.printScreen()

        self.seerdata.current_block = self.seerdata.get_block()
        will_escape = self.seerdata.get_escape()
        decisions = [x for x in self._getUserMove()]
        playerDamage = 0
        playerAction = ""

        # SWAPPING
        if decisions[0] == '1' or decisions[0] == '2':
            items = self.inventory.get_pack()
            if len(items) == 0:
                self.messages.append("You have no items to swap between!")
                return False
            
            handChoice = 'Main Hand' if decisions[0] == '1' else 'Off-Hand'
            self.swap_weapon_to = handChoice
            
            # Print the weapons available to swap to
            validSwap = False
            while not validSwap:
                self.messages.append('Which weapon do you want to place in your {}?'.format(handChoice))
                itemIndexOffset = 1
                if self.inventory.get_main_hand():
                    itemIndexOffset += 1
                if self.inventory.get_offhand():
                    itemIndexOffset += 1
                for i in range(len(items)):
                    item = items[i]
                    keyPress = 'Press {} to swap to '.format(i + itemIndexOffset)
                    weaponMssg = '{0} (Type: {1}, Strength: {2}, Durability: {3})'.format(item['name'], item['type'], item['strength'], item['durability'])
                    self.messages.append(keyPress + weaponMssg)
                self.printScreen()
                
                try:
                    itemChoice = self.user.__move__(self.getDataForAI('SWAP'))
                    itemChoice = int(itemChoice[0]) - itemIndexOffset
                    self.messages = []    
                    if not self.inventory.is_valid_item_index(itemChoice):
                        self.messages.append('Invalid command!')
                        return False
                    elif (handChoice == 'Main Hand' and self.inventory.swap_main_hand(itemChoice)) or \
                            (handChoice == 'Off-Hand' and self.inventory.swap_offhand(itemChoice)):
                        self.messages.append('Successfully swapped weapon to {}!'.format(handChoice))
                        validSwap = True
                    else:
                        self.messages.append('You cannot place a {} in your {}!'.format(items[itemChoice]['name'], handChoice))
                        return False
                except ValueError:
                    self.messages.append("Invalid input!")
            if not USE_AI: time.sleep(2)
        
        # ATTACKING
        elif decisions[0] == 'f':
            self.playerStance = "OFFENSIVE"
            result = self.inventory.use_misc("Fireballs")
            if result:
                playerDamage = ITEM_STRENGTHS["Fireballs"]
                self.messages.append("You blast the {0} for {1} damage!".format(self.current_enemy.name, playerDamage))
                self.current_enemy.damage(playerDamage)
            else:
                self.messages.append("You wave your hands around, but nothing happens.")
            return True

        elif decisions[0] == 'x':
            self.playerStance = "OFFENSIVE"
            # are we attacking with a ranged weapon?
            ranged_items = self.inventory.get_equipped_ranged()
            if ranged_items:
                # deal the damage
                playerAction = "shoot"

            # for non-ranged weapons
            else:
                # deal the damage
                playerAction = "hit"

            if self.rangedEncounter and not self.inventory.get_equipped_ranged():
                # Melee weapon is equipped during ranged encounter, therefore cannot do damage
                return True
            playerDamage = self.inventory.get_damage()
            if (self.rangedEncounter):
                playerDamage *= RANGE_COMBAT_FACTOR
                
            # deal the damage and update
            totalDamage = max(1, # Force player to do minimum 1 damage
                              int(playerDamage * (float(self.inventory.next_attack) / 3)))
            self.current_enemy.damage(totalDamage)
            self.messages.append(
                "You {0} the {1} for {2} damage!".format(
                    playerAction,
                    self.current_enemy.name,
                    totalDamage))

            return True

        # ESCAPE
        elif decisions[0] == 'e':
            if not self.escapes_remaining: self.messages.append("You don't have any more Babylon Candles!")
            else:
                self.escapes_remaining -= 1
                if not will_escape:
                    self.messages.append("You failed to escape!")
                else:
                    self.messages.append("You escaped using a Babylon Candle!")
                    self.printScreen()
                    if not USE_AI: time.sleep(1.2)
                    raise Escape()

        # ITEMS
        elif decisions[0] == 'i':
            item_type = "Potions"
            result = self.inventory.use_misc(item_type)
            # TODO: Not yet fully implemented for things other than Potions
            if result:
                self.playerStance = "NEUTRAL"
                self.player.health = min(
                    result +
                    self.player.health,
                    PLAYER_MAX_HEALTH)
                self.messages.append(
                    "You drank a potion and recovered {0} health!".format(result))
                self.printScreen()
                return True
            else:
                self.messages.append("You don't have any Potions!")
                return False

        # SHIELDING
        elif decisions[0] == 'c':
            # is there a shield equipped?
            shields = self.inventory.get_equipped_defense()
            if shields:
                self.playerStance = "DEFENSIVE"
                self.messages.append("You raised your shield!")
                return True
            else:
                self.messages.append(
                    "You try to raise your shield, only to discover you're not holding one. The {0} looks confused.".format(
                        self.current_enemy.name))
                return True

        # BAD COMMAND
        else:
            assert(False and "Invalid command specified")

    def enemyTurn(self):
        # enemy will of course hit back
        damage = int((float(self.current_enemy.item.strength) * ENEMY_DAMAGE_CONSTANT) * self.current_enemy.next_attack)
        # player is shielding
        shield_level = 0
        if self.playerStance == "DEFENSIVE":
            # find the shields the player has
            #shield_level = self.inventory.get_equipped_defense().strength
            shield_level = self.inventory.get_defense()
            self.inventory.check_durability()
        if self.playerStance == "DEFENSIVE" and self.seerdata.current_block:
            self.messages.append("You successfully blocked the enemy attack!")
        else:
            self.player.damage(damage)
            damageType = "hit" if not isinstance(
                self.current_enemy.item,
                RangedWeapon) else "shoot"
            self.messages.append(
                "The {0} {2}s you for {1} damage!".format(
                    self.current_enemy.name,
                    damage,
                    damageType))
        return True

        # escape results

    def _isMssgTooLong(self, currentMessage, messageToAppend):
        return len(currentMessage + messageToAppend) > 159


    def runEvent(self):


        from ai import USE_AI

        self.seerdata.generate_encounter(self.inventory.get_defense(), self.escape_chance, self.items_dropped, is_dorf=("DORF" in self.current_enemy.image))
        # Combat loop
        isPlayerTurn = True
        self.messages = []
        if self.player.hiding: self.messages.append("A {0} found your hiding place!".format(self.current_enemy.name))
        else: self.messages.append("A {0} appeared!".format(self.current_enemy.name))
        self.playerStance = "NEUTRAL"
        # Assume player will not make a mistake until he does
        success = True
        # Is player or enemy using a bow?
        self.rangedEncounter = False
        self.current_enemy.next_attack = self.seerdata.get_enemy_attack()
        self.inventory.next_attack = self.seerdata.get_player_attack()
        if self.inventory.get_equipped_ranged() or isinstance(
                self.current_enemy.item,
                RangedWeapon):
            self.rangedEncounter = True

        while not self.current_enemy.isDead() and not self.player.isDead():
            self.printScreen()

            try:
                if self.rangedEncounter:
                    if self.inventory.get_equipped_ranged():
                        while not self.playerTurn():  # Loop on invalid moves
                            self.swap_weapon_to = None # Clear swap hand state
                            self.printScreen()
                        self.swap_weapon_to = None # Clear swap hand state
                        if self.inventory.get_equipped_ranged():
                            self.inventory.next_attack = self.seerdata.get_player_attack()
                        elif self.playerStance == 'OFFENSIVE':
                            self.messages.append("You swing your weapon wildly, but the {0} isn't close enough. The {0} looks confused...".format(self.current_enemy.name))
                        self.inventory.check_durability()
                    else:
                        self.messages.append(
                            'You run closer to the {0}...'.format(self.current_enemy.name)
                        )
                    if not self.current_enemy.isDead() and isinstance(self.current_enemy.item, RangedWeapon):
                        self.enemyTurn()
                        self.current_enemy.next_attack = self.seerdata.get_enemy_attack()

                # Player's move
                elif isPlayerTurn:
                    while not self.playerTurn():  # Loop on invalid moves
                        self.swap_weapon_to = None # Clear swap hand state
                        self.printScreen()
                    self.swap_weapon_to = None # Clear swap hand state
                    self.inventory.next_attack = self.seerdata.get_player_attack()
                    self.inventory.check_durability()

                # enemy's move
                else:
                    self.enemyTurn()
                    self.current_enemy.next_attack = self.seerdata.get_enemy_attack()
                # update
                #self.printScreen()

                # Bow is only useful on the first turn
                if self.rangedEncounter:
                    self.rangedEncounter = False
                    if not self.current_enemy.isDead() and not self.player.isDead() and not isinstance(
                            self.current_enemy.item,
                            RangedWeapon):
                        self.messages.append(
                            "The {0} runs closer to you...".format(
                                self.current_enemy.name))
                else:
                    # Change whose turn it is
                    isPlayerTurn = False if isPlayerTurn else True
            except Escape as e:
                self.messages.append("You successfully ran away!")
                self.printScreen()
                return

        # someone died
        if self.current_enemy.isDead():
            self.current_enemy.image = "DEAD_" + self.current_enemy.image
            self.messages.append(
                "You defeated the {0}!".format(
                    self.current_enemy.name))
            self.printScreen()

            if self.seerdata.get_drop_chance():
                self.items_dropped += 1
                self.messages.append(
                    "The {0} dropped a {1}...".format(
                        self.current_enemy.name,
                        self.current_enemy.item.name))
                self.current_enemy.image = "BLANK_ENEMY"

                items = self.inventory.get_pack()
                pickupMssg = '[1: Place in MH] [2: Place in OH]'
                validOptions = ['1', '2',]
                self.messages.append("Would you like to take this with you?")
                toAppend = ''
                for i in range(len(items)):
                    # Add 3 because MH and OH are 1 and 2, so indexing starts at 3
                    validOptions.append(str(i + 3))
                    toAppend = ' [{0}: Replace {1}]'.format(str(i + 3), items[i]['name'])
                    if self._isMssgTooLong(pickupMssg, toAppend):
                        self.messages.append(pickupMssg)
                        pickupMssg = ''
                        toAppend = toAppend[1:]
                    pickupMssg += toAppend
                
                # If Space still in inventory, display "Add to inventory"
                if self.inventory.has_inventory_space():
                    validOptions.append('8')
                    toAppend = ' [8: Add to inventory]'
                    if self._isMssgTooLong(pickupMssg, toAppend):
                        self.messages.append(pickupMssg)
                        pickupMssg = ''
                        toAppend = toAppend[1:]
                    pickupMssg += toAppend
                
                # Always allowed to ignore items
                validOptions.append('9')
                toAppend = ' [9: Ignore]'
                if self._isMssgTooLong(pickupMssg, toAppend):
                    self.messages.append(pickupMssg)
                    pickupMssg = ''
                    toAppend = toAppend[1:]
                pickupMssg += toAppend

                # self.messages.append("[1: Pick up with MH] [2: Pick up with OH] [3: Don't pick up]")
                self.messages.append(pickupMssg)
                self.printScreen()
                y_or_n = self.user.__move__(self.getDataForAI("ITEM"))
                while y_or_n not in validOptions:
                    self.messages.append("Please enter " + '/'.join(validOptions))
                    self.printScreen()
                    y_or_n = self.user.__move__(self.getDataForAI("ITEM"))
                if y_or_n == '1':
                    # pick up item
                    self.inventory.equip_main_hand(self.current_enemy.item)
                    self.printScreen()
                    if not USE_AI: 
                        time.sleep(2)
                elif y_or_n == '2':
                    self.inventory.equip_offhand(self.current_enemy.item)
                    self.printScreen()
                    if not USE_AI: 
                        time.sleep(2)
                elif y_or_n == '8':
                    self.inventory.add_to_pack(self.current_enemy.item)
                elif y_or_n != '9':
                    # Items in inventory are keys 3-7
                    self.inventory.replace_item(int(y_or_n) - 3, self.current_enemy.item)


        elif self.player.isDead():
            self.printScreen()
            if not USE_AI: time.sleep(2)
            raise Defeat("You have been defeated.")

    def checkEvent(self):
        pass
        random.seed()

        event_value = random.uniform(0, 1)
        encounter_chance = 0.03 + BASE_ENEMY_ENCOUNTER_CHANCE * self.danger 
        
        if self.player.hiding: 
            h_event_value = random.uniform(0, 1)
            h_encounter_chance = 0.03 + BASE_HIDE_ENCOUNTER_CHANCE * self.hide_danger 
            if h_event_value <= h_encounter_chance:
                encounter_chance = 1
            else:
                encounter_chance = -1
        
        if STORY_MODE and self.map.stevendorf and not self.map.boss_fight:
            self.map.boss_fight = True
            self.current_enemy = self.enemy_factory.generateEnemy(self.level, boss=self.map.stevendorf or self.encounter_sdorf, dorfweap=14)
            self.runEvent()

        elif event_value <= encounter_chance and not self.invuln_turns:
            # spawn an enemy TODO generator
            self.current_enemy = self.enemy_factory.get_next_enemy()
            self.runEvent()
            self.current_enemy = None

        if self.invuln_turns: self.invuln_turns -= 1
        self.player.hiding = False

    def _update(self, var, start, end, flex):
        temp_danger = var
        danger_change = random.randint(0,flex)
        up_or_down = random.uniform(0,1)
        if up_or_down <= DANGER_MODIFIER: temp_danger += danger_change
        else: temp_danger -= danger_change
        if temp_danger > end: temp_danger = end
        elif temp_danger < start: temp_danger = start
        return temp_danger

    def update_danger(self):
        self.dangers.append(self._update(self.dangers[-1], 0, 10, 2))
        self.danger = self.dangers.pop(0)
        self.escape_chances.append(self._update(self.escape_chances[-1], 1, 4, 3))
        self.escape_chance = self.escape_chances.pop(0)
        self.hide_dangers.append(self._update(self.hide_dangers[-1], 0, 10, 2))
        self.hide_danger = self.hide_dangers.pop(0)

    def move(self, direction):
        if direction == 'HIDE':
            self.player.hiding = True
            self.checkEvent()
            return 1
        # is there something on this square?
        if self.map.canMove(direction):
            if self.map.mapMove(direction):
                return 2
            self.checkEvent()
            return 1
        return 0
