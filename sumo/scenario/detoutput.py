# coding=utf-8

import xml.etree.ElementTree as ET

# 从文件生成ElementTree
tree = ET.parse('test.det.xml')
root = tree.getroot()

for det in root.findall('e1Detector'):
    det.attrib['file'] = "./detoutput/e1Detector.xml"

tree.write('test.det.xml')