from cx_Freeze import setup, Executable
from os.path import join, dirname

import PySnake

requires_files = ['game_font.ttf', 'game.ico', 'README.md', 'LICENSE.md']
requires = []
with open('requirements.txt', 'r') as file:
    requires.extend([row for row in file.read().split('\n') if row != ''])

setup(
    name="PySnake",
    version=PySnake.__version__,
    description="A little game on Python.",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='M.Price',
    platforms=['Windows', 'Linux'],
    install_requires=requires,
    package_data={'': requires_files},
    data_files=[('', requires_files)],
    include_package_data=True,
    executables=[Executable("PySnake.py", icon='game.ico')],
    zip_safe=True
)
