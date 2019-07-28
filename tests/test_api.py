import json

from django.urls import reverse
from django.test import Client, TestCase

from . import TestBase


class APITest(TestBase):

    @classmethod
    def setUpClass(cls):
        cls.import_from_all_sources(clear_before=True)
        super().setUpClass()

    def setUp(self):
        self.client = Client()

    def _retrieve_json_data(self, reverse_url, args=None):
        response = self.client.get(reverse(reverse_url, args=args))
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def test_accesspoint_collection(self):
        data = self._retrieve_json_data("accesspoint-list")
        self.assertIn("main_ip", data[0])

    def test_accesspoint_details(self):
        data = self._retrieve_json_data("accesspoint-details", ["192.168.2.4"])
        self.assertEqual(data["main_ip"], "192.168.2.4")

    def test_accesspoint_interfaces(self):
        data = self._retrieve_json_data("accesspoint-interfaces", ["192.168.2.4"])
        self.assertIn("eth0", [iface["if_name"] for iface in data])

    def test_accesspoint_links(self):
        data = self._retrieve_json_data("accesspoint-interfaces", ["192.168.2.4"])
        self.assertIn(True, [link["is_wireless"] for link in data])

    def test_interface_list(self):
        data = self._retrieve_json_data("interface-list")
        self.assertIn("eth0", [iface["if_name"] for iface in data])

    def test_interface_details(self):
        data = self._retrieve_json_data("interface-details", ["192.168.2.4"])
        self.assertEqual(data["if_name"], "ath0")

    def test_interface_accesspoint(self):
        data = self._retrieve_json_data("interface-accesspoint", ["192.168.12.4"])
        self.assertEqual(data["main_ip"], "192.168.2.4")

    def test_link_list(self):
        data = self._retrieve_json_data("link-list")
        self.assertIn(True, [link["is_wireless"] for link in data])

    def test_link_details(self):
        data = self._retrieve_json_data("link-detail-id", [1])
        self.assertIn("is_wireless", data)
        data = self._retrieve_json_data("link-detail-peers", ["192.168.2.4", "192.168.2.3"])
        self.assertIn("is_wireless", data)

    def test_site_list(self):
        data = self._retrieve_json_data("site-list")
        self.assertIn("post_address", data[0])

    def test_site_details(self):
        data = self._retrieve_json_data("site-details", [1])
        self.assertIn("post_address", data)
