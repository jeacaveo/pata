import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pata_jeacaveo",
    version="1.0.0",
    author="Jean Ventura",
    author_email="jv@venturasystems.net",
    description="Library in charge of loading, "
    "maintaining and refining data and databases "
    "related to Prismata (strategy game).",
    long_description=long_description,
    long_description_content_type="text/x-rst; charset=UTF-8",
    url="https://github.com/jeacaveo/pata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "test": ["mock", "coverage"],
        },
    )
