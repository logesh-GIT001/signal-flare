from setuptools import setup, find_packages

setup(
    name="signal-flare",
    version="1.1.0",
    author="SIGNAL-FLARE Contributors",
    description="Post-exploitation breach confirmation",
    url="https://github.com/logesh-GIT001/signal-flare",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "signal-flare=signal_flare.cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

