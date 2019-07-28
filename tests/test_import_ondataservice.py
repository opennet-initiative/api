import on_geronimo.oni_model.models as models

from . import IMPORT_ONDATASERVICE_SAMPLE_FILE, TestBase


class OndataserviceImportTest(TestBase):

    @classmethod
    def setUpClass(cls):
        cls.import_from_ondataservice(clear_before=True)
        super().setUpClass()

    def test_parsed_counts(self):
        self.assertEqual(models.AccessPoint.objects.all().count(), 10)
        self.assertEqual(models.EthernetNetworkInterface.objects.all().count(), 28)
        self.assertEqual(models.NetworkInterfaceAddress.objects.all().count(), 31)
        self.assertEqual(models.WifiNetworkInterfaceAttributes.objects.all().count(), 3)
        self.assertEqual(models.RoutingLink.objects.all().count(), 0)
        self.assertEqual(models.InterfaceRoutingLink.objects.all().count(), 0)

    def test_network_interface_attributes(self):
        for ap_main_ip, expected_wireless_interfaces in (
                ("192.168.2.4", {"ath0": "Z10-Klinikum"}),
                ("192.168.2.84", {"wlan0": "dom-planetdachneu.oni.de"}),
                ("192.168.2.106", {"wlan0": "Budapester.on-i.de"})):
            with self.subTest(ap=ap_main_ip):
                parsed_addresses = set()
                ap = models.AccessPoint.objects.get(main_ip=ap_main_ip)
                wireless_attributes = models.WifiNetworkInterfaceAttributes.objects.filter(
                    interface__accesspoint=ap)
                self.assertEqual(wireless_attributes.count(), len(expected_wireless_interfaces))
                for if_name, ssid in expected_wireless_interfaces.items():
                    with self.subTest(interface_name=if_name):
                        attributes = wireless_attributes.get(interface__if_name=if_name)
                        self.assertEqual(ssid, attributes.wifi_ssid)
