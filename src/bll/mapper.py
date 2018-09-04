from src.tools import Tools
from sharedmodel.module import Root, Category, Field, Customer
from sharedmodel.module.table import Cell, Head, Body
from sharedmodel.module.enum import FieldType, Modification


class Mapper():
    def __init__(self):
        self.tools = Tools()

    def map_short(self, model):
        return {
            '_id': model['_id'],
            'status': model['status'],

        }

    def map_participant(self, participant):
        return {
            'admitted': True,
            'evolveDateTime': None,
            'guid': participant['guid'],
            'name': participant['name'],
            'price': None,
            'region': participant['region'],
            'rejectionCodes': [],
            'winner': True # потому что на этой площадке из участников показывается только победитель
        }

    def map(self, item, item1, item2, item3, item4, item5, multilot, attachments, customer, contacts,s):
        customer_search = '' if customer is None else '{} {}'.format(customer.get('name'), customer.get('region'))
        #participant_search = '' if participant is None else '{} {}'.format(participant.get('guid'), participant.get('name'))
        okpd = []
        okpd2= []
        okdp= []
        ktru= []
        #print([customer][0]['name'])
        model = {
            '_id': '{}'.format(item),
            'customers': [] if customer is None else [customer],
            #'participants': [] if participant is None else [self.map_participant(participant)],
            'type': 30, #change
            'timestamp': self.tools.get_utc(),
            'number': item,
            'group': item,
            'kind': 0,
            'orderName': item2,
            'maxPrice': None,
            'submissionCloseDateTime': self.tools.get_utc_epoch(item4),
            'submissionStartDateTime': None,
            'publicationDateTime': self.tools.get_utc_epoch(item5),
            'guaranteeApp': None,
            'guaranteeContract': None,
            'preference': [],
            'placingWay': 5000,
            'region': customer.get('region') if customer is not None else None,
            'okpd': okpd,
            'okpd2': okpd2,
            'okdp': okdp,
            'ktru': ktru,
            'prepayment': None,
            'organisationsSearch': '{}'.format(customer_search).strip(),
            'tenderSearch': '{} {} {}'.format(item, item2, customer.get('name')),
            'globalSearch': '{} {} {} {}'.format(okdp, okpd, okpd2, (item, item2, customer.get('name'))),
            'version': 1, # версия тендера если есть изменения????????
            'multiLot': multilot,
            'json': None,
            'attachments': attachments,
            'platform': {
                'href': "http://tenders.polyusgold.com/",
                'name': "«ПАО Полюс»",
            },
            'href': 'http://tenders.polyusgold.com/purchases/{}'.format(item1),
            'modification': None,#???????
            'futureNumber': None,#??????
            "guid": '{}'.format(customer.get('guid')),#????????
            'scoringDateTime': None,
            'biddingDateTime': None,
            'status': s #self.get_status(item['LotStatusName'])
        }
        json = self.get_json(model, contacts, item3)
        model.update({'json': json})
        return model

    def get_placingway(self, placingway, org_form):
        if placingway == 'Аукцион' and org_form == 'Закрытая':
            return 12
        elif placingway == 'Аукцион' and org_form == 'Открытая':
            return 2
        elif placingway == 'Конкурс' and org_form == 'Закрытая':
            return 9
        elif placingway == 'Конкурс' and org_form == 'Открытая':
            return 1
        elif placingway == 'Запрос цен' and org_form == 'Закрытая':
            return 4
        elif placingway == 'Запрос цен' and org_form == 'Открытая':
            return 4
        else:
            return 0

        # fortyfour = {
        #     "Открытый конкурс": 1,
        #     "Открытый аукцион": 2,
        #     "Открытый аукцион в электронной форме": 3,
        #     "Запрос котировок": 4,
        #     "Предварительный отбор": 5,
        #     "Закупка у единственного поставщика (подрядчика, исполнителя)": 6,
        #     "Конкурс с ограниченным участием": 7,
        #     "Двухэтапный конкурс": 8,
        #     "Закрытый конкурс": 9,
        #     "Закрытый конкурс с ограниченным участием": 10,
        #     "Закрытый двухэтапный конкурс": 11,
        #     "Закрытый аукцион": 12,
        #     "Запрос котировок без размещения извещения": 13,
        #     "Запрос предложений": 14,
        #     "Электронный аукцион": 15,
        #     "Иной многолотовый способ": 16,
        #     "Сообщение о заинтересованности в проведении открытого конкурса": 17,
        #     "Иной однолотовый способ": 18
        # }

    def get_status(self, string):
        if string is None or string.strip() == '':
            return 0

        #elif string == 'Опубликовано':
         #   return 1
        #elif string == 'Прием заявок':
         #   return 2
        elif string :
            return 2
        elif string == 'Проведена':
            return 3
        #elif string == 'Завершен':
        #    return 7
        #elif string == 'Не состоялся с выбором победителя' or string == 'Отменен':
        #    return 4
        #elif string == 'Договор завершен':
        #    return 6
        #elif string == 'Не состоялся' \
        #        or string == 'Не состоялся с заключением договора' \
        #        or string == 'Не состоялся без заключения договора':
        #    return 5
        #elif string == 'Заменен новой версией':
        #    return 0

        # Без статуса
        # None = 0,
        # Опубликован
        # Active = 1,
        # На рассмотрении комиссии
        # Commission = 2,
        # Закрыт
        # Closed = 3,
        # Отменен
        # Cancel = 4,
        # Приостановлен
        # Abandoned = 5,
        # Исполнение завершено
        # Played = 6,
        # Исполняется
        # Playing = 7,
        # Приостановлено определение поставщика
        # Suspended = 8

    def get_json(self, model, contacts, organization):
        return Root() \
            .add_general(
            Field(
                name="MaxPrice",
                type=FieldType.Price,
                value=model['maxPrice'],
                displayName="Цена контракта"
              )
             ) \
            .add_customer(
            Customer().set_properties(
                max_price=None,
                guarantee_app=None,
                guarantee_contract=None,
                customer_guid=model['customers'][0]['guid'],
                customer_name=model['customers'][0]['name']
            )
            ) \
            .add_category(
             lambda c: c.set_properties(
                name='ProcedureInfo',
                displayName='Порядок размещения заказа'
            ).add_field(Field(
                name='AcceptOrderEndDateTime',
                displayName='Дата окончания приема заявок',
                value=model['submissionCloseDateTime'],
                type=FieldType.DateTime,
                modifications=[Modification.Calendar]
              ))
            ) \
            .add_category(
            lambda c: c.set_properties(
                name='Contacts',
                displayName='Контактная информация'
            ).add_field(Field(
                name='Organization',
                displayName='Организация',
                value=organization,
                type=FieldType.String
            )).add_array(
                lambda ar: ar.set_properties(
                    name='Contacts',
                    displayName='Контакты',
                    modifications=[Modification.HiddenLabel]
                ).add_field(Field(
                    name='FIO',
                    displayName='ФИО',
                    value=contacts[0]['name'],
                    type=FieldType.String,
                    modifications=[Modification.HiddenLabel]
                )).add_field(Field(
                    name='Phone',
                    displayName='Телефон',
                    value=contacts[0]['phone'],
                    type=FieldType.String,
                    modifications=[]
                )).add_field(Field(
                    name='Email',
                    displayName='Электронная почта',
                    value=contacts[0]['email'],
                    type=FieldType.String,
                    modifications=[]
                ))
            )
           ) \
            .to_json()








