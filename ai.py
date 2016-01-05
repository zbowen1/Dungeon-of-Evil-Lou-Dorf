from getch import getch
from constants import *
import time, random
import select
import sys
import multiprocessing
from multiprocessing import Pipe
import threading
import time
random.seed()

################################################################################
#                        Toggle Student AI / Story Mode                        #
################################################################################
USE_AI = True#
STORY_MODE = True                                                            #
################################################################################

# A dictionary for 'passing' information between your functions
ACTION_INFO = {'source_hand': 0, 'shoot':False}

def hand_empty (options):
    if options['inventory']['main_hand'] is None and options['inventory']['off_hand'] is None:
        return 11
    if options['inventory']['main_hand'] is None and options['inventory']['off_hand'] is not None:
        return 12
    if options['inventory']['main_hand'] is not None and options['inventory']['off_hand'] is None:
        return 21
    if options['inventory']['main_hand'] is not None and options['inventory']['off_hand'] is not None:

        return 22

def search_for_best_weapon_over(options,weapon_type):
    k = 0
    temp_strength = 0
    best_index = 0
    if options['inventory']['backpack_weapons'] is not None:
        while k < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['type'] == weapon_type:
                if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['strength'] >= temp_strength:
                    temp_strength = options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['strength']
                    best_index = k

            k += 1
    if hand_empty(options) == 11:


        return best_index
    elif hand_empty(options) == 12:
        if options['inventory']['off_hand']['type'] == weapon_type:
            if options['inventory']['off_hand']['strength'] >= temp_strength:
                return 'OFF_HAND'


    elif hand_empty(options) == 21:
        if options['inventory']['main_hand']['type'] == weapon_type:
            if options['inventory']['main_hand']['strength'] >= temp_strength:
                return 'MAIN_HAND'

    elif hand_empty(options) == 22:
        if options['inventory']['main_hand']['type'] == weapon_type and options['inventory']['off_hand']['type'] == weapon_type:
            if options['inventory']['main_hand']['strength'] >= options['inventory']['off_hand']['strength']:
                if options['inventory']['main_hand']['strength'] >= temp_strength:
                    return 'MAIN_HAND'
                else:
                    return best_index
            else:
                if options['inventory']['off_hand']['strength'] >= temp_strength:
                    return 'OFF_HAND'
                else:
                    return best_index
        elif options['inventory']['main_hand']['type'] == weapon_type and options['inventory']['off_hand']['type'] != weapon_type:
            if options['inventory']['main_hand']['strength'] >= temp_strength:
                return 'MAIN_HAND'
        elif options['inventory']['off_hand']['type'] == weapon_type and options['inventory']['main_hand']['type'] != weapon_type:
            if options['inventory']['off_hand']['strength'] >= temp_strength:
                return 'OFF_HAND'
    return best_index


def search_for_worst_weapon_over(options,weapon_type):
    k = 0
    temp_strength = 1000
    worst_index = 0
    if options['inventory']['backpack_weapons'] is not None:
        while k < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['type'] == weapon_type:
                if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['strength'] <= temp_strength:
                    temp_strength = options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[k]]['strength']
                    worst_index = k
            k += 1
    if hand_empty(options) == 11:


        return worst_index
    elif hand_empty(options) == 12:
        if options['inventory']['off_hand']['type'] == weapon_type:
            if options['inventory']['off_hand']['strength'] <= temp_strength:
                return 'OFF_HAND'


    elif hand_empty(options) == 21:
        if options['inventory']['main_hand']['type'] == weapon_type:
            if options['inventory']['main_hand']['strength'] <= temp_strength:
                return 'MAIN_HAND'

    elif hand_empty(options) == 22:
        if options['inventory']['main_hand']['type'] == weapon_type and options['inventory']['off_hand']['type'] == weapon_type:
            if options['inventory']['main_hand']['strength'] <= options['inventory']['off_hand']['strength']:
                if options['inventory']['main_hand']['strength'] <= temp_strength:
                    return 'MAIN_HAND'
                else:
                    return worst_index
            else:
                if options['inventory']['off_hand']['strength'] <= temp_strength:
                    return 'OFF_HAND'
                else:
                    return worst_index
        elif options['inventory']['main_hand']['type'] == weapon_type and options['inventory']['off_hand']['type'] != weapon_type:
            if options['inventory']['main_hand']['strength'] <= temp_strength:
                return 'MAIN_HAND'
        elif options['inventory']['off_hand']['type'] == weapon_type and options['inventory']['main_hand']['type'] != weapon_type:
            if options['inventory']['off_hand']['strength'] <= temp_strength:
                return 'OFF_HAND'
    return worst_index



