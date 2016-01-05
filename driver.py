from asciiart import *
from weapons import *
from constants import *
from maps import *
from utils import *
from game import *
from getch import getch
from dungeon_generator import *
import asciiart
import random, time, sys
from docopt import docopt

doc = """
Usage:
    driver.py
    driver.py (-b <n> | --batch <n>) [-s | --seed]

Options:
    -b <n>, --batch <n>  Run the game back to back <n> times
    -s, --seed  Run the game using a seed
"""

DIRS = {
    'w': 'UP',
    'a': 'LEFT',
    's': 'DOWN',
    'd': 'RIGHT',
}

def main(seed=None):
    from ai import USE_AI, STORY_MODE

    if seed == None:
        random.seed()
    else:
        random.seed(seed)

    if STORY_MODE:
        pass #entranceAnimation()

    VICTORY = 2
    GOOD = 1
    ERROR = 0

    game = Game()
    userMove = '\0'
    message_list = []
    while (userMove != 'q'):
        from ai import USE_AI, STORY_MODE
        resultOfMove = GOOD
        message = ''
        if message_list:
            assert(len(message_list) == 1)
            message = message_list[0]
            message_list = []
        game.map.printMap(game.danger, game.player.health, game.inventory.miscitems["Potions"], message, 
            (game.level if game.level < (AMULET_LEVEL + 1) else ((AMULET_LEVEL + 1) - (game.level % (AMULET_LEVEL + 1)) - 1)) if STORY_MODE else game.level,
            game.steps_left, game.hide_danger, game.escape_chance, game.escapes_remaining, game.inventory.miscitems["Fireballs"], game.inventory.miscitems["Repel"],
            game.invuln_turns)
        #handle move
        userMove = game.user.__move__(game.getDataForAI("MOVE"))
        try:
            if userMove == 'o':
                printHelpScreen(game.getDataForAI("MOVE"))
                while getch() != 'o': print "Press 'o' to return to the game!"
            if userMove == 'p':
                printMapSeerData(game.seerdata.get_info("MOVE", game.enemy_factory, [game.danger] + game.dangers, [game.hide_danger] + game.hide_dangers, [game.escape_chance] + game.escape_chances))
                while getch() != 'p': print "Press 'p' to return to the game!"
            if userMove in ['w', 's', 'a', 'd']:
                game.map._visited = set()
                resultOfMove = game.move(DIRS[userMove])
                if resultOfMove == GOOD:
                    game.takeStep()
            elif userMove == 'r':
                item_type = "Repel"
                result = game.inventory.use_misc(item_type)
                if result:
                    game.invuln_turns += ITEM_STRENGTHS[item_type]
                    message_list.append("You drink one of your Repels. You suddenly feel very unappealing...")
                else:
                    message_list.append("You don't have any more Repel!")
            elif userMove == 'i':
                item_type = "Potions"
                result = game.inventory.use_misc(item_type)
                # TODO: Not yet fully implemented for things other than Potions
                if result:
                    game.player.health = min(result + game.player.health, PLAYER_MAX_HEALTH)
                    message_list.append("You drank a potion and recovered {} health!".format(result))
                else:
                    message_list.append("You don't have any Potions!")
                    #resultOfMove = ERROR
            elif userMove == 'h':
                if not game.player.hiding:
                    game.takeStep()
                    game.move("HIDE")
                    message_list.append(HIDING_MSGS[random.randint(0,len(HIDING_MSGS) - 1)])
            elif userMove == 'x':
                path = game.map.findPath()
                assert(path != None)
                game.map._visited.add(game.map.player)
                if path[0][0] < game.map.player[0]:
                    resultOfMove = game.move("UP")
                elif path[0][0] > game.map.player[0]:
                    resultOfMove = game.move("DOWN")
                elif path[0][1] < game.map.player[1]:
                    resultOfMove = game.move("LEFT")
                elif path[0][1] > game.map.player[1]:
                    resultOfMove = game.move("RIGHT")
                else:
                    raise Exception("Find Path returned player's current square")
                game.takeStep()
            else:
                resultOfMove = ERROR
            if resultOfMove == VICTORY:
                game.levelUp()
                if not STORY_MODE:
                    if not ((game.level) % 10):
                        game.encounter_sdorf = True
                else:
                    # story mode
                    if game.level == AMULET_LEVEL + 1:
                        # found the amulet
                        for i in range(22): print
                        print " " * 60 + "You've found the Amulet of Awesomeness! Escape while you still can!".format(
                            (game.level if game.level < (AMULET_LEVEL + 1) else ((AMULET_LEVEL + 1) - (game.level % (AMULET_LEVEL + 1)) - 1)))
                        for i in range(22): print
                        if not USE_AI: 
                            print "Press [ENTER] to continue..."
                            getch()

                    if game.level == AMULET_LEVEL * 2 + 1:
                        raise Victory("You have defeated the Fortress of Dorf!")
                    else:
                        for i in range(22): print
                        print " " * 70 + "Fortress of Dorf: Floor {0}".format(
                            (game.level if game.level < (AMULET_LEVEL + 1) else ((AMULET_LEVEL + 1) - (game.level % (AMULET_LEVEL + 1)) - 1)))
                        for i in range(22): print
                        if not USE_AI: 
                            print "Press [ENTER] to continue..."
                            getch()
                game.map = Map(game.level)
                while game.map.findPath() == None:
                    game.map = Map(game.level)
            elif resultOfMove == GOOD: 
                game.update_danger()
                pass
            elif resultOfMove == ERROR:
                message_list.append("Sorry, you can't do that!") 
        except Defeat as e:
            for i in range(22): print
            if not STORY_MODE:
                # print statistics
                print " " * 50 + "AI Results: {0} Levels Completed.".format(game.level)
            else:
                print " " * 60 + str(e)
            for i in range(22): print
            if not STORY_MODE:
                return game.level
            else:
                return 0
            # sys.exit()
        except Victory as e:
            # exitAnimation()
            for i in range(22): print
            print " " * 60 + str(e)
            for i in range(22): print
            # sys.exit()
            return 1
        except Quit as e:
            break

    # user quit the game
    print "Bye"
    return 0

if __name__ == "__main__":
    from ai import STORY_MODE

    args = docopt(doc)
    numGames = 1
    if '--batch' in args:
        try:
            numGames = int(args['--batch'])
        except:
            numGames = 1
    if numGames == 1:
        main()
    else:
        gameReturns = []
        for i in range(numGames):
            if ('-s' in args and args['-s']) or \
                ('--seed' in args and args['--seed']):
                gameReturns.append(main(i))
            else:
                gameReturns.append(main())
        
        if STORY_MODE:
            print 'Your AI completed {0:.2f}% runs of story mode!'.format(sum(gameReturns) / float(numGames) * 100)
        else:
            print 'Your AI completed an average of {0:.2f} levels of gauntlet mode (over {1} runs)'.format(sum(gameReturns) / float(numGames), numGames)
