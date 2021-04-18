# JOML
## Introduction
This format is not intended to exchange structured data read and written by machines (like JSON is commonly used for), but rather as a format read and written by people and read by machines (like TOML and YAML).

It should be easy to integrate, which means that a fully specification conformant parser should be easy to write and fairly small. To state it clearly: A key goal is simplicty.

It's essentially a saner YAML/JSON (for humans) hybrid with **a bunch** of stuff taken from the TOML spec.

## Encoding
* UTF-8
* Newline is LF (0x0A) or CRLF (0x0D 0x0A)
* Whitespace is space (0x20) or tab (0x09)

## Comments
A single-comment starts wherever a `#` occurs outside of a string and ends with a newline.

## Key-Value Pairs
A key must be a string and may be quoted. They are case-sensitive. Values can be any of the ones described in the following sections.
```yaml
key2: "value2"
keys are strings and can contain spaces: true
"they may be ::\"quoted\"::, too": true
```

Key-value pairs may be separated by a newline or a comma:
```yaml
key1: "value1", key2: "value2"
```

## Null
`null` represents a special value and must be distinct from the case in which a key is simply missing.
```yaml
key: null
```

## Strings
Strings must be double quoted and may contain any of the following escape sequences:
```yaml
str1: "Enclosed in double-quotes"
str2: "Escape \"quote\" and backslash \\ with backslash"
str3: "Arbitrary byte sequence with \x00\x01\x02"
str4: "Unicode escapes: \u20ac (€) \U0001D49C (𝒜)"
str5: "Other escape characters: \t, \n, \r"
```

Multi-line strings also use double quotes and may use trimming
```yaml
strm1: "Multi
Line
String"
# Trim whitespace at the start of the following line with a trailing backslash
strm2: "\
    Multi\
    Line\
    String\
    "
strm3: "Multi\nLine\nString" # equivalent to the one above
```

## Numbers
### Integers
Integers are 64-bit signed integers.

```yaml
num1: +1
num2: 2
num3: -12
num4: 0xbaadf00d
num5: 0o0123567
num6: 0b1110101
```

### Floats
Floating point numbers are either IEEE754 binary32 (single) or IEEE754 binary64 (double) numbers.

```yaml
num7: +1.0
num8: 3.1415
num9: -0.01
num10: 1e-5
num11: 3E6
num12: 2.77e-3
num13: inf
num14: -inf
num15: nan
num15: -nan
```

Any NaN value (signalling NaN or quiet NaN, any sign and any payload bits) may be serialized as `nan` and `nan` may be deserialized to any NaN value too. `-nan` is allowed, but is equivalent to `nan`. Though you should not rely on it, is suggested to use a positive, quiet NaN with payload 0 (0x7fc00000 or 0x7ff8000000000000 for single and double respectively).

## Booleans
```yaml
bool1: true
bool1: false
```

## Arrays
Arrays are surrounded by `[` and `]`. Their values may also be separated by either a newline or a comma.
```yaml
array1: [1, 2, 3]
array2: ["heterogeneous", 1, "arrays", 2, "are", 3, "fine"]
array3: [
    "trailing",
    "comma",
    "is",
    "fine",
]
array4: [
    "newline"
    "are"
    "sufficient"
    "as"
    "separator"
]
```

## Dictionaries
The document itself is a dictionary.
Dictionaries other than the root of the document are surrounded by `{` and `}`.
The same rules (as for the document and for arrays) regarding separation of values apply.
```yaml
point: {x: 1, y: 2}
colors: {
    background: [255, 255, 255]
    text: [0, 0, 0]
}
```