def num_weapon(options, weapon_type_or_name, type_or_name):
    i = 0
    count = 0
    if options['inventory']['main_hand'] is None and options['inventory']['off_hand'] is not None:
        if options['inventory']['off_hand'][type_or_name] == weapon_type_or_name:
            count += 1
        while i < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[i]][type_or_name] == weapon_type_or_name:
                count += 1
            i = i+1
    elif options['inventory']['main_hand'] is not None and options['inventory']['off_hand'] is None:
        if options['inventory']['main_hand'][type_or_name] == weapon_type_or_name:
            count += 1
        while i < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[i]][type_or_name] == weapon_type_or_name:
                count += 1
            i = i+1
    elif options['inventory']['main_hand'] is not None and options['inventory']['off_hand'] is not None:
        if options['inventory']['off_hand'][type_or_name] == weapon_type_or_name:
            count += 1
        if options['inventory']['main_hand'][type_or_name] == weapon_type_or_name:
            count += 1
        while i < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[i]][type_or_name] == weapon_type_or_name:
                count += 1
            i = i+1
    elif options['inventory']['main_hand'] is None and options['inventory']['off_hand'] is None:
        while i < len(options['inventory']['backpack_weapons'].keys()):
            if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[i]][type_or_name] == weapon_type_or_name:
                count += 1
            i = i+1

    return count




