"""
@template MyTemplate {"Hey {{ name }}!"}

printf(
    @template apply MyTemplate {"name": "Willie"}
);


@template LinkedList {
    typedef struct {{name}} {
        {{type}} value;
        struct {{name}} next*;
    } {{name}};
}
"""
