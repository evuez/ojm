# OJM: Object JSON Mapping?

Allows you to save Python objects to JSON files.

It's an old piece of code, it seems to kinda work, but the code isn't what you'd call "pretty".

# Demo

See `demo.py` for full classes definition.

```python
import ojm

# Define classes...

class Human(ojm.Model):
    # ...

class Organ(ojm.Model):
    # ...


# Register models
ojm.register(Human)
ojm.register(Organ)


# Have fun!

john = Human('John Doe', 42)
john.add_organ(Organ('heart'))
john.save()

# `duplicate()` is required to later save this new instance
jane = Human.load(john.uuid).duplicate()
jane.name = 'Jane Doe'
print(jane.embedded_organs[0].name)  # heart
jane.save()


jane.linked_human = john
jane.update()

print(Human.load(jane.uuid).linked_human.name)  # John Doe

```
