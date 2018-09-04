import re
from decimal import Decimal
from datetime import datetime, timedelta
import time

class Tools():
    def clear(self, string):
        if string is None or string.strip() == '':
            return None
        return re.sub(' +',' ', string.strip().replace('\n','').replace('\r','').replace('\t',''))

    def to_decimal(self, string):
        if string is None or string.strip() == '' or string.strip() == 'Цена не определена':
            return None
        return Decimal(string.replace(' ','').replace(',','.').split('₽')[0])

    def get_utc_epoch(self, date_string):
        if date_string is None or date_string.strip() == '':
            return None

        date = datetime.strptime(date_string.replace('\n','').replace('\t', '').replace('\r', '').strip(), '%d.%m.%Y')
        epoch_time = (date - datetime(1970, 1, 1)).total_seconds() * 1000
        return int(epoch_time)

    def get_utc(self):
        return int(time.time()) * 1000
