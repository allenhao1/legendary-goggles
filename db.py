from pymongo import MongoClient
import pymongo

client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['try2']
