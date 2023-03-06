class SuperFoo:
    ATTRIBUTES: tuple = tuple()

class Foo(SuperFoo):
    def __init__(self, bar1, bar2, bar3) -> None:
        self.bar1 = bar1
        self.bar2 = bar2
        self.bar3 = bar3
        
    ATTRIBUTES: tuple = ("bar1", "bar2", "bar3")
    
    
def process(child_instance: SuperFoo):
    for attribute in child_instance.ATTRIBUTES:
        print(getattr(child_instance, attribute))
        
process(Foo(123, 456, 789))
        
"""
Hi!

I got following code *(It is a very simplified and broken down example)*:

```python
class SuperFoo:
    ATTRIBUTES: tuple = tuple()

class Foo(SuperFoo):
    def __init__(self, bar1, bar2, bar3) -> None:
        self.bar1 = bar1
        self.bar2 = bar2
        self.bar3 = bar3
        
    ATTRIBUTES: tuple = (Foo.bar1, Foo.bar2, Foo.bar3)    
    
    
def process(child_instance: SuperFoo):
    for attribute in child_instance.ATTRIBUTES:
        print(getattr(child_instance, attribute))
        
process(Foo(123, 456, 789))
```

the output I expect would be:

```
> 123
> 456
> 789
```

Obviously this doesn't work, instead the IDE warns me that `Foo` is not defined, and the error which is raised says so as well.

```
ATTRIBUTES: tuple = (Foo.bar1, Foo.bar2, Foo.bar3)    
NameError: name 'Foo' is not defined
```

While I completely get why this happens, I have no clue how to solve it.
Any help would be appreciated.
"""