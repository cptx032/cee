# cee - C extended expressions
The main goal of CEE is to be some kind of C pre-processor with superpowers. So we can include many different features from different programming languages to the C programming language.

So, for example, the idea is that you can create an `async` keyword for the C programming language if you want, a `defer`, create arena allocators with some kind of syntax similar to Python's `with` keyword, create a fancy for-loop iterator like `for i in array` etc.

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

The idea is also that each plugin should be **context-free**. This means that the result of a plugin should not be dependant of another plugin. This allow a more simple structure inside the project and a more consistent behavior for each plugin.

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

If you want to use a .cee file in your project you will need to use the `@import` plugin.

### func
The `@func` is a tentative to make C functions with the sintax of Golang functions, so this:
```c
void main(void) {
    //
}
```

becomes

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

### Random fields
This idea comes from the "private" fields in Python, that are class fields starting with double underscores (`__field`). What Python does is just renaming that field to `_ClassName__field`. The idea of the random command is allow something similar, but instead of putting the class name, we just create random characters:
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


## The future: the things we want to support:
- plugins name alias, so `@func` could also be `@fun`, `@fn`, `@def`, `@proc`, `@procedure`, `@routine`, `@defun`, `@sub`, `@function`...
- auto-comma insertion on functions
- modules, to allow the automatic insertion of `#ifndef` directives and also module naming
- some kind of `for` command
- lambda functions
- inline unit testing `@test {}`
- allow plugins configurations, so if I want to enable/disable the function auto-comma I can say `@config { func -enable_auto_comma }.`
- module rename to `@package`, `@mod`, `@unit`, `@defpackage`, `@library`, `@lib`
