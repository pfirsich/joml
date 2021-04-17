# General
This format is not intended to exchange structured data read and written by machines (like JSON is commonly used as), but rather as a format read and written by people and read by machines.

It should be easy to integrate, which means that a fully specification conformant parser should be easy to write and fairly small.

It's essentially a saner YAML/JSON (for humans) hybrid with a bunch of stuff taken from the TOML spec.

* UTF-8
* keys are case-sensitive
* Newline is LF or CR (should I just allow LF and CR LF?)

# Notes For Later
## Mandatory String Quotation
optional quotation would make this invalid (the comma separator is at fault):
```yaml
key1: this is a sentence, that I really like
key2: something
```

I severely dislike that magic value (like true, false maybe null) can only be identified after being parsed as a string. If you have a subtly malformed number, it would also just be interpreted as a string (e.g. `1ê-6` or maybe some invisible unicode codepoints/whitespace in there), when you actually want an error.

# Open Questions
## Null
Should simply not defining a value result in a special null value? (e.g. `key1:`). *I don't like this*
Should there be a way to represent a special null value explicitly? (e.g. `key1: null`).
Should this value be different from the absence of a value?

# Comments
A single-comment starts wherever a `#` or `//` occurs wherever it is not part of a double-quoted string and ends with newline, everything between that is a comment

A multi-line comment behaves the same, but starts with `/*` and ends with `*/`.

# Key/Value Pair
Key must be string (may be quoted)
```yaml
key2: "value2"
keys are strings and can contain spaces: true
"they may be ::\"quoted\"::, too": true
```
K/V pairs may be separated by newline, or a comma!
```yaml
key1: "value1", key2: "value2"
```

# Strings
```yaml
#str0: double quotes are optional
str1: "Enclosed in double-quotes"
str2: "Escape \"quote\" and backslash \\ with backslash"
str3: "Arbitrary byte sequence with \x00\x01\x02"
strm1: "Multi
Line
String"
strm2: "\ # Trim whitespace with trailing backslash
    Multi \
    Line \
    String\
    "
```

# Numbers
```yaml
num1: +1
num2: 2
num3: -12
num4: 0xbaadf00d
num5: 0o0123567
num6: 0b1110101
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

# Boolean
```yaml
bool1: true
bool1: false
```

# Array
Surrounded by []. Values separated by newline or comma
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

# Dictionary
The document itself is a dictionary. Surrounded by {}. Same rules regarding separation
```yaml
point: {x: 1, y: 2}
colors: {
    background: [255, 255, 255]
    text: [0, 0, 0]
}
```
