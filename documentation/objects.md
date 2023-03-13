# music_kraken.objects

## DatabaseObject

[music_kraken.objects.DatabaseObject](../src/music_kraken/objects/parents.py)

This is a parent object, which most Music-Objects inherit from. It provides the **functionality** to:

- autogenerate id's *(UUID)*, if not passed in the constructur.
- [merge](#databaseobjectmerge) the data of another instance of the same time in self.
- Check if two different instances of the same type represent the same data, using `__eq__`.

Additionally it provides an **Interface** to:

- define the attributes used to [merge](#databaseobjectmerge).
- define the attribuse and values used to check for equal data. *(used in `__eq__` and in the merge)*
- get the id3 [metadata](#metadata).
- get all [options](#options) *(used in searching from e.g. the command line)*

### DatabaseObject.merge()

## Collection

[music_kraken.objects.Collection](../src/music_kraken/objects/collection.py)

This is an object, which acts as a list. You can save instaces of a subclass of [DatabaseObject](#databaseobject).

Then you can for example append a new Object. The difference to a normal list is, that if you have two different objects that both represent the same data, it doesn't get added, but all data gets [merged](#databaseobjectmerge) into the existing Object instead.

For example, you have two different Artist-Objects, where both have one source in common. The one Artist-Object already is in the Collection. The other artist object is passed in the append command.  
In this case it doesn't simply add the artist object to the collection, but modifies the already existing Artist-Object, adding all attributes the new artist object has, and then discards the other object.

```python
artist_collection = Collection(element_type=Artist)

# adds the artist to the list (len 1)
artist_collection.append(artist_1)

# detects artist 2 has a mutual source
# thus not adding but mergin (len 1)
artist_collection.appent(artist_2)
```

Function | Explanation
---|---
`append()` | appends an object to the collection
`extend()` | appends a list of objects to the collection
`__len__()` | gets the ammount of objects in collection
`shallow_list` | gets a shallow copy of the list `_data` the objects are contained in
`sort()` | takes the same arguments than `list.sort`, and does the same
`__iter__()` | allows you to use collections e.g. a for loop

## Options

## Metadata
