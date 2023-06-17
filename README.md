# RL with Blender

This repo shows how to train agent with Blender environemnt.

Here are why you could choose Blender as the game env:

* Blazingly-fast startup speed
* Blender is totally free and Open-sourece
* It has a robust camera system, which works well with [task](http://arxiv.org/abs/2111.08096) need visiual input.
* Native support for Python
* Easy to create 3D or 2D scene

## Installation

You need a [Blener]() installed on you machine. This project will run by blender's own Python environment. So you need also install all dependecies on blender's Python environment.

```shell
<Path-to-Blender-Python>/python.exe -m pip install <package-name>.
```

After successfully install dependencies, open [env.blend](./env.blend) with Blender. Now you can run the script from Script panel.

If you want to create your own blender project, make sure the project file is in the same directory with `main.py`. Then add this code to the blender's text editor:

```python
import bpy
import os
import sys

dir_path = os.path.dirname(bpy.data.filepath)
if dir_path not in sys.path:
    sys.path.append(dir_path)

filename = os.path.join(dir_path, "main.py")

# A list of modules that need to be reloaded
# Replace 'mymodule1', 'mymodule2', etc. with the actual names of the modules
modules_to_reload = ['blender_env', 'controller.missile', 'mymodule3']

for module in modules_to_reload:
    if module in sys.modules:
        del sys.modules[module]

with open(filename, 'r') as f:
    script = f.read()

exec(script)
```

## License

GPL
