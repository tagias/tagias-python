import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tagias",
    version="1.0.4",
    author="Vladimir Kryazh",
    author_email="vladimir@tagias.com",
    license="MIT License",
    description="Public python module for tagias.com external API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="tagias annotation tag label",
    url="https://github.com/tagias/tagias-python",
    packages=["tagias"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    install_requires=["requests"],
)
