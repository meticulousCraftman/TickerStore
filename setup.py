import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tickerstore",
    version="0.0.1",
    author="Apoorva Singh",
    author_email="apoorva.singh157@gmail.com",
    description="Fetches historical financial data from stock market",
    long_description=long_description,
    url="https://github.com/meticulousCraftman/tickerstore",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
