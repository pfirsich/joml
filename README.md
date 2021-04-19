# JOML
## Introduction
This format is not intended to exchange structured data read and written by machines (like JSON is commonly used for), but rather as a format read and written by people and read by machines (like TOML and YAML).

It should be easy to integrate, which means that a fully specification conformant parser should be easy to write and fairly small. To state it clearly: A key goal is simplicty.

It's essentially a saner subset of YAML or a JSON for configuration with **a bunch** of details taken from the TOML.

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
str5: "Other escape characters: \t, \n, \r, \f, \b" # the ones supported by JSON
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

## Libraries
I am developing a reference parser alongside this specification in [joml-cpp](https://github.com/pfirsich/joml-cpp).

## Alternatives
### JSON
JSON is good for serializing data. There is always only one way to express what you want to represent, which is a very good thing. But sadly, there are no comments, which almost always is already a complete deal breaker. There are also no multi-line strings and some syntactic annoyances, such as no trailing commas or mandatory quoting of keys. JSON is good for data, but rarely for configuration.

### YAML
YAML is really huge. I wanted to check how YAML does multi-line strings, when deciding on how I want to do them in JOML and it turns out, there are 9 ways to quote strings in YAML. You actually have to look stuff up, when reading YAML files sometimes and I am convinced this should not happen - It's just a configuration file. The spec is gigantic too of course and YAML parsers are famous for not implementing it completely or implementing it incorrectly.

### TOML
On the one hand it is simple, but it is also very complex and surprising at times.

This works:
```toml
dict = {a = 1, b = 2}
```

This doesn't:
```toml
dict = {
    a = 1,
    b = 2
}
```
You can't just express whatever you like and the things that you can express, sometimes have special syntax that frankly often just looks weird and is unwieldy. I have in the past decided against TOML multiple times, because the files would have just looked silly. I feel like that with TOML I can do less things, but you need to know more (i.e. have to look stuff up). Also it's a lot harder to implement a parser for it.

## Open Questions
### UTF-8 in Strings
I am not sure if strings should be utf-8 strings or should just be byte arrays. Personally I have wanted to include arbitrary binary data in JSON strings (or other config files) before, but it is sadly not possible, as there are only `\uHHHH` escape sequences. `\xHH` in YAML will just provide a shorter way to represent code points below U+7F. In C/C++ and Python for example it gives you the option to represent arbitrary bytes though. For example: In C++ `\xFF` will represent the byte sequence `FF`, when in YAML `\xFF` will represent the UTF-8 byte sequence `C3 BF`. With the former behaviour being called "bytes" and the latter being called "unicode" in the following, some common programming languages behave like this:

| Language   | Behaviour                             |
|------------|---------------------------------------|
| C & C++    | bytes                                 |
| Java       | error                                 |
| JavaScript | unicode                               |
| Lua        | bytes                                 |
| Python 2   | bytes                                 |
| Python 3   | unicode (unless using `bytes` object) |
| Ruby       | bytes                                 |
| Rust       | error                                 |

This is not simply a question of what `\xHH` should do, but rather a much bigger question of whether it should be allowed to specify non-UTF-8 strings in general and by extension if JOML should be allowed to serialize/deserialize them. All the other popular configuration languages (and JSON) do not allow non-unicode strings, but I think it could be very useful. Not enforcing an encoding at a level deeper than simply writing it at the top of this document might lead to chaotic situations in which everyone does what they want. For now the reference parser will read arbitrary bytes from `\xHH` escape sequences, but it's already a significant problem for the tests, because they are specified using JSON.

### Valid Keys
Currently unquoted keys can be anything. They may include newlines or hashes. They may look arbitrarily weird, as long as they do not contain a colon. You can sort of emulate annotations (see below) with them `position (vec2): [0, 0]`, which is kind of cool, but I think in general, you can do too much stuff that looks confusing. I should restrict the valid characters of keys, but I need to think about to what subset exactly.

### Dictionaries
I think that dictionaries should absolutely be ordered. In that case duplicate keys can be easily resolved by having a later occurence override the earlier one. It remains to be decided whether all elements should be saved, only the latest (in the document) value of a duplicate key should be saved or whether an error should be generated if a key is used multiple times.

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

### Digit Separators
They are very useful and good, but most programming languages' "toInt"/"toNumber" or similar do not support them. And the parser should be easy to build.

### null
* I decided against allowing simply omitting a value (just `key:`), because it makes the parser more complicated and it often looks like a mistake.
* I wasn't sure whether to add null at all, but people are lacking it in TOML, so I think it should be "fixed" in JOML. There are also some use cases (for example *overwriting* a value that was *derived* from another object with an empty value).
* Because of the example above assigning null ist also different from the simple absence of a value. If they were the same that would also defeat the point of `null` in general.

### Strings
* Escape sequences were added, because people WILL use them and then be surprised if it doesn't work, even though you can technically do most of them with `\xHH`. I simply picked the ones supported by JSON, because it's the smallest set I have found and it has all the important ones.
* I decided against only optionally having to escape backslash, i.e. if the following character is not part of a valid escape sequence (e.g. `oof\oof` would be valid string containing a backslash), but it could lead to sneaky error, or example when using Windows paths: `E:\Users\Joel\directory\file`. It is better to just always error if a backslash is used without a valid escape sequence. Also different programming languages handle this differently, so to avoid people getting unexpected results, there should be more errors, not less.
* There are no literal strings (like TOML), because though they are very useful and nice to have, they are not at all necessary and no one will ever do this "instinctively" just to be surprised that it doesn't work. Also if you don't quite know JOML well enough yet, it would rather look like a mistake to encounter backslashes outside of a valid escape sequence.

### Comments
* There are no multi-line comments, because every usable editor on the planet will help you comment multiple lines trivially. The extra complexity, even if it is minimal, cannot be justified because of that.
