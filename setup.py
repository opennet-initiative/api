from setuptools import find_packages, setup
import os

from on_geronimo import VERSION


# parse dependencies from requirements.txt
def get_requirements():
    with open('requirements.txt') as f:
        required = [line for line in f.read().splitlines() if line.strip() and "#" not in line]
        return required


setup(
    name="on-geronimo",
    # "rc1.dev1254" may be added via environment
    version=VERSION + os.environ.get("RELEASE_SUFFIX", ""),
    description="Data collector and API for a mesh network",
    url="ssh://git@dev.opennet-initiative.de:on_geronimo.git",
    author="Lars Kruse",
    author_email="devel@sumpfralle.de",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=get_requirements(),
    extras_require={},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "on-geronimo-manage=on_geronimo.manage:main_func",
        ],
    },
)
