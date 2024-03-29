# Set LD_LIBRARY_PATH to current directory
export LD_LIBRARY_PATH := $(shell pwd)

# Compiler options
CC := clang
CFLAGS := -Wall -pedantic -std=c99 -fPIC
LDFLAGS := -shared

# Python include directory
PYTHON_INCLUDE := -I/usr/include/python3.11/

# Target: all
all: _phylib.so

# Compile phylib.c to create phylib.o
phylib.o: phylib.c
	$(CC) $(CFLAGS) -c $< -o $@

# Create libphylib.so from phylib.o
libphylib.so: phylib.o
	$(CC) $(LDFLAGS) -o $@ $< -lm

# Generate Python wrapper using SWIG
phylib_wrap.c: phylib.i
	swig -python $<

# Compile phylib_wrap.c to create phylib_wrap.o
phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) $(PYTHON_INCLUDE) -c $< -o $@

# Link phylib_wrap.o with libpython and libphylib to create _phylib.so
_phylib.so: phylib_wrap.o libphylib.so
	$(CC) $(CFLAGS) $(LDFLAGS) $< -L. -L/usr/lib/python3.11 -lpython3.11 -lphylib -o $@

# Phony target to clean up intermediate and generated files
.PHONY: clean
clean:
	rm -f phylib.o libphylib.so phylib_wrap.c phylib_wrap.o _phylib.so phylib.py
