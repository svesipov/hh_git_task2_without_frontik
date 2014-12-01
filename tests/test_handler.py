# coding=utf-8

import requests
import unittest

from .instances import frontik_non_debug, frontik_test_app


class TestHandler(unittest.TestCase):
    def test_active_limit(self):
        text = frontik_non_debug.get_page_text('app/recursion?n=6')
        self.assertEqual(text, '200 200 200 200 200 503')

    def test_check_finished(self):
        text = frontik_test_app.get_page_text('check_finished')
        self.assertEqual(text, 'Callback not called')

        # Check that callback has not been called at later IOLoop iteration

        text = frontik_test_app.get_page_text('check_finished')
        self.assertEqual(text, 'Callback not called')

    def test_head(self):
        response = frontik_test_app.get_page('head', method=requests.head)
        self.assertEqual(response.headers['X-Foo'], 'Bar')
        self.assertEqual(response.content, '')

    def test_no_method(self):
        response = frontik_test_app.get_page('head', method=requests.post)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers['Allow'], 'get')
