# iTunes xml generator

Simple python package helps you generate xml file like "iTunes Library.xml" with random track and artist attributes.
Can be used e.g. for testing some software which needs differents iTunes Library.

## Usage
## Install via pip
```
pip install itunesxmlgen
```
### Generate
```
from itunesxmlgen import generate_xml

xml = generate_xml()  # returns xml node (<lxml.etree.Element object>)
```

### Convert to string (if needed)
```
from itunesxmlgen.utils import tostring

string_xml = tostring(xml)
print(string_xml)
```

For more information see docstring.

## Run locally
### Clone repo
```
git clone git@github.com:perminovs/iTunesXmlGen.git
cd ./iTunesXmlGen
```
### Create & activate virtualenv (recommended)
```
virtualenv venv --python=/usr/bin/python3
source ./venv/bin/activate
```
### Install requirement
```
pip install -r requirements.txt
```
### Run tests
```
python -m unittest itunesxmlgen/tests/tests.py
```

## License
This repository uses the [MIT License](/LICENSE).
