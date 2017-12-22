# -*- coding=utf-8
"""Common Tools Module."""
import hashlib
import base64
import os
import io
import re

from xml.dom import minidom
from xml.etree import ElementTree
from dicttoxml import dicttoxml
from .exception import CosClientError


class XMLParser:
    """
    Formattor of XML Tree.
        return a object witch can be render to a XML string or a Dict.
    """

    namespace_pattern = re.compile(r'\{.*\}(.*)')

    def __init__(self, xml, force_list=None):
        self.force_list = force_list or []
        if isinstance(xml, str):
            self.data = self._parse(ElementTree.fromstring(xml))
        elif isinstance(xml, ElementTree.Element):
            self.data = self._parse(xml)
        elif isinstance(xml, dict):
            self.data = xml
        else:
            raise TypeError

    def _key(self, key):
        group = re.match(self.namespace_pattern, key)
        try:
            return group[1]
        except IndexError:
            return key
        except TypeError:
            return key

    def _parse(self, xml_element):
        data = {}
        for element in xml_element:
            element_count = len(element)
            key = self._key(element.tag)
            if element_count:
                self._update(data, {key: self._parse(element)})
            elif element.items():
                items = element.items()
                if element.text:
                    items.append((key, element.text))
                self._update(data, {key: dict(items)})
            else:
                self._update(data, {key: element.text})
        return data

    def _update(self, target, source):
        for key in source:
            if key in target:
                if not isinstance(target[key], list):
                    value = target.pop(key)
                    lst = list()
                    lst.append(value)
                    lst.append(source[key])
                    target.update({key: lst})
                else:
                    target[key].append(source[key])
            elif key in self.force_list:
                target.update({key: [source[key]]})
            else:
                target.update({key: source[key]})

    def _xml(self, tag, data, attr=None):
        element = ElementTree.Element(tag, attrib=attr or {})
        for k, v in data.items():
            if isinstance(v, list):
                for item in v:
                    element.append(self._xml(k, item))
            elif isinstance(v, dict):
                element.append(self._xml(k, v))
            elif isinstance(v, str):
                child = ElementTree.Element(k)
                child.text = str(v)
                element.append(child)
        return element

    def to_xml_bytes(self, tag, attr=None):
        """
        Convert into XML Bytes.
        """
        prefix = b'<?xml version="1.0" encoding="utf-8" ?>'
        return prefix + ElementTree.tostring(
            self._xml(tag, self.data, attr=attr or None))

    def to_xml_element(self, tag, attr=None):
        """
        Convert into XML Element.
        """
        return self._xml(tag, self.data, attr=attr or None)

    def to_dict(self):
        """
        Convert into Dict.
        """
        return dict(self.data)
