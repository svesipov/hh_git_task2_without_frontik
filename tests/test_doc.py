# coding=utf-8

from lxml import etree
import unittest

from frontik.doc import Doc
from frontik.future import Future
from frontik.responses import RequestResult, FailedRequestException
from .instances import frontik_test_app


class TestDoc(unittest.TestCase):
    def test_simple(self):
        d = Doc('a')

        self.assertTrue(d.is_empty())

        d.put('test')

        self.assertFalse(d.is_empty())
        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a>test</a>""")

    def test_future_simple(self):
        d = Doc('a')
        f = Future()
        d.put(f)

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a/>""")

        f.set_result('test')

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a>test</a>""")

    def test_future_etree_element(self):
        d = Doc('a')
        f = Future()
        f.set_result(etree.Element('b'))
        d.put(f)

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a><b/></a>""")

    def test_future_list(self):
        d = Doc('a')
        f = Future()
        f.set_result([etree.Comment('ccc'), etree.Element('bbb')])
        d.put(f)

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a><!--ccc--><bbb/></a>""")

    def test_failed_future(self):
        d = Doc('a')
        f = Future()
        result = RequestResult()
        result.set_exception(FailedRequestException(reason='error', code='code'))
        f.set_result(result)
        d.put(f)

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n"""
                                        """<a><error reason="error" code="code"/></a>""")

    def test_doc_nested(self):
        a = Doc('a')
        b = Doc('b')
        b.put('test')
        a.put(b)

        self.assertEqual(a.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a><b>test</b></a>""")

    def test_nodes_and_text(self):
        a = Doc('a')
        a.put('1')
        a.put(Doc('b'))
        a.put('2')
        a.put(Doc('c'))
        a.put('3')

        self.assertEqual(a.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a>1<b/>2<c/>3</a>""")

    def test_root_node(self):
        d = Doc(root_node=etree.Element('doc'))
        d.put(etree.Element('test1'))

        self.assertEqual(d.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<doc><test1/></doc>""")

    def test_root_node_doc(self):
        d1 = Doc('a')
        d1.put(etree.Comment('1'))

        d2 = Doc(root_node=d1)
        d2.put(etree.Comment('2'))

        self.assertEqual(d2.to_string(), """<?xml version='1.0' encoding='utf-8'?>\n<a><!--1--><!--2--></a>""")

    def test_root_node_invalid(self):
        d = Doc(root_node='a')
        d.put(etree.Element('a'))

        self.assertRaises(ValueError, d.to_etree_element)

    def test_doc_page(self):
        xml = frontik_test_app.get_page_xml('compose_doc')

        self.assertIsNotNone(xml.find('a'))
        self.assertEqual(xml.findtext('a'), 'aaa')

        self.assertIsNotNone(xml.find('bbb'))

        self.assertIsNotNone(xml.find('c'))
        self.assertIn(xml.findtext('c'), (None, ''))

    def test_doc_invalid_xml(self):
        xml = frontik_test_app.get_page_xml('compose_doc?invalid=true')

        self.assertIsNotNone(xml.find('error'))
        self.assertEqual(xml.find('error').get('reason'), 'invalid XML')
