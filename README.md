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

If you want to use a .cee file in your project you will need to use the `@import` plugin.

The other thing you can do with this command is to import many libs at once:

```c
@import {stdlib, stdio, stdbool, MyLib.cee}
```

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
For a while, the `module` plugin only creates the `#define` macro to avoid create symbols twice. You can use the module plugin with or without name. In case of using this plugin without name, Cee will create a random name for you.

```c
@module My Module {
    @fn my_function() {
        printf("%s\n", "My Function!");
    }
}
```
As you can see, you can create module names with blank spaces, accents etc.

### delegate
The delegate plugin is just a new way of creating pointers to functions. It works the same way the `@function` plugin works: it is just a rearrangement of arguments, on how we write the code. So instead of doing:
```c
Response* (http_method*)(Request*);
```
we can do:
```c
@delegate http_method {Response*, Request*};
```
The argument of the command is the name of the delegate and what is inside the body is a list of types. The first type is the return type, and the following types are the arguments of the function. If a function doesn't receive any argument and doesn't return anything, you can omit the body:
```c
@delegate http_method {};
```

You can use delegates together with `@function` to create lambda functions. So Imagine that you have a function that receives as argument another function:
```c
@fn filter_number(@delegate number_operation {bool, int}, int number) bool {
    return number_operation(number);
}
```
Now you can define the function directly when calling the `filter_number` function, as like you are writing a lambda function in Javascript:
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


## The future: the things we want to support:
- auto-comma insertion on functions
- some kind of `for` command
- inline unit testing `@test {}`
- allow plugins configurations, so if I want to enable/disable the function auto-comma I can say `@config { func -enable_auto_comma }.`
- a command like `cee show commands`
- jinja templates for some kind of generic programming
