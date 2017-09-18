from setuptools import setup
import os

from geronimo import VERSION


# Module entsprechend PEP420 (ohne "__init__.py") werden von setuptools.find_packages nicht erkannt
# siehe https://bitbucket.org/pypa/setuptools/issues/97
def get_package_list(path):
    return [item[0].replace(os.path.sep, ".") for item in os.walk(path)
            if "__pycache__" not in item[0]]


# parse dependencies from requirements.txt
def get_requirements():
    with open('requirements.txt') as f:
        required = [line for line in f.read().splitlines() if line.strip() and "#" not in line]
        return required


setup(
    name="geronimo",
    # "rc1.dev1254" may be added via environment
    version=VERSION + os.environ.get("RELEASE_SUFFIX", ""),
    description="Data collector and API for a mesh network",
    url="ssh://git@dev.on-i.de:on_geronimo.git",
    author="Lars Kruse",
    author_email="devel@sumpfralle.de",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=get_package_list("geronimo"),
    install_requires=get_requirements(),
    extras_require={},
    entry_points={
        "console_scripts": [
            "geronimo-manage=geronimo.manage:main_func",
        ],
    },
)
