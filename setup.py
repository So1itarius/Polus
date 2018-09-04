from src.collector import Collector

if __name__ == "__main__":
    collector = Collector()
    #Для удобства я использую сортировку страниц сайта, поэтому такая ссылка
    starturl = "http://tenders.polyusgold.com/purchases/?NAME=&CODE=&BU=&PT=&ORDER=DATE_ACTIVE_TO%3AASC"
    archiveurl = "http://tenders.polyusgold.com/archive/?NAME=&BU=&PT=&ORDER=DATE_ACTIVE_TO%3ADESC"
    #Запускаем активные и архив по очереди,передавая статус и время
    p = collector.collect(starturl, "2", None)
    print("checking archive ...")
    collector.collect(archiveurl, "3", p)