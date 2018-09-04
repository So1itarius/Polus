from src.http import Http
from src.bll.mapper import Mapper
from src.bll.parser import Parser
from src.repository.mongodb import MongoRepository
from src.repository.rabbitmq import RabbitMqProvider
from settings import configparse


class Collector():
    def __init__(self):
        cfg = configparse()
        cfg_mongo = cfg['mongodb']
        cfg_rabbit = cfg['rabbitmq']

        self.http = Http()
        self.mapper = Mapper()
        self.parser = Parser()
        self.repository = MongoRepository(cfg_mongo['host'],
                                          cfg_mongo['port'],
                                          cfg_mongo['database'],
                                          cfg_mongo['collection'])
        self.rabbitmq = RabbitMqProvider(cfg_rabbit['host'],
                                         cfg_rabbit['port'],
                                         cfg_rabbit['username'],
                                         cfg_rabbit['password'],
                                         cfg_rabbit['queue'])
        self.token = None

    def collect(self,url,status,time):

       page_list=self.http.get_page_list(url)
       #Ищем и возвращаем время
       min_date=self.http.get_tender_mindate(url)

       y=0 #Счетчик страниц
       special_tender_list=[]
       print('preparation of a special list')
       g=0 #Еще один счетчик страниц
       for i in page_list:
           special_tender_list = special_tender_list + self.http.get_special_tender_list(i)
           print("check page ", g)
           g=g+1
       w1=set(special_tender_list)#превращаем список в множество, чтобы можно было проверить, принадлежит ли элемент множеству
       print('done')
       for i in page_list:
        t=len(page_list)
        y=y+1
        print('Page number [{}/{}]'.format(y, t))
        tender_list_with_info=self.http.get_tender_list(i,status,time)
        z=0
        #Проверка на повторные публикации
        for j in tender_list_with_info:
            if set(j).isdisjoint(w1) is False and self.parser.special_search(tender_list_with_info[z][2]) is None:
                tender_list_with_info.remove(j)
                print("Remove: ",j)
            z=z+1
        total = len(tender_list_with_info)
        prev = None

        for i, item in enumerate(tender_list_with_info):
            print('[{}/{}] Processing tender number: {}'.format(i+1, total, item[0]))
            if prev != item[0]:
                self.process_tender(item[0],item[1],item[2], item[3],item[4],item[5], status)
            prev = item[0]

       return min_date

    def process_tender(self,item,item1,item2,item3,item4,item5,st):

        multilot = False

        tender_attachments_html = self.http.get_tender_documents(item1)#--Получаем страницу с данными документа
        attachments = self.parser.get_attachments(tender_attachments_html)

        contacts_html = self.http.get_tender_contacts(item1)#--Получаем контакты:имя и телефон
        contacts = self.parser.get_contacts(contacts_html)

        customer = None
        if item1 is not None:
                customer = self.http.get_organization(item3, None, None)##-возвращаем модель/заглушку???

        model = self.mapper.map(item, item1, item2, item3, item4, item5, multilot, attachments, customer, contacts, st)
        short_model = {
                '_id': model['_id'],
                'status': st,
                'time': model['submissionCloseDateTime']
            }
        a2=self.repository.get_status(model['_id'])
        #Проверка, если тендер был в активных, но обнаружился в архиве, то его статус обновляется и в базу он не заносится
        if a2 is not None and st == '3' and a2['status'] == '2':
            self.repository.update(model['_id'], '3', model['submissionCloseDateTime'])
            return "Coincidence..."

        self.repository.upsert(short_model)
        print('Upserted in MongoDB')
        self.rabbitmq.publish(model)
        print('Published to RabbitMQ')






