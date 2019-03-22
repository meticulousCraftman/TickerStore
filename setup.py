import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TickerStore",
    version="0.0.8",
    author="Apoorva Singh",
    author_email="apoorva.singh157@gmail.com",
    description="Historical data of financial instruments from NSE",
    long_description=long_description,
    url="https://github.com/meticulousCraftman/tickerstore",
    license="MIT",
    install_requires=[
        "upstox",
        "python-dotenv",
        "Flask",
        "influxdb",
        "crayons",
        "nsepy",
        "pandas",
        "requests",
        "lxml",
        "loguru",
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