## Parsers
I am developing a reference parser alongside this specification in [joml-cpp](https://github.com/pfirsich/joml-cpp).

## Open Questions
### Null
* Should simply not defining a value result in a special null value? (e.g. `key1:`). *I don't like this. It makes the parser more complicated and it often looks like a mistake.*
* Should there be a way to represent a special null value explicitly? (e.g. `key1: null`). *Plenty of people are lacking null in TOML, so I shall add it.*
* Should this value be different from the absence of a value? *Yes it should be different, because without it it, there would be less of a point for the whole feature. It gives you the option to "override" stuff as empty.*

### Newlines
* Should CRLF be supported? Probably for practicality reasons, but it's annoying to implement *Yes, Windows exists and Windows users are less likely to know what different line endings are.*

### Dictionaries
I think that dictionaries should absolutely be ordered. In that case duplicate keys can be easily resolved by having a later occurence override the earlier one. It remains to be decided whether all elements should be saved, only the latest (in the document) value of a duplicate key should be saved or whether an error should be generated if a key is used multiple times.

### Strings
* More escape characters? You can do most of them with \x if you have to. But maybe the common/convenient ones (the ones TOML supports: https://toml.io/en/v1.0.0#string - \b, \t, \n, \f, \r, \", \\. Most of these I have never ever used in over a decade of programming. My subset would be: \t, \n, \r, \", \\)? *Yes, I need more, because people will use them and then they will be confused when that didn't work.*
* Should escaping backlash only be necessary if the following character is not part of a valid escape sequence (so `"oof\oof"` is valid)? I think this is kinda cool, but can lead to sneaky errors, like when typing a windows path: `E:\Users\Joel\directory\notherdir\file` (\n is going to be a newline). *Using \ for an invalid escape sequence should always error. Different languages handle this differently, so that the end result could surprise people, which is not good.*
* Should there be literal strings (with single quotes) like TOML has them, where no escaping is performed? *No, I think it's really useful and nice to have, but not at all necessary and no one will ever do this "instinctively" and then be surprised that it doesn't work. Also if you don't quite know the language well enough, finding backslashes in literal strings might just look like a mistake. I might change my mind on this later.*
* Should I have unicode escape sequences? (`\uXXXX` and `\UXXXXXXXX`) *The best reason for doing this is that everyone has it and people will be surprised if it's not there and it doesn't add too much complexity by itself.*

### Comments
* Should I allow `//` and `/**/` comments? I'm not quite sure how necessary multi-line comments are. *Every usable editor on the planet will help you comment multiple lines trivially. The extra complexity, even if it is very little, cannot be justified. And if there are no C style multi-line comments, there should be no C-style single line comments either.*

### Types / Annotations
I would like to have had type-annotations in the past. Should it be possible to prepend values with a type (`position: (vec2) [0, 0], color: (color) [1, 0, 0]` or `bytes: <hex> "baadf00d"`) and the type name would be saved alongside the value.
If the type name is a builtin type, it will do conversions.
More examples:

```yaml
# Remove limitations of JOML, for example make a dict not allow unique keys
dict: (unique) {
    a: 1
    a: 2 # ERROR!
}

# Annotate how data should be used. For example whether an array should replace values or append to them.
settings: (replace) ["cool", "fancy"]
settings: (append) ["cool", "fancy"]
settings: (prepend) ["cool", "fancy"]

# If the annotation is just a string, you could decide to interpret the annotation as JOML itself.
# How to use annotations in there though? How does the annotation terminate?
# Maybe it should just always be JOML? But then there is no good way to allow simple type annotations (single word without any special characters).
position: (type: "vec2", synchronize: true, precision: "half") {
    x: 0,
    y: 0
}
```

This would be cool, but needs to be justified WELL, because it increases complexity. I am not at all decided on the syntax. I needed this a bunch of times, but I think it's contrary to the goals of this language (low complexity). Though it does open the doors for an arbitrary amount of extension with fairly little effort.

## Notes For Later
### Mandatory String Quotation
optional quotation would make this invalid (the comma separator is at fault):
```yaml
key1: this is a sentence, that I really like
key2: something
```

I severely dislike that magic values (like `true`, `false` and maybe `null`) can only be identified after being parsed as a string. If you have a subtly malformed number, it would also just be interpreted as a string (e.g. `1ê-6` or maybe some invisible unicode codepoints/whitespace in there), when you actually want an error.

### -nan
from IEEE-754 (2008):
```
Conversion of a quiet NaN in a supported format to an external character sequence shall produce a language-defined one of “nan” or a sequence that is equivalent except for case (e.g., “NaN”), with an optional preceding sign. (This standard does not interpret the sign of a NaN.)
```
The sign is not used and it's optional. I personally think that there is not much of a difference. Why should I keep the sign, when the payload is ignored?
