import on_geronimo.oni_model.models as models

from . import IMPORT_OLSR_SAMPLE_FILE, TestBase


class OLSRImportTest(TestBase):

    @classmethod
    def setUpClass(cls):
        cls.import_from_olsr(clear_before=True)
        super().setUpClass()

    def test_parsed_counts(self):
        self.assertEqual(models.AccessPoint.objects.all().count(), 280)
        self.assertEqual(models.EthernetNetworkInterface.objects.all().count(), 473)
        self.assertEqual(models.NetworkInterfaceAddress.objects.all().count(), 473)
        self.assertEqual(models.WifiNetworkInterfaceAttributes.objects.all().count(), 0)
        self.assertEqual(models.RoutingLink.objects.all().count(), 625)
        self.assertEqual(models.InterfaceRoutingLink.objects.all().count(), 1250)

    def test_address_assignments(self):
        for ap, expected_addresses in (
                ("192.168.1.12", {"192.168.1.12", "192.168.11.12"}),
                ("192.168.1.54", {"192.168.1.54"}),
                ("192.168.2.36", {"192.168.2.36", "192.168.12.36"})):
            with self.subTest(ap=ap):
                parsed_addresses = set()
                for interface in models.AccessPoint.objects.get(pk=ap).interfaces.all():
                    parsed_addresses.update(address.address
                                            for address in interface.addresses.all())
                self.assertEqual(expected_addresses, parsed_addresses)
