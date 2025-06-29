# cee - C extended expressions
The main goal of CEE is to be some kind of C pre-processor with superpowers. So we can include many different features from different programming languages to the C programming language.

So, for example, the idea is that you can create an `async` keyword for the C programming language if you want, a `defer`, create arena allocators with some kind of syntax similar to Python's `with` keyword, create a fancy for-loop iterator like `for i in array` etc.

# Installation
Cee doesn't need any dependency. Just clone the repository and then you can do the following:
```bash
python my/cee/repo/cee.py gcc main.cee -o my_ouptut
```
This means: just repeat the compilation command as argument to the cee script and it will loop through the argument files looking for `.cee` files.

For each `.cee` file it find, it will transpile it and move the newly created file into a `.cee_build` folder in the current folder.

## Basic Example
This is how a typical .cee file looks like:
```c
import {stdio}

@func main() {
    printf("%s\n", "Hello World!");
}
```

## How it works

The basic idea is that Cee is a superset of the C syntax. We just include some new syntax to the existing C sources that will be processed by the Cee pre-processor. We call each one of the Cee features a "plugin". The plugin is like a command, it have the following structure: `@COMMAND ARGUMENTS BODY`. The `ARGUMENTS` is optional and the body should be between curly-braces. So, a typical command should be like: `@my_command arg1 arg2 {}`. Where the command is `my_command`, the arguments is `arg1 arg2`, in other words, the argument is a string between the command and the body, and the body, that is every thing between the curly-braces.

The arguments are not parsed, when implementing a new command, you will receive just a string, and you should be the responsible for parsing the arguments depending on which syntax you want.

The same for the body, you will receive just a string with the content of the body.

Futhermore, each plugin can have multiple command names, this means that to create a function, for example, you can use `@function`, but you also can use `@def`, or `@fn` and so on. We usually like to include all the names from the most commons programming languages, since most of them doesnt conflicts. So if you are coming from Go, you can use `func`, if you are coming from Python you can keep the `@def` usage etc.

## Current Plugins

For a while, the project has not so many features. Below we list the features that Cee supports today:

### Imports
The idea is that we can use `import` to substitute `#include` directives:

```c
@import {A}     // becomes: #include <A.h>
@import {A.h}   // becomes: #include <A.h>
@import {A.c}   // becomes: #include <A.c>
@import {A.cee} // becomes: #include "./cee/A.cee", the file will be compiled in this temp folder
```

If you want to use a .cee file in your project **you will need to use the `@import` plugin**.

The other thing you can do with this command is to import many libs at once:

```c
@import {stdlib, stdio, stdbool, MyLib.cee}
```

You can use this command with the following keywords: `import, use, load, require, include, using, uses`

### func
The `@func` is a way of creating C functions with a more flexible syntax. So you can write C functions that looks like Golang functions, Rust functions or Python functions. So this:
```c
void main(void) {
    //
}
```

can be written as:

```c
@func main() {
    //
}
```

you can see that we can omit the void in the arguments and in the return type. The return type should be after the arguments:
```c
@func sum(int a, int b) int {
    return a + b;
}
```

Also, a function created with `@function` can omit the semicolon, it will be inserted automatically:
```c
@fn sum(a: int, b: int) -> int {
    int result = a + b
    printf("Sum %d + %d = %d\n", a, b, result)
    return a + b
}
```
Look how the above code looks like a Rust code, we can also write the argument in the `type name` format, or in the `name: type` format. The return type can also be written as `name() int`, or we can use the arrow format: `name() -> int`. Alternatively, you can replace `->` for `>` in the return type.

The functions in Cee can also be lambdas, this means that you can create functions without names to be used as arguments to other functions. See below the section about delegates.

This command can be used with the following keywords: `func, function, fn, def, proc, procedure, routine, sub`. This means that all the functions below are the same:
```c
@fn sum(a: int, b: int) -> int { return a + b }
@function sum(int a, int b) > int { return a + b }
@def sum(int a, b: int) > int { return a + b }
@sub sum(a: int, int b) int { return a + b; }
@proc sum(int a, int b) > int { return a + b }
@procedure sum(int a, int b) > int { return a + b }
```


### Random fields
This idea comes from the "private" fields in Python, that are class fields starting with double underscores (`__field`). What Python does is just renaming that field to `_ClassName__field`. The idea of the random command is allow something similar, but instead of hiding the field by prefixing the class name, we just create random characters:
```c
struct Person {
    int @random {id};
};

Person myself;
myself.@random {id} = 123;
```
this will be transpiled to:
```c
struct Person {
    int jfurb;
};

Person myself;
myself.jfurb = 123;
```

