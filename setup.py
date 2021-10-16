import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helios",
    version="0.3.0",
    author="Filipi N. Silva, Bruno Messias",
    author_email="filipi@iu.edu, messias.physics@gmail.com",
    description="Python library to work with complex networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fury/helios",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
