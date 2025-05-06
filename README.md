# cee - C extended expressions
The main goal of CEE is to be some kind of C pre-processor with superpowers. So we can include many different features from different programming languages to the C programming language.

So, for example, the idea is that you can create an `async` keyword for the C programming language if you want, a `defer`, create arena allocators with some kind of syntax similar to Python's `with` keyword, create a fancy for-loop iterator like `for i in array` etc.

For a while, the project is only able to create components with templates. More detail below.

# Template Components
Imagine that you want to create many different linkedlists, each linkedlist have different values, for example: you want a linkedlist for strings (a list of strings), a linkedlist for maps (each node have a key and a value, both strings) and so on. So, the structure that you will need to create for the `StringList` and for the `Map` are very similar, this is the idea of a component template: you can create a base/generic linkedlist and create `.cee` files to define the variable you will use with that template. A practical example:

```json
// StringList.cee
{
    "name": "StringList",
    "type": "template",
    "template_path": "./LinkedList.Jinja2",
    "output": "../StringList.c",
    "context": {
        "fields": [
            {"type": "char*", "name": "value"}
        ]
    }
}

```

```c
// LinkedList.Jinja2
#ifndef __{{ name | upper }}
#define __{{ name | upper }}

typedef struct {{ name }}
{
    {%- for field in fields %}
    {{ field.type }} {{ field.name }};
    {%- endfor %}

    struct {{ name }} *next;
    struct {{ name }} *previous;

    struct {{ name }} *first;
    struct {{ name }} *last;
    int length;
} {{ name }};

#endif
```
Both `.cee` and `.Jinja2` files should be inside a folder named `cee`. Once you run the cee command, you will cee (pun intended) that a new file named `StringList.c` is created.

For more complex examples you can check the `examples` folder.
