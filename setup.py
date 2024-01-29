from setuptools import setup

setup(
    name="pygis",
    packages=["pygis"],
    python_requires=">3.10",
    install_requires=[
        "PyQt6",
        "requests",
        "pillow",
        "pyproj",
        "click",
        "typing_extensions",
    ],
    entry_points={
        "console_scripts": [
            "pygis = pygis.__main__:main",
        ]
    }
)
