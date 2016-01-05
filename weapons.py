class GenericItemSelection(Exception):
    pass

class Item(object):
    def __init__(self):
        raise GenericItemSelection()

class Weapon(Item):
    def __init__(self, image, name, strength, durability):
        # later: kwargs
        self.image = image
        self.name = name
        self.strength = strength
        self.durability = durability

    def description(self):
        return {'name': self.name, 'strength': self.strength, 'type': self.image, 'durability': self.durability}

class MeleeWeapon(Weapon):
    def __init__(self, image, name,  strength, durability):
        super(MeleeWeapon, self).__init__(image, name, strength, durability)
        pass

class RangedWeapon(Weapon):
    def __init__(self, image, name, strength, durability):
        super(RangedWeapon, self).__init__(image, name, strength, durability)
        pass

class Defense(Weapon):
    def __init__(self, image, name, strength, durability):
        super(Defense, self).__init__(image, name, strength, durability)
        pass