def combat_action(options):
    global ACTION_INFO # Necessary for reading and writing the global ACTION_INFO dictionary
    #escape 1
    if options['enemy']['name'] == 'Three-Headed Wolf'or options['enemy']['name'] == 'Ancient Dragon':
        #escape
        if options['future']['will_drop'] == False and options['future']['escapes'][0] == True and options['inventory']['candles'] >0:
            return 'e'

    #use potions
    if options['inventory']['potions'] > 0:
        if int((float(options['enemy']['item']['strength']) * 0.5 )* options['enemy']['next_attack']) >= options['player']['health']:
            return 'i'

    #fire ball
    if options['enemy']['health'] >= 20 and options['inventory']['fireballs'] > 0 and options['enemy']['next_attack'] <= 3:
        return 'f'

    #Dorf
    if options['enemy']['name'] == 'Evil Steve-n-Dorf'and options['inventory']['candles'] > 0:
        if options['future']['escapes'][0] == True and options['inventory']['candles'] > 0:
            return 'e'
        if num_weapon(options,'SHIELD', 'type') >= 1:
            if search_for_best_weapon_over(options, 'SHIELD') != 'OFF_HAND':
                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options,'SHIELD')
                return '2'
            else:
                if options['future']['blocks'][0] == True:
                    return 'c'
                else:
                    if num_weapon(options, 'SWORD', 'type') >= 1:
                        if search_for_worst_weapon_over(options,'SWORD') != 'MAIN_HAND':
                            ACTION_INFO['source_hand'] = search_for_worst_weapon_over(options, 'SWORD')
                            return '1'
        return 'x'

    #
    if options['enemy']['name'] == 'Evil Steve-n-Dorf' or options['enemy']['name'] == 'Ancient Dragon' or options['enemy']['name'] == 'Three-Headed Wolf' or options['enemy']['name'] == 'Mud Troll' or options['enemy']['name'] == 'Big Skeleton' or options['enemy']['name'] == 'Skeleton' or options['enemy']['name'] == 'Big Goblin' or options['enemy']['name'] == 'Cave Goblin' or options['enemy']['name'] == 'Cave rat':
        # defense
        if options['enemy']['next_attack'] >= 3 and ACTION_INFO['shoot'] == False:
            if num_weapon(options,'SHIELD', 'type') >= 1:
                if search_for_best_weapon_over(options, 'SHIELD') != 'OFF_HAND':
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options,'SHIELD')
                    return '2'
                elif search_for_best_weapon_over(options, 'SHIELD') == 'OFF_HAND':
                    #kill-in-next_attack
                    if num_weapon(options, 'CLAWS', 'type') > 0:
                        if search_for_best_weapon_over(options, 'CLAWS') == 'MAIN_HAND':
                            if int(options['inventory']['main_hand']['strength']*(float(options['player']['next_attack'])/3)) >= options['enemy']['health']:
                                return 'x'
                        elif search_for_best_weapon_over(options, 'CLAWS') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'CLAWS') != 'OFF_HAND':
                            if int(options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options,'CLAWS')]]['strength']*(float(options['player']['next_attack'])/3))>=options['enemy']['health']:

                                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options,'CLAWS')
                                return '1'
                    elif num_weapon(options, 'CLUB', 'type') > 0:
                        if search_for_best_weapon_over(options, 'CLUB') == 'MAIN_HAND':
                            if int(options['inventory']['main_hand']['strength']*(float(options['player']['next_attack'])/3)) >= options['enemy']['health']:
                                return 'x'
                        elif search_for_best_weapon_over(options, 'CLUB') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'CLUB') != 'OFF_HAND':
                            if int(options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options,'CLUB')]]['strength']*(float(options['player']['next_attack'])/3))>=options['enemy']['health']:

                                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options,'CLUB')
                                return '1'
                    elif num_weapon(options, 'SWORD', 'type') > 0:
                        if search_for_best_weapon_over(options, 'SWORD') == 'MAIN_HAND':
                            if int(options['inventory']['main_hand']['strength']*(float(options['player']['next_attack'])/3)) >= options['enemy']['health']:
                                return 'x'
                        elif search_for_best_weapon_over(options, 'SWORD') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'SWORD') != 'OFF_HAND':
                            if int(options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options,'SWORD')]]['strength']*(float(options['player']['next_attack'])/3))>=options['enemy']['health']:

                                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options,'SWORD')
                                return '1'

                    if options['future']['blocks'][0] == True:
                        return 'c'
        ACTION_INFO['shoot'] = False
        #attack
        if num_weapon(options, 'CLAWS', 'type') > 0:
            if search_for_best_weapon_over(options, 'CLAWS') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'CLAWS') != 'OFF_HAND':
                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'CLAWS')
                return '1'
            elif search_for_best_weapon_over(options, 'CLAWS') == 'OFF_HAND':
                if num_weapon(options, 'SHIELD', 'type') > 0:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SHIELD')
                    return '2'
        elif num_weapon(options, 'CLUB', 'type') > 0:
            if search_for_best_weapon_over(options, 'CLUB') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'CLUB') != 'OFF_HAND':
                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'CLUB')
                return '1'
            elif search_for_best_weapon_over(options, 'CLUB') == 'OFF_HAND':
                if num_weapon(options, 'SHIELD', 'type') > 0:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SHIELD')
                    return '2'
        elif num_weapon(options, 'SWORD', 'type') > 0 and num_weapon(options, 'BOW', 'type') >0:
            if search_for_best_weapon_over(options, 'SWORD') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'SWORD') != 'OFF_HAND' and search_for_best_weapon_over(options, 'BOW') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'BOW') != 'OFF_HAND':
                if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options, 'SWORD')]]['strength'] >= options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options, 'BOW')]]['strength']:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SWORD')
                    return '1'
                else:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'BOW')
                    ACTION_INFO['shoot'] = True
                    return '1'
            elif search_for_best_weapon_over(options, 'SWORD') == 'MAIN_HAND' and search_for_best_weapon_over(options, 'BOW') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'BOW') != 'OFF_HAND':
                if options['inventory']['main_hand']['strength'] < options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options, 'BOW')]]['strength']:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'BOW')
                    ACTION_INFO['shoot'] = True
                    return '1'
            elif search_for_best_weapon_over(options, 'SWORD') == 'OFF_HAND' and search_for_best_weapon_over(options, 'BOW') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'BOW') != 'OFF_HAND':

                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'BOW')
                ACTION_INFO['shoot'] = True
                return '1'
            elif search_for_best_weapon_over(options, 'BOW') == 'MAIN_HAND' and search_for_best_weapon_over(options, 'SWORD') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'SWORD') != 'OFF_HAND':
                if options['inventory']['backpack_weapons'][options['inventory']['backpack_weapons'].keys()[search_for_best_weapon_over(options, 'SWORD')]]['strength'] >= options['inventory']['main_hand']['strength']:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SWORD')
                    return '1'
        elif num_weapon(options, 'SWORD', 'type') > 0:
            if search_for_best_weapon_over(options, 'SWORD') != 'MAIN_HAND' and search_for_best_weapon_over(options, 'SWORD') != 'OFF_HAND':
                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SWORD')
                return '1'
            elif search_for_best_weapon_over(options, 'SWORD') == 'OFF_HAND':
                if num_weapon(options, 'SHIELD', 'type') > 0:
                    ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'SHIELD')
                    return '2'
        elif num_weapon(options, 'BOW', 'type') > 0:
             if search_for_best_weapon_over(options, 'BOW') != 'MAIN_HAND':
                ACTION_INFO['source_hand'] = search_for_best_weapon_over(options, 'BOW')
                ACTION_INFO['shoot'] = True
                return '1'

        return 'x'
























    """
    Return 'x' to attack the enemy
    Return 'c' to defend against the enemy's next attack
    Return 'i' to use a potion and heal yourself
    Return 'e' to use a Babylon Candle and attempt to escape combat
    NEW: Return 'f' to use a fireball and attack the enemy
    NEW: Return '1' to swap one of your weapons to your Main Hand, you may only swap 
         if your 'backpack_weapons' is not empty
    NEW: Return '2' to swap one of your weapons to your Off-Hand, you may only swap 
         if your 'backpack_weapons' is not empty
    """

    return 'x'

