import unittest
import xmlrpclib

class TestDomain(unittest.TestCase):
    def setUp(self):
        import xmlrpclib
        self.client = xmlrpclib.ServerProxy('http://localhost:3333')

    def tearDown(self):
        # self.client.disconnect()
        pass

    def test_ok(self):
        domains = self.client.domain.list()
        self.assertEqual(len(domains), 10)


if __name__ == '__main__':
    unittest.main()
