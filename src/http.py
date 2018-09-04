import sys
from datetime import datetime
from urllib.parse import urljoin
import requests
from parsel import Selector

from src.bll.parser import Parser
from src.repository.mongodb import MongoRepository
from settings import configparse


from src.tools import Tools


def handler(x):
    return x.replace("<h2>\n\t\t\t<span>", "").replace("</span> ", " ").replace("\n\t\t\t", "").replace(" \n\t\t","").replace("</h2>", "")

class Http():
    def __init__(self):
        cfg = configparse()
        self.parser = Parser()
        cfg_mongo = cfg['mongodb']
        self.repository = MongoRepository(cfg_mongo['host'],
                                          cfg_mongo['port'],
                                          cfg_mongo['database'],
                                          cfg_mongo['collection'])
        self.tools = Tools()

    def get_page_list(self, starturl):
        Startpage = []
        index = requests.get(starturl)
        y = 0
        x = 0
        while True:
            Startpage.append(starturl)
            print("add page", x)
            x = x + 1
            for href in Selector(index.text).css('.pagination ul :last-child a::attr(href)').extract():
                url = urljoin(index.url, href)
                sel = Selector(requests.get(url).text)
            if url == starturl:
                break
            else:
                starturl = url
                index = requests.get(starturl)
        return Startpage

    def get_special_tender_list(self, starturl):
        SpecialTenderInfo = set()
        index = requests.get(starturl)
        for href in Selector(index.text).css('.purchase-title a::attr(href)').extract():
            url = urljoin(index.url, href)
            sel = Selector(requests.get(url).text)

            id = sel.css(' .purchase-single-head span::text').extract_first()
            title = handler(sel.css(' .purchase-single-head h2').extract_first())

            if self.parser.special_search(title) is not None:
                SpecialTenderInfo.add(id)
        return list(SpecialTenderInfo)


    def get_tender_list(self, starturl,status,time):
        """Возвращает списком c данными для тендеров"""

        TenderInfo = set()

        index = requests.get(starturl)
        for href in Selector(index.text).css('.purchase-title a::attr(href)').extract():
              url = urljoin(index.url, href)
              sel = Selector(requests.get(url).text)

              id=sel.css(' .purchase-single-head span::text').extract_first()
              dbmodel = self.repository.get_one('{}'.format(id))
              info = handler(sel.css('.purchase-single-head .purchase-single-info::text').extract_first())
              tm = info[info.find("|") + 20:info.rfind("|") - 1]
              #Проверка с базой в середине функции, мне казалось,что брейк просто бы остановил цикл в колекте продолжилось бы выполнение, тут сравнение со временем можно регулировать, накинуть дни например
              if dbmodel is not None and dbmodel['_id'] == id and dbmodel['status']==status and dbmodel['time'] == self.tools.get_utc_epoch(tm) and (
                      time is not None and (self.tools.get_utc_epoch(tm)) < time):
                                   sys.exit(0)
              if dbmodel is not None and dbmodel['_id'] == id and dbmodel['status']==status and dbmodel['time'] == self.tools.get_utc_epoch(tm):
                    print("Coincidence? I don't think so ...")
                    continue

              title = handler(sel.css(' .purchase-single-head h2').extract_first())
              organization = sel.css(' .purchase-single-filters a::text').extract_first()
              TenderInfo.add((
                id,
                href,
                title[title.find("]") + 2:],
                organization,
                tm,
                info[info.find("|") - 12:info.find("|")],
              ))

        a = list(TenderInfo)
        return a

    def get_tender_mindate(self,url):
        index = requests.get(url)
        for href in Selector(index.text).css('.purchase-title a::attr(href)').extract():
            url = urljoin(index.url, href)
            sel = Selector(requests.get(url).text)
            info = handler(sel.css('.purchase-single-head .purchase-single-info::text').extract_first())
            a=info[info.find("|") + 20:info.rfind("|") - 1]
            #Неполучилось воспользщоваться функцией из Tools, поэтому скопировал (ಥ﹏ಥ)
            date = datetime.strptime(a.replace('\n', '').replace('\t', '').replace('\r', '').strip(),
                                     '%d.%m.%Y')
            ep_time = (date - datetime(1970, 1, 1)).total_seconds() * 1000
            break
        return int(ep_time)


    def get_tender_contacts(self, tender_number):
        """Возвращает HTML документ с контактами для тендера"""
        starturl = 'http://tenders.polyusgold.com/purchases/{}'.format(tender_number)
        sel = Selector(requests.get(starturl).text)

        a = sel.css(' .purchase-single-body').extract_first()
        return a

    def get_tender_lots(self, tender_id, tender_number, token):
        """Возвращает JSON со списком лотов для тендера"""
        url = 'https://zakupki.ugmk.com/Tenders/LoadLots/{}'.format(tender_id)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__={}'.format(token),
            'Host': 'zakupki.ugmk.com',
            'Origin': 'https://zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com/Tender/{}'.format(tender_number),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'offset': 0,
            'limit': 1000,
            'sortColumn': None,
            'sortAsc': False,
            '__RequestVerificationToken': token
        }

        r = requests.post(url, data, headers=headers)
        return r.json()['Rows']

    def get_tender_data(self, tender_number):
        """Возвращает HTML документ с данными тендера"""
        url = 'http://tenders.polyusgold.com/purchases/{}'.format(tender_number)
        r = requests.get(url)
        return r.text

    def get_tender_documents(self, tender_number):
        """Получение HTML с документами тендера"""
        #TenderInfo = set()
        starturl = 'http://tenders.polyusgold.com/purchases/{}'.format(tender_number)
        sel = Selector(requests.get(starturl).text)

        a = sel.css(' .purchase-single-docs ul').extract_first()

        return a

    def get_lot_data(self, lot_url, tender_number, token):
        """Возвращает HTML с данными для лота"""
        url = 'https://zakupki.ugmk.com{}'.format(lot_url)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'ASP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__={}'.format(token),
            'Host': 'zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com/Tender/{}'.format(tender_number),
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        r = requests.get(url, headers=headers)
        return r.text

    def get_lot_documents(self, entity_id, lot_url, token):
        url = 'https://zakupki.ugmk.com/Documents/List?entityTypeCode=TenderLot&entityUid={}'.format(entity_id)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__=K3dfzSt3g/2sa7vr2mJqfDTCyXcqWyLBvjQ7Omjx2Alt6sT63z9CQ43PEsPx7cPND1LSl1GmDQ+MlQX806uU7WV3Sm00gdhatsjwNQXDDe7KnvzYWnAiDNTAr28sZSElM/4l7PBVnzo2tOM6SfQY7mPkdS2hE0G5AckN1/mudaA=',
            'Host': 'zakupki.ugmk.com',
            'Origin': 'https://zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com{}'.format(lot_url),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            '__RequestVerificationToken': token
        }
        r = requests.post(url, data, headers=headers)
        return r.text

    def get_lot_stages(self, lot_uid, lot_url, token):
        url = 'https://zakupki.ugmk.com/Tenders/LoadNotices?lotUId={}'.format(lot_uid)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'SP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__={}'.format(token),
            'Host': 'zakupki.ugmk.com',
            'Origin': 'https://zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com/{}'.format(lot_url),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'offset': 0,
            'limit': 1000,
            'sortColumn': None,
            'sortAsc': False,
            '__RequestVerificationToken': token
        }

        r = requests.post(url, data, headers=headers)
        return r.json()

    def get_organization_page(self, company_id, token):
        url = 'https://zakupki.ugmk.com/Companies/Details/{}'.format(company_id)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'ASP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__={}'.format(token),
            'Host': 'zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com/Tender/T-000001749',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        r = requests.get(url, headers=headers)
        return r.text

    def get_organization(self, name, inn, kpp):
        url = 'http://organizationHost/organization?inn={}&kpp={}&name={}'.format(inn, kpp, name)
        # r = requests.get(url)
        # return r.json()
        # заглушка
        if name is None:
            return None
        return {
            'guid': None,
            'name': name,
            'region': None
        }

    def get_stages_list(self, lot_uid, lot_url, token):
        url = 'https://zakupki.ugmk.com/Tenders/LoadNotices?lotUId={}'.format(lot_uid)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=vvselgjio1azsx5igfremgcb; __RequestVerificationToken_Lw__={}'.format(token),
            'Host': 'zakupki.ugmk.com',
            'Origin': 'https://zakupki.ugmk.com',
            'Pragma': 'no-cache',
            'Referer': 'https://zakupki.ugmk.com{}'.format(lot_url),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'offset': 0,
            'limit': 1000,
            'sortColumn': None,
            'sortAsc': False,
            '__RequestVerificationToken': token
        }
        r = requests.post(url, data, headers=headers)
        return r.json()['Rows']



