## Installation

You need have a Blener installed on you machine. This project will run by blender's own Python environment.

```shell
<Path-to-Blender-Python>/python.exe -m pip install <package-name>.
```

Create a blender project, and save in the same directory with `main.py`. Then add this code to the blender's text editor:

```python
import bpy
import os
import sys

dir_path = os.path.dirname(bpy.data.filepath)
if dir_path not in sys.path:
    sys.path.append(dir_path)

filename = os.path.join(dir_path, "main.py")
exec(compile(open(filename).read(), filename, 'exec'))

```
