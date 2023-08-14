> This is bs, ima use dynaconf

# Concept

The core concept is, to have instances of dataclasses that hold all values. On programm start the values are just overridden by those in the file.

## Dataclass Structure

You have one [File](#file) class, that contains a list of [Section](#section) classes.  
Every [Section](#section) class contains a list of [SectionElement](#section-elements) classes.

# Classes

## File

`File` classes have one name, with whom the path will be generated:

```
{CONFIG_DIR}/{file_name}.conf
```

I also pass in the config direcory in the constructor, such that the module can be pretty independently used. Though it's default value is the default config director from `utils.path_manager`.


They contain a list of [ConfigElement](#config-elements)s, arguably the most important ones.

## Config Elements

# Config Syntax

- every line is stripped from all whitespaces at the beginning and end

```
# a comment

config_name=some_value

# list
[config_name.list.start]
config_name=one list item
config_name=another list item
[config_name.list.end]

# dict
[config_name.dict.start]
one_key=one value item
another_key=another value item
[config_name.dict.end]
```

- empty lines will be ignored
- If `#` is at the beginning of the line, it will be ignored
- if there is neither a `\[.*\]` or a `=` in a line, it will raise a warning, but will be ignored 
