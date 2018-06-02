from iTunesXmlGen import generate_xml
from iTunesXmlGen.utils import tostring


# TODO real tests

xml = generate_xml()
string = tostring(xml)
print(string)