This plugin is not intended to be really serious, you can use it to create some randoms characters in the place you want, but the intention is not to perform some kind of private field in the OPP term.

### module
The `module` plugin creates the `#define` macro to avoid create symbols twice and enables the auto semi-colon insertion in all the code inside the module. You can use the module plugin with or without name. In case of using this plugin without name, Cee will create a random name for you.

```c
@module My Module {
    struct MyStruct {
        int a_number
    }
    @fn my_function() {
        printf("%s\n", "My Function!")
    }
}
```
As you can see, you can create module names with blank spaces, accents etc. Note how the `struct` now doesn't need to use the semicolon anymore (but you still will need to use the `type name` format for each atttribute).
You can use this command with the following keywords: `module, package, mod, unit, library, lib, once`

### delegate
The delegate plugin is just a new way of defining pointers to functions. So instead of doing:
```c
Response* (http_method*)(Request*);
```
we can do:
```c
@delegate http_method {Response*, Request*};
```
The argument of the command is the name of the delegate (the pointer's name) and what is inside the body is a list of types. The first type is the return type, and the following types are the arguments of the function. If a function doesn't receive any argument and doesn't return anything, you can omit the body:
```c
@delegate http_method {};
```

You can use delegates together with `@function` to create lambda functions. Imagine that you have a function that receives as argument another function:
```c
@fn filter_number(@delegate number_operation {bool, int}, int number) bool {
    return number_operation(number);
}
```
Now you can define the function when calling the `filter_number` function, as like you are writing a lambda function in Javascript as argument for another function:
```c
bool result = filter_number(@fn (int number) bool {
    return (number % 2) == 0;
}, number);
```

What Cee does is very simple: when you create a `@function` without name, it will generate a random name for you, and will move the function definition to the body of the source file. After that, it will replace the lambda function with the random name, something similar to:
```c
bool __lambda_qtpia(int number) {
    return (number % 2) == 0;
}
bool filter_number(bool (*number_operation)(int), int number) {
    return number_operation(number);
}
bool result = filter_number(__lambda_qtpia, number);
```

### defer
Defer works as `defer` in GoLang, this means: as sson as the context ends, the command will be executed. The difference between Cee defer and GoLang defer is that the scope of the defer is set by using the curly-brackets:
```c
@fn most_common_word(file_path: char*) char* {
    FILE *file_pointer = open(file_path)
    @defer close(file_pointer) {
        // a bunch of clever code
        if (condition) {
            return NULL;
        }
        return most_common_word_found;
    }
}
```

This will be translated to:
```c
@fn most_common_word(file_path: char*) char* {
    FILE *file_pointer = open(file_path)
    // a bunch of clever code
    if (condition) {
        close(file_pointer)
        return NULL;
    }
    close(file_pointer)
    return most_common_word_found;
}
```


### ll - Linked Lists
```c
@ll MyMap {
    "key": "char*",
    "value": "char*",
    "natural_keys": ["key"]
}
```
#### Natural Keys
WIP

## Rules
- Each Plugin should return valid C code, this means in others words that a Plugin should not return Cee code, but a complete and valid C code.
- Each plugin should do only one thing, this means that, if a plugin exist to define names only once, your plugin should not do this. If there's a plugin to remove semicolons, your plugin should not remove semicolons...and so on


## The future: the things we want to support:
- some kind of `for/foreach` command
- inline unit testing `@test {}`
- allow plugins configurations, so if I want to enable/disable the function auto-semicolon I can say `@config { func -enable_auto_semicolon }.`
- a command like `cee show commands`
- jinja templates for some kind of generic programming

# How to create your own plugins

You can create your own plugins to define new syntaxes, or utilities. The cee command looks at two different places in order to load plugins: the internal `plugins` folder and the `.cee/plugins` in the current folder. So if you want to create new plugins, just create a new `.cee/plugins` folder in the project, walk into that directory and run the cee command that all plugins will be loaded.

To be considered a plugin, you must create a Python file with a `Plugin` class. That class must have:
- a `names` attribute with type `list[str]` containing all the valid command names you want to use for calling your plugin. So if your command to be `@mycommand` and `@my_command`, the names should be: `names = ["mycommand", "my_command"]`
- a `is_command_valid(command: cee_core.CeeCommand)` static method. This command receives a command object and you should be able to validate if the command is ok. It is useful, for example, if your command should receive arguments but the user doesn't provided it.
- a `get_proposed_changes(command: cee_core.CeeCommand,) -> cee_core.SourceCodeChanges` static method. This is the function responsible for replace all the string `@mycommand arg {}` for another string. That string is provided by that function.