def movement_action(options):
    global ACTION_INFO # Necessary for reading and writing the global ACTION_INFO dictionary
    #potion
    if options['player']['health'] <= 25 and options['inventory']['potions'] > 0:
        return 'i'

    # use repel

    if options['player']['health'] <= 250 and options['inventory']['repels'] > 0 and options['inventory']['potions'] == 0 and options['invuln_steps'] == 0:

        return 'r'

    #use potions
    if options['map_danger'] - options['hide_danger'] > 2 and options['hide_danger'] <= 4:
        return 'h'

    #walk
    return 'x'
    """
    Return 'w', 'a', 's', 'd', or 'x' to navigate around the map
    Return 'i' to use a potion and heal
    Return 'h' to hide
    NEW: Return 'r' to use a repel potion
    """

    return random.choice(['w', 'a', 's', 'd'])

def item_action(options):   
    global ACTION_INFO # Necessary for reading and writing the global ACTION_INFO dictionary
    """
    Return '1' to place the item in your main hand
    Return '2' to place the item in your off-hand
    NEW: If your backpack is not full, you may return '8' to add the item to your backpack
         otherwise you may return a key from the 'backpack_weapons' dictionary to
         replace the item associated with that key
    NEW: Return '9' to ignore the item
    """
    i = num_weapon(options, "BOW", "type")
    isd = 0
    ii = 0
    j = num_weapon(options, "SWORD", "type")+ num_weapon(options, "CLUB", "type") + num_weapon(options, "CLAWS", "type")
    jsd = 0
    jj = 0
    k = num_weapon(options, "SHIELD", "type")
    ksd = 0
    kk = 0
    num = len(options["inventory"]['backpack_weapons'].keys())
    x = options["enemy"]['item']['strength']**2*options["enemy"]['item']['durability']
    if options['inventory']['off_hand'] is None and options['inventory']['main_hand'] is None:
        if num != 0:
            for a in range(1, 1 + num):
                if options["inventory"]['backpack_weapons'][str(a+2)]['type']=='BOW':
                    if ii == 0:
                       ii = a
                       isd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                    elif ii != 0:
                        if isd > options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']:
                            isd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                            ii = a
                elif options["inventory"]['backpack_weapons'][str(a+2)]['type']=='SWORD' or \
                        options["inventory"]['backpack_weapons'][str(a+2)]['type']=="CLAWS" or \
                        options["inventory"]['backpack_weapons'][str(a+2)]['type']=="CLUB":
                    if jj == 0:
                       jj = a
                       jsd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                    elif jj != 0:
                        if jsd > options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']:
                            jsd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                            jj = a
                elif options["inventory"]['backpack_weapons'][str(a+2)]['type']=='SHIELD':
                    if kk == 0:
                       kk = a
                       ksd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                    elif kk != 0:
                        if ksd > options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(a+2)]['durability']:
                            ksd = options["inventory"]['backpack_weapons'][str(a+2)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(a+2)]['durability']
                            kk = a

        if options["enemy"]['item']['type'] == 'BOW':
            if i == 0:
                return '8'
            elif i == 1:
                if isd < x:
                    return str(ii + 2)
                else:
                    return "9"
        elif options["enemy"]['item']['type'] == 'SWORD' or \
                    options["enemy"]['item']['type'] == "CLAWS" or \
                    options["enemy"]['item']['type'] == "CLUB":
            if j <= 2:
                return '8'
            elif j == 3:
                if jsd < x:
                    return str(jj + 2)
                else:
                    return "9"
        elif options["enemy"]['item']['type'] == 'SHIELD':
            if k <= 1:
                return '8'
            elif k == 2:
                if ksd < x:
                    return str(kk + 2)
                else:
                    return "9"

    elif options['inventory']['off_hand'] is not None and options['inventory']['main_hand'] is not None:
        if num != 0:
            for b in range(3,3+num):
                if options["inventory"]['backpack_weapons'][str(b)]['type']=='BOW':
                   if ii == 0:
                       ii = b
                       isd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']
                   elif ii != 0:
                        if isd > options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']:
                            isd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(b)]['durability']
                            ii = b
                elif options["inventory"]['backpack_weapons'][str(b)]['type']=='SWORD' or \
                        options["inventory"]['backpack_weapons'][str(b)]['type']=="CLAWS" or \
                        options["inventory"]['backpack_weapons'][str(b)]['type']=="CLUB":
                    if jj == 0:
                       jj = b
                       jsd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']
                    elif jj != 0:
                        if jsd > options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']:
                            jsd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(b)]['durability']
                            jj = b
                elif options["inventory"]['backpack_weapons'][str(b)]['type']=='SHIELD':
                    if kk == 0:
                       kk = b
                       ksd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']
                    elif kk != 0:
                        if ksd > options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(b)]['durability']:
                            ksd = options["inventory"]['backpack_weapons'][str(b)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(b)]['durability']
                            kk = b

        if options["enemy"]['item']['type'] == 'BOW':
            if i == 0:
                return '8'
            elif i == 1:
                if isd < x:
                    return str(ii)
                else:
                    return "9"
        elif options["enemy"]['item']['type'] == 'SWORD' or \
                options["enemy"]['item']['type'] == "CLAWS" or \
                options["enemy"]['item']['type'] == "CLUB":
            if j <= 2:
                return '8'
            elif j == 3:
                if options['inventory']['off_hand']['type']=='SHIELD':
                    if options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < jsd \
                            and options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < x:
                        return '1'
                    elif options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] > jsd \
                            and jsd < x:
                        return str(jj)
                    else:
                        return '9'
                elif options['inventory']['off_hand']['type']=='SWORD' or options['inventory']['off_hand']['type']=="CLAWS" or options['inventory']['off_hand']['type']=="CLUB":
                    if options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] \
                        < options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] \
                        and options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < jsd\
                        and options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < x:
                        return '1'
                    elif options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] \
                        < options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] \
                        and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < jsd\
                        and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < x:
                        return '2'
                    elif jsd < options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] \
                        and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] > jsd\
                        and jsd < x:
                        return str(jj)
                    else:
                        return '9'
        elif options["enemy"]['item']['type'] == 'SHIELD':
            if k <= 1:
                return '8'
            elif k == 2:
                if options['inventory']['off_hand']['type'] != 'SHIELD':
                    if x > ksd:
                        return str(kk)
                    else:
                        return '9'
                elif options['inventory']['off_hand']['type'] == 'SHIELD':
                    if options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < x \
                        and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < ksd:
                        return '2'
                    elif ksd < x \
                        and ksd < options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability']:
                        return str(kk)
                    else:
                        return '9'

    else:
        if options['inventory']['off_hand'] is None:
            if num != 0:
                for c in range(2,2+num):
                    if options["inventory"]['backpack_weapons'][str(c+1)]['type']=='BOW':
                        if ii == 0:
                            ii = c
                            isd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                        elif ii != 0:
                            if isd > options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']:
                                isd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                                ii = c
                    elif options["inventory"]['backpack_weapons'][str(c+1)]['type']=='SWORD' or \
                        options["inventory"]['backpack_weapons'][str(c+1)]['type']=="CLAWS" or \
                        options["inventory"]['backpack_weapons'][str(c+1)]['type']=="CLUB":
                        if jj == 0:
                            jj = c
                            jsd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                        elif jj != 0:
                            if jsd > options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']:
                                jsd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                                jj = c
                    elif options["inventory"]['backpack_weapons'][str(c+1)]['type']=='SHIELD':
                        if kk == 0:
                            kk = c
                            ksd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                        elif kk != 0:
                            if ksd > options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(c+1)]['durability']:
                                ksd = options["inventory"]['backpack_weapons'][str(c+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(c+1)]['durability']
                                kk = c

            if options["enemy"]['item']['type'] == 'BOW':
                if i == 0:
                    return "8"
                elif i == 1:
                    if options["inventory"]['main_hand']['type'] == "BOW":
                        if options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < x:
                            return "1"
                        else:
                            return "9"
                    elif options["inventory"]['main_hand']['type'] != "BOW":
                        if isd < x:
                            return str(ii+1)

            elif options["enemy"]['item']['type'] == 'SWORD' or \
                    options["enemy"]['item']['type'] == "CLAWS" or \
                    options["enemy"]['item']['type'] == "CLUB":
                if j <=2:
                    return "8"
                elif j ==3:
                    if options["inventory"]['main_hand']['type'] == 'SWORD' or \
                            options["inventory"]['main_hand']['type'] == "CLAWS" or \
                            options["inventory"]['main_hand']['type'] == "CLUB":
                        if options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < x \
                                and options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability'] < jsd:
                            return '1'
                        elif jsd < x \
                            and jsd < options['inventory']['main_hand']['strength']**2*options['inventory']['main_hand']['durability']:
                            return str(jj + 1)
                        else:
                            return '9'
                    elif options["inventory"]['main_hand']['type'] != 'SWORD' and \
                            options["inventory"]['main_hand']['type'] != "CLAWS" and \
                            options["inventory"]['main_hand']['type'] != "CLUB":
                        if jsd < x:
                            return str(jj+1)

            elif options["enemy"]['item']['type'] == 'SHIELD':
                if k <= 1:
                    return "8"
                elif k == 2:
                    if x < ksd:
                        return "9"
                    else:
                        return str(kk+1)



        elif options['inventory']['main_hand'] is None:
            if num != 0:
                for d in range(2,2+num):
                    if options["inventory"]['backpack_weapons'][str(d+1)]['type']=='BOW':
                        if ii == 0:
                            ii = d
                            isd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                        elif ii != 0:
                            if isd > options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(d+1)]['durability']:
                                isd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                                ii = d
                    elif options["inventory"]['backpack_weapons'][str(d+1)]['type']=='SWORD' or \
                        options["inventory"]['backpack_weapons'][str(d+1)]['type']=="CLAWS" or \
                        options["inventory"]['backpack_weapons'][str(d+1)]['type']=="CLUB":
                        if jj == 0:
                            jj = d
                            jsd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                        elif jj != 0:
                            if jsd > options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(d+1)]['durability']:
                                jsd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                                jj = d
                    elif options["inventory"]['backpack_weapons'][str(d+1)]['type']=='SHIELD':
                        if kk == 0:
                            kk = d
                            ksd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                            *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                        elif kk != 0:
                            if ksd > options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                *options["inventory"]['backpack_weapons'][str(d+1)]['durability']:
                                ksd = options["inventory"]['backpack_weapons'][str(d+1)]['strength']**2\
                                    *options["inventory"]['backpack_weapons'][str(d+1)]['durability']
                                kk = d

            if options["enemy"]['item']['type'] == 'BOW':
                if i == 0:
                    return "8"
                elif i == 1:
                    if x < isd:
                        return "9"
                    else:
                        return str(ii+1)

            elif options["enemy"]['item']['type'] == 'SWORD' or \
                    options["enemy"]['item']['type'] == "CLAWS" or \
                    options["enemy"]['item']['type'] == "CLUB":
                if j <= 2:
                    return "8"
                elif j == 3:
                    if options["inventory"]['off_hand']['type'] == 'SWORD' or \
                            options["inventory"]['off_hand']['type'] == "CLAWS" or \
                            options["inventory"]['off_hand']['type'] == "CLUB":
                        if options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < x \
                                and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < jsd:
                            return '2'
                        elif jsd < x \
                                and jsd < options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability']:
                            return str(jj + 1)
                        else:
                            return '9'
                    elif options["inventory"]['off_hand']['type'] != 'SWORD' and \
                            options["inventory"]['off_hand']['type'] != "CLAWS" and \
                            options["inventory"]['off_hand']['type'] != "CLUB":
                        if jsd < x:
                            return str(jj + 1)
                        else:
                            return '9'

            elif options["enemy"]['item']['type'] == 'SHIELD':
                if k <= 1:
                    return '8'
                elif k == 2:
                    if options["inventory"]['off_hand']['type'] == "SHIELD":
                        if options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < x \
                                and options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability'] < ksd:
                            return '2'
                        elif ksd < x \
                                and ksd < options['inventory']['off_hand']['strength']**2*options['inventory']['off_hand']['durability']:
                            return str(kk + 1)
                        else:
                            return '9'
                    elif options["inventory"]['off_hand']['type'] != "SHIELD":
                        if ksd < x:
                            return str(kk + 1)
                        else:
                            return '9'


    return '9'


