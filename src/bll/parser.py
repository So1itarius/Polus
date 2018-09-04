from lxml import etree
from src.tools import Tools
import re


class Parser():
    def __init__(self):
        self.parser = etree.HTMLParser()
        self.tools = Tools()
        self.entity_regex = re.compile('(?:entityUid=)([a-zA-Z0-9-]+)')
        self.price_regex = re.compile('(.*)+\(.*\)+')


    def get_contacts(self, html):
        contacts = []
        result = re.search(r': [А-Яа-я,]+ [А-Яа-я ]+', html)
        result1 = re.search(r'[0-9][0-9(),доб\. -]+[0-9]', html)
        result2 = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', html)
        contact = {
            'name': None if result == None else result.group(0)[2:].replace(',', '').replace('.', '').strip(),
            'phone': None if result1 == None else result1.group(0).strip(),
            'email': None if result2 == None else result2.group(0).strip()
        }
        contacts.append(contact)

        return contacts

    def get_customer_data(self, html):
        org = {
            'name': None,
            'inn': None,
            'kpp': None
        }

        tree = etree.fromstring(html, self.parser)
        childs = tree.xpath('.//div[@class="control-group row-fluid  "]')

        for child in childs:
            label = child.find('label')
            if label is None:
                continue

            if label.text == 'Полное наименование':
                org['name'] = child.xpath('.//div[@class="control-readonly"]')[0].text
            if label.text == 'ИНН':
                org['inn'] = child.xpath('.//div[@class="control-readonly"]')[0].text
            if label.text == 'КПП':
                org['kpp'] = child.xpath('.//div[@class="control-readonly"]')[0].text
        return org

    def get_attachments(self, html):
        #Юнит тест ругается возможно на цикл вайл
        if html is None or html == '':
            return []

        result = re.findall(r'href=".+"', html)
        result1 = re.findall(r'\t([^\t\n]+)\t', html)
        result2 = []
        i = 0

        while i != len(result):
            attachment = {
                'displayName': "Документы по текущей закупке",
                'realName': result1[i].strip('\t'),
                'size': None,
                'publicationDateTime': None,
                'href': 'http://tenders.polyusgold.com{}'.format(result[i][6:-1])
            }
            result2.append(attachment)
            i = i + 1

        return result2

    def get_entity_id(self, html):
        search = self.entity_regex.search(html)
        if search is not None and len(search.groups()) > 0:
            return search.groups()[0]
        return None

    def special_search(self, word):
        return re.search(r'повторная публикация', word)

    def get_lot_data(self, html):
        result = {
            'name': None,
            'number': None,
            'organizer': None,
            'placingWay': None,
            'status': None,
            'organizeForm': None,
            'submissionForm': None,
            'maxPrice': None,
            'priceStep': None,
            'submissionStartDateTime': None,
            'submissionCloseDateTime': None,
            'biddingDateTime': None
        }
        if html is None or html == '':
            return result

        tree = etree.fromstring(html, self.parser)

        org = tree.find('.//label[@for="OrganizerName"]')

        result['name'] = self.tools.clear(self.get_text(tree.find('.//label[@for="Title"]')))
        result['number'] = self.get_text(tree.find('.//label[@for="LotNumberFull"]'))
        result['organizer'] = self.tools.clear(self.get_text(org))
        result['placingWay'] = self.get_text(tree.find('.//label[@for="NoticeConfigName"]'))
        result['status'] = self.get_text(tree.find('.//label[@for="LotStatusName"]'))
        result['organizeForm'] = self.get_text(tree.find('.//label[@for="ParticipationForm"]'))
        result['submissionForm'] = self.get_text(tree.find('.//label[@for="ParticipationRequestForm"]'))
        result['maxPrice'] = self.get_text(tree.find('.//label[@for="InitialPrice"]'))
        result['priceStep'] = self.get_text(tree.find('.//label[@for="PriceStep"]'))
        result['submissionStartDateTime'] = self.get_text(tree.find('.//label[@for="RequestReceivingBeginDate"]'))
        result['submissionCloseDateTime'] = self.get_text(tree.find('.//label[@for="RequestReceivingEndDate"]'))
        result['biddingDateTime'] = self.get_text(tree.find('.//label[@for="BidReceivingBeginDate"]'))
        result['envelopDateTime'] = self.get_text(tree.find('.//label[@for="EnvelopeOpeningBeginDate"]'))
        result['deliveryDateTime'] = self.get_text(tree.find('.//label[@for="PlannedExecutionDate"]'))

        return result

    def get_text(self, elem):
        if elem is not None:
            return elem.getparent().find('.//div[@class="control-readonly"]').text \
                   or elem.getparent().find('.//div[@class="control-readonly"]/a').text
        return None

    # def get_status(self, string):
    #     if string is None or string.strip() == '':
    #         return 0
    #
    #     'Опубликовано' 1
    #     'Прием заявок' 1
    #     'Прием заявок завершен' 1
    #     'Вскрытие конвертов' 2
    #     'Определение участников торгов' 2
    #     'Участники определены' 7
    #     'Идут торги' 2
    #     'Подведение итогов' 2
    #     'Завершен'
    #     'Не состоялся с выбором победителя'
    #     'Состоялся с заключением договора'
    #     'Договор завершен' 6
    #     'Состоялся без заключения договора'
    #     'Не состоялся' 5
    #     'Не состоялся с заключением договора' 5
    #     'Не состоялся без заключения договора'  5
    #     'Отменен' 4
    #     'Заменен новой версией' 0
    #
    #
    #
    #     None = 0,
    #     Active = 1,
    #     Commission = 2,
    #     Closed = 3,
    #     Cancel = 4,
    #     Abandoned = 5,
    #     /// <summary>
    #     /// Исполнение завершено
    #     /// </summary>
    #     Played = 6,
    #     /// <summary>
    #     /// Исполняется
    #     /// </summary>
    #     Playing = 7,
    #     /// <summary>
    #     /// Приостановлено определение поставщика
    #     /// </summary>
    #     Suspended = 8
