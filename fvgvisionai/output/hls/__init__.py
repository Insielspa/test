import cython

_modulo_name = __name__

if cython.compiled:
    print(f"Cython compiled {_modulo_name} module!")
