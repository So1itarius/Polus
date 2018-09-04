import unittest

from src.bll.parser import Parser


class Unittest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_get_contacts(self):
        path = 'C://Users//Павел//Desktop//Polus(redesign ugmk-collector)(Final ver.)//test//files//contacts.html'
        with open(path) as data_file:
            html = data_file.read()

        result = self.parser.get_contacts(html)
        self.assertEqual(1, len(result))

    def test_get_customer_data(self):
        path = 'C://Users//Павел//Desktop//Polus(redesign ugmk-collector)(Final ver.)//test//files//organization.html'
        with open(path, encoding='utf_8_sig') as data_file:
            html = data_file.read()

        result = self.parser.get_customer_data(html)
        self.assertIsNotNone(result)
        self.assertEqual(result['inn'], '6606015817')
        self.assertEqual(result['kpp'], '660601001')

    def test_get_attachments(self):
        path ='C://Users//Павел//Desktop//Polus(redesign ugmk-collector)(Final ver.)//test//files//lot_attachments.html'
        with open(path) as data_file:
            html = data_file.read()

        result = self.parser.get_attachments(html)
        self.assertEqual(6, len(result))

    def test_get_attachments_tender(self):
        path = '../files/tender_attachments.html'
        with open(path, encoding='utf_8_sig') as data_file:
            html = data_file.read()

        result = self.parser.get_attachments(html)
        self.assertEqual(1, len(result))
