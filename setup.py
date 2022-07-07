from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_file(fname):
    with open(fname, "r") as f:
        return f.read()


# sudo apt install twine -y
# python3 -m pip install --upgrade setuptools wheel
setup(
    name="speechloop",
    version="0.0.2",
    author="robmsmt",
    author_email="robmsmt@gmail.com",
    description='A "keep it simple" collection of many speech recognition engines... Designed to help answer - what is the best ASR?',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robmsmt/SpeechLoop",
    python_requires=">=3.6",
    packages=["speechloop"],
    # packages=find_packages('speechloop'),
    # package_dir={'': 'speechloop'},
    include_package_data=True,
    install_requires=[elem.strip() for elem in read_file("requirements.txt").splitlines()],
    entry_points={"console_scripts": ["speechloop=speechloop:interactive_cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    keywords=["speech", "testing", "asr"],
)
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

# one liner
# rm -rf ./build ./dist ./SpeechLoop.egg-info && python3 -m build --wheel && twine upload dist/*
# rm -rf ./build ./dist ./SpeechLoop.egg-info ; python3 setup.py bdist_wheel

# INSTALL LOCALLY: `pip install --editable .`
# BUILD: `rm -rf wheels; pip wheel . -w wheels`
# OR `rm -rf build dist speechloop.egg-info ; python3 setup.py sdist bdist_wheel`


# FIRST TIME SETUP
#sudo apt install twine -y
#python3 -m pip install --upgrade setuptools wheel
#python3 setup.py sdist bdist_wheel
#twine upload dist/*

# ONE LINER
#rm -rf build/ dist/ speechloop.egg-info/ ; python3 setup.py sdist bdist_wheel && twine upload dist/*

### note you cannot (easily) reuse the same version number when it's uploaded to pypi
