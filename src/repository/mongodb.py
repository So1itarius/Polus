from pymongo import MongoClient

class MongoRepository():
    def __init__(self, host, port, database, collection):
        self.collection = MongoClient(host, port)[database][collection]

    def get_one(self, id):
        result = self.collection.find_one({ '_id': id })
        return result

    def get_status(self, st):
        result = self.collection.find({'status': st})
        return result

    def remove(self,i,st):
        result = self.collection.remove({"_id": i, "status": st})
        return result

    def update(self, id, st, time):
        self.collection.update_one({'_id': id},{'status': st, 'time': time})

    def upsert(self, shortmodel):
        self.collection.update_one({
            '_id': shortmodel['_id']
        },{
            '$set': {'status': shortmodel['status'], 'time': shortmodel['time']}
            },  True)

