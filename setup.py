import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swift-morm",
    version="0.1",
    author="Pedro Lins",
    author_email="paugustolins@gmail.com",
    description="Swift Morm is a simple object mapper for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PdrLins/swift-morm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
