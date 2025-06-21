import logging
from typing import Dict
from datetime import datetime, timedelta
from pymongo import MongoClient
from django.conf import settings

logger = logging.getLogger("")


class MongoRepository:
    def __init__(self, host, port, username, password, database):
        try:
            self.client = MongoClient(
                host=host,
                port=int(port),
                username=username,
                password=password
            )
            self.db = self.client[database]
        except Exception as e:
            logger.error(
                f'Fail to connect to MongoDB url {host}:{port}: {str(e)}')
            raise

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {e}")
            raise

    def insert_one(self, collection_name: str, document: Dict) -> str:
        try:
            result = self.db[collection_name].insert_one(document)
            logger.info(f"Inserted new document in {collection_name} payload {document}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document {document}: {str(e)}")
            raise

    def find_documents(self, collection_name, filter=None):
        return list(self.db[collection_name].find(filter or {}))

    def update_one(self, collection_name: str, before: Dict, after: Dict):
        try:
            if not before:
                self.insert_one(collection_name, after)
                return

            result = self.db[collection_name].update_one(
                before, {"$set": after}, upsert=False
            )
            if result.matched_count:
                logger.info(f"Updated document in {collection_name} where {before} to {after}")
            else:
                logger.warning(f"No matching document found for update: before {before} after {after}")
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            raise