def swap_select_weapon(options):
    global ACTION_INFO # Necessary for reading and writing the global ACTION_INFO dictionary
    """
    *** NEW FUNCTION AND SCENARIO ***
    *** Called during the SWAP scenario ***
    Return one of the keys from the 'backpack_weapons' dictionary to place that item
        in 'swap_weapon_to_hand'
    WARNING: The only valid values you may return are the keys in the 'backpack_weapons'
             dictionary!
    WARNING: If the weapon you choose cannot be placed in 'swap_weapon_to_hand' your 
             the swap will not be succesfful and your combat_action() function will be 
             called again
    """
    return options['inventory']['backpack_weapons'].keys()[ACTION_INFO['source_hand']]




#####################################################################################
#                Game Driver for your AI. Don't modify this section.                #
#####################################################################################
def _check_loop():                                                                  #
    raw_input()                                                                     #
    USE_AI = False                                                                  #
                                                                                    #
class User(object):                                                                 #
    def __init__(self):                                                             #
        self.input_check = None                                                     #
        self.set_ai(USE_AI)                                                         #
                                                                                    #
    def select(self, options):                                                      #
        if options['situation'] == 'COMBAT': return combat_action(options)          #
        elif options['situation'] == 'ITEM': return item_action(options)            #
        elif options['situation'] == 'MOVE': return movement_action(options)        #
        elif options['situation'] == 'SWAP': return swap_select_weapon(options)     #
        else: raise Exception("Bad move option: {0}".format(options['situation']))  #
                                                                                    #
    def set_ai(self, setting):                                                      #
        global USE_AI                                                               #
        if setting:                                                                 #
            # launch subprocess to handle input                                     #
            USE_AI = True                                                           #
            self.input_check = threading.Thread(target=_check_loop)                 #
            self.input_check.daemon = True                                          #
            self.input_check.start()                                                #
        else:                                                                       #
            # end the subprocess                                                    #
            if self.input_check and self.input_check.is_alive():                    #
                self.input_check.join(GAME_SPEED)                                   #
            USE_AI = False                                                          #
                                                                                    #
                                                                                    #
    def __move__(self, options):                                                    #
        if not USE_AI:                                                              #
            usr = getch()                                                           #
            if ord(usr) == 13:                                                      #
                self.set_ai(True)                                                   #
                return self.select(options).lower()                                 #
            return usr.lower()                                                      #
                                                                                    #
        time.sleep(GAME_SPEED)                                                      #
        if self.input_check and not self.input_check.is_alive():                    #
            self.set_ai(False)                                                      #
            return getch().lower()                                                  #
        return self.select(options).lower()                                         #
                                                                                    #
                                                                                    #
#####################################################################################
