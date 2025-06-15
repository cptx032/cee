"""
@with include {
    "open": "close",
    "fopen": "fclose",
    "opendir": "closedir",
    "pipe": "close",
    "malloc": "free",
    "calloc": "free",
    "realloc": "free",
    "aligned_alloc": "free",
    "posix_memalign": "free",
    "mmap": "munmap",
    "socket": "close",
    "accept": "close",
    "sem_init": "sem_destroy",
    "pthread_mutex_init": "pthread_mutex_destroy",
    "pthread_cond_init": "pthread_cond_destroy",
    "dlopen": "dlclose",
    "tmpfile": "close"
}
@with open("my_path") as here {
        print();
}
"""
