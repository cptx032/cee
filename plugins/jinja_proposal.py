"""
@template MyTemplate {"Hey {{ name }}!"}

printf(
        @template inline MyTemplate {"name": "Willie"}
);


@template LinkedList {
        typedef struct {{name}} {
                {{type}} value;
                struct {{name}} next*;
        } {{name}};
}


@template outline LinkedList {"type": int, "name": "IntegerLinkedList"}
"""
