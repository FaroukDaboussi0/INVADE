from pymongo import MongoClient

class Documents:
    def __init__(self, db_name='appcreator', collection_name='appdata'):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.ids = {}

    def set_ids(self, ids):
        self.ids = ids
        # Save the IDs to MongoDB
        self.collection.update_one(
            {'_id': 'document_ids'},
            {'$set': {'ids': self.ids}},
            upsert=True
        )

    def get_disponible_documents(self):
        # Load the document with _id = 'document_ids' from MongoDB
        document = self.collection.find_one({'_id': 'document_ids'})
        if document:
            # Update self.ids with the loaded document's ids
            self.ids = document.get('ids', {})
        # Return existing keys in the set IDs
        return list(self.ids.keys())

    def get_document_by_key(self, key):
        # Load IDs from MongoDB
        document = self.collection.find_one({'_id': 'document_ids'})
        if (document):
            self.ids = document.get('ids', {})
        # Find the ID corresponding to the key
        document_id = self.ids.get(key)
        if document_id:
            # Load the document from its ID from the db

            return self.collection .find_one({'_id': document_id})
        return None

    def save_document(self, document, key):
        # Set a custom _id for the document
        document['_id'] = key
        # Save the document in the collection
        result = self.collection .insert_one(document)
        document_id = result.inserted_id
        # Append the document ID to the ids dictionary
        self.ids[key] = document_id
        # Update the ids dictionary in the database
        self.collection.update_one(
            {'_id': 'document_ids'},
            {'$set': {'ids': self.ids}},
            upsert=True
        )
        return document_id

    def find(self,d, key):
        found = []
        if isinstance(d, dict):
            for k, v in d.items():
                if k == key:
                    found.append(v)
                else:
                    found.extend(self.find(v, key))
        elif isinstance(d, list):
            for item in d:
                found.extend(self.find(item, key))
        return found

    def remove_key(self,data, target_key):
    
        if isinstance(data, dict):
            # Create a copy of the dictionary without the target key
            modified_data = {key: value for key, value in data.items() if key != target_key}
            
            # Recursively call the function on the remaining keys
            for key, value in modified_data.items():
                modified_data[key] = self.remove_key(value, target_key)
                
            return modified_data

        elif isinstance(data, list):
            # If it's a list, recursively call the function on each item
            return [self.remove_key(item, target_key) for item in data]

        return data 
    
    def get_sub_dict_from_key(self,data, target_key):
    
        if isinstance(data, dict):
            # If it's a dictionary, check if the key exists and return its value
            if target_key in data:
                return data[target_key]
            
            # If the key is not found, continue searching recursively in the values
            for key, value in data.items():
                result = self.get_sub_dict_from_key(value, target_key)
                if result is not None:
                    return result

        elif isinstance(data, list):
            # If it's a list, search through each item in the list
            for item in data:
                result = self.get_sub_dict_from_key(item, target_key)
                if result is not None:
                    return result

        # Return None if the key is not found in the current structure
        return None
