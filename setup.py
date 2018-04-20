from cx_Freeze import setup, Executable
import os

import PySnake

requires_files = ['game_font.ttf', 'game.ico', 'README.md', 'LICENSE.md']
requires = []
with open('requirements.txt', 'r') as file:
    requires.extend([row for row in file.read().split('\n') if row != ''])

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

build_exe_options = {
    "packages": ["os", "tkinter"]
}

setup(
    name="PySnake",
    version=PySnake.__version__,
    description="A little game on Python.",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.md')).read(),
    author='M.Price',
    platforms=['Windows', 'Linux'],
    install_requires=requires,
    options={"build_exe": build_exe_options},
    package_data={'': requires_files},
    data_files=[('', requires_files)],
    include_package_data=True,
    executables=[Executable("PySnake.py", icon='game.ico')],
    zip_safe=True
)
