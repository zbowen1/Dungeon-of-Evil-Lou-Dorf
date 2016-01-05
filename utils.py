from dungeon_generator import getEntrance
from asciiart import *
from getch import getch
from ai import USE_AI, STORY_MODE
from constants import *
import time
import pprint

def printBattlefield(img, img2, width, height):
    final_image = []
    image = img.split("\n")
    image2 = img2.split("\n")
    if len(image) > height:
        return ["BAD IMAGE SPLIT"] * height
    if len(image2) > height:
        return ["BAD IMAGE2 SPLIT"] * height
    if len(image) < height:
        for i in range(height - len(image)): image.insert(0, "|")
    if len(image2) < height:
        for i in range(height - len(image2)): image2.append("|")
    for i in range(height):
        final_image.append(image[i] + " " * (width + 1 - len(image[i]) - len(image2[i])) + image2[i]) 

    for line in final_image:
        print line


def printMessageBox(message):
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    msg = message.split("\n")
    for i in range(min(8, len(msg))):
        print "| {0:159s} |".format(msg[i])
    if len(msg) < 8:
        for i in range(8 - len(msg)):
            print "| {0:159s} |".format("")
    print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

def printHelpScreen(data):
    if 'blocks' in data['future']:
        data['future']['blocks'] = ', '.join([str(x) for x in data['future']['blocks']])
        data['future']['escapes'] = ', '.join([str(x) for x in data['future']['escapes']])
    if 'enemies' in data['future']:
        for i in range(len(data['future'])):
            data['future']['enemies'][i] = str(data['future']['enemies'][i])
    output = pprint.pformat(data).split("\n")
    if 'enemies' in data['future']:
        counter = len(output)
        for i in range(counter):
            if 'enemies' in output[i]:
                current = output[i].split(':')
                before, after = current[0] + ':' + current[1] + ':', ':'.join(current[2:])
                output = output[0:i] + [before, after] + output[i+1:]
        for i in range(len(output)):
            if 'item' in output[i]:
                output[i] = (' ' * (3 if output[i][0] == '[' else 4)) + output[i].lstrip()
    for i in range(15): print
    print HELP_HEADER
    for line in output:
        print "| {0:<159s} |".format(line)
    for i in range(38 - len(output)):
        print "|" + " " * 161 + "|"
    print "- " * (MAP_WIDTH + 2)

def printSeerData(info):
    pattacks = "Strength of Next {0} Player Attacks:".format(ADVANCE_LEN)
    eattacks = "Strength of Next {0} Enemy Attacks:".format(ADVANCE_LEN)
    blocks = "Result of Next {0} Player Blocks:".format(ADVANCE_LEN)
    escapes = "Result of Next {0} Player Escapes:".format(ADVANCE_LEN)
    drop = "Will the enemy drop their item?"
    for i in range(45): print
    print HELP_HEADER
    print pattacks + "-" * (163 - len(pattacks))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[STRENGTHNAMES[x] for x in info['player_attacks']]) + " |"
    print eattacks + "-" * (163 - len(eattacks))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[STRENGTHNAMES[x] for x in info['enemy_attacks']]) + " |"
    print blocks + "-" * (163 - len(blocks))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[str(x) for x in info['blocks']]) + " |"
    print escapes + "-" * (163 - len(escapes))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[str(x) for x in info['escapes']]) + " |"
    print drop + "-" * (163 - len(drop))
    print "|{0:<155s}|".format("\t" + str(info['will_drop']))
    print "-" * 163
    for i in range(27): print "|" + " " * 161 + "|"
    print "- " * (MAP_WIDTH + 2)

def printMapSeerData(info):
    mapdanger = "Next {0} Values for Map Danger".format(ADVANCE_LEN)
    hidedanger = "Next {0} Values for Hide Danger".format(ADVANCE_LEN)
    escapechance = "Next {0} Values for Escape Chance".format(ADVANCE_LEN)
    nextenemies = "Next {0} Enemies to be Encountered".format(ADVANCE_LEN)
    for i in range(45): print
    print HELP_HEADER
    print mapdanger + "-" * (163 - len(mapdanger))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[DANGERS[x] for x in info['map_danger']]) + " |"
    print hidedanger + "-" * (163 - len(hidedanger))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[DANGERS[x] for x in info['hide_danger']]) + " |"
    print escapechance + "-" * (163 - len(escapechance))
    print "| " + " | ".join(["{:^15s}"] * ADVANCE_LEN).format(*[PROBS[x] for x in info['escapes']]) + " |"
    print nextenemies + "-" * (163 - len(nextenemies)) 
    enemies = pprint.pformat([{"name": x['name'], "health": x['health'], "item": x['item']} for x in info['enemies']]).split("\n")
    for line in enemies:
        print "| {0:<159s} |".format(line)
    for i in range(31 - len(enemies)):
        print "|" + " " * 161 + "|"
    print "- " * (MAP_WIDTH + 2)

def entranceAnimation():
    outside = getEntrance()
    for i in range(15): print
    for line in outside:
        print ''.join(line)
    print "Press [ENTER] to begin your adventure..."
    if not USE_AI: getch()
    player_x = 30
    player_y = 79
    old = outside[player_x][player_y]
    outside[player_x][player_y] = 'X'
    for i in range(15): print
    for line in outside:
        print ''.join(line)
    time.sleep(.5)
    while (player_x > 14):
        outside[player_x][player_y] = old
        player_x -= 1
        old = outside[player_x][player_y]
        outside[player_x][player_y] = 'X'
        for i in range(15): print
        for line in outside:
            print ''.join(line)
        time.sleep(.25)
    time.sleep(1)
    for i in range(15): print
    for i in range(22):
        print
    print " " * 70 + "Begin"
    for i in range(22):
        print
    time.sleep(2)


def exitAnimation():
    outside = getEntrance()
    for i in range(15): print
    for line in outside:
        print ''.join(line)
