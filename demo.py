# -*- coding: utf-8 -*-


"""
No actual tests for now, just a demo of what can be done.
"""


import ojm


class Human(ojm.Model):
    def __init__(self, name=None, age=None):
        super().__init__()

        self.name = name
        self.age = age
        self.embedded_organs = []
        self.linked_human = None

    def add_organ(self, organ):
        self.embedded_organs.append(organ)


class Organ(ojm.Model):
    def __init__(self, name=None):
        super().__init__()

        self.name = name


# Register models
ojm.register(Human)
ojm.register(Organ)


# Demo

john = Human('John Doe', 42)
john.add_organ(Organ('heart'))
john.save()

# `duplicate()` is required to later save this new instance
jane = Human.load(john.uuid).duplicate()
jane.name = 'Jane Doe'
print(jane.age)  # 42
print(jane.embedded_organs[0].name)  # heart
jane.save()


jane.linked_human = john
jane.update()

print(Human.load(jane.uuid).linked_human.name)  # John Doe
