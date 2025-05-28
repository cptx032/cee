"""
FILE *file_ptr = fopen("example.txt", "w");
@defer fclose(file_pointer) {
        fprintf(file_ptr, "Hello, World!\n");
        if (1==1) {
                // here it should inject too
                return;
        }
        my_delegates_append(@fn {
                return; // because the return is part of a cee function, this return should be ignored
        });
}
"""
