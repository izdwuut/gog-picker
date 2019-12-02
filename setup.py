import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gog-picker",
    version="0.5.0",
    author='Bartosz "izdwuut" Konikiewicz',
    author_email="izdwuut@gmail.com",
    description="Gift of Games Picker for Reddit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/izdwuut/gog-picker",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English"
    ],
    install_requires=[
        "steam",
        "praw",
        "prawcore",
        "beautifulsoup4",
        "rdoclient-py3",
        "requests"
    ]
)