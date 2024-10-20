from setuptools import setup
from Cython.Build import cythonize
import os

# Collect all Python files to convert to C extensions
def find_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and any other unnecessary folders
        dirs[:] = [d for d in dirs if d not in [ 'migrations', 'media', 'static', 'templates','densepose','detectron2']]
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                py_files.append(os.path.join(root, file))
    return py_files

setup(
    name="ZenVton_django_app",
    ext_modules=cythonize(find_py_files("."), 
                          compiler_directives={"always_allow_keywords": True}),
)
