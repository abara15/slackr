from json import dumps, load
import os.path


class DB:
    START_ID = 1

    def __init__(self, name, primary_key="id"):
        """
        Creates an empty in-memory database if no ./data/name.json exists in data folder.
        If a valid JSON file under .data/name.json exists, seeds the DB from the JSON file.
        """
        self.name = name
        self.primary_key = primary_key
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.json_path = os.path.join(dir_path, f"data/{name}.json")
        if os.path.exists(self.json_path):
            parsed, maxId = fromJson(self.json_path)
            self.dict = parsed
            self.nextId = maxId + 1
        else:
            self.dict = {}
            self.nextId = self.START_ID

    def get(self, id):
        """
        Returns the record with the specified ID (primary_key = id).
        Returns none if the ID does not exist in the database.
        """
        return self.dict.get(id, None)

    def query(self, key, operator, value):
        """
        Returns a list of all records that have a 'key' that match the specified
        operation with the provided value.
        Returns an empty list if no records match the value.
        Example: To return all users with a first_name of 'John': 
                 users.query('first_name', '=', 'john')
        Works with all python operations including checking if a value is in a list.
        """
        results = []
        for id in self.dict:
            record = self.dict[id]
            if key in record:
                current = record[key]
                if (
                        operator in ["is", "=", "=="]
                        and current == value
                        or operator in ["not", "!=", "!=="]
                        and current != value
                        or operator == "<"
                        and current < value
                        or operator == "<="
                        and current <= value
                        or operator == ">"
                        and current >= value
                        or operator == ">="
                        and current > value
                        or operator in ["contains", "in"]
                        and value in current
                ):
                    results.append(record)
        return results

    def list(self):
        """
        Returns a list with all the records in the DB.
        Returns an empty list if there are no records in the DB.
        """
        return list(self.dict.values())

    def add(self, payload):
        """
        Creates a new record with the given payload and returns the id
        of the created record.
        The id is stored under the primary_key in all records.
        """
        recordId = self.nextId
        payload[self.primary_key] = recordId
        self.dict[recordId] = payload
        self.nextId += 1
        return recordId

    def addWithId(self, payload, recordId):
        """
        Works like add but you specifiy the ID.
        Returns the specified ID.
        Overwrites the record with the specified ID if it already exists.
        """
        payload[self.primary_key] = recordId
        self.dict[recordId] = payload
        return recordId

    def set(self, id, keyToUpdate, newValueToSet):
        """
        Sets the keyToUpdate equal to newValueToSet on the record with the
        specified ID.
        If the key points to a list, adds the new value to the list.
        To remove a value from a list use the remove method.
        Raises an error if ID or key do not exist.
        """
        valueToUpdate = self.dict[id][keyToUpdate]
        if isinstance(valueToUpdate, list):
            self.dict[id][keyToUpdate].append(newValueToSet)
        else:
            self.dict[id][keyToUpdate] = newValueToSet
        return self.get(id)

    def remove(self, id, keyToAList, valueToRemove):
        """
        Given a record id and a key on that record that points to a list,
        removes the value from the list.
        Raises an error if ID does not exist or if key does not point to a list.
        """
        listToUpdate = self.dict[id][keyToAList]
        if not isinstance(listToUpdate, list):
            raise KeyError("Specified key must point to a list.")
        self.dict[id][keyToAList].remove(valueToRemove)
        return self.get(id)

    def delete_record(self, id):
        """
        Deletes the record of the given ID.
        """
        del self.dict[id]

    def size(self):
        """
        Returns the number of records in the DB.
        """
        return len(self.dict)

    def drop(self):
        """
        Deletes all records in the DB.
        """
        self.dict.clear()

    def saveAsJson(self):
        """
        Saves the DB in a JSON file with the same name as the DB name.
        """
        f = open(self.json_path, "w")
        f.write(dumps(self.dict))
        return self.json_path

    def __str__(self):
        result = ""
        result += f"====== Printing {self.name} ======\n"
        for key in self.dict:
            result += f"{key}: "
            result += self.dict[key].__str__() + "\n"
        result += "====== Printing Finished ======\n"
        return result

    def __len__(self):
        return len(self.dict)


def fromJson(filename):
    """
    Loads DB from a saved JSON file.
    """
    f = open(filename, "r")
    parsedJson = load(f)
    f.close()
    result = {}
    for key in parsedJson:
        result[int(key)] = parsedJson[key]
    return result, max(result)


##########################
# Global Databases
##########################


"""
User Record:
    u_id: int
    first_name: str
    last_name: str
    email: str
    handle_str: str
    img_url : str
    password_hash: str
    reset_codes: [str] -> List of valid password reset codes.
    is_admin: bool,
    is_slackr_owner: bool
"""
users = DB("users", "u_id")

"""
Channel Record:
    channel_id: int
    name: string
    all_members: [int] -> List of u_ids of all members including owners.
    owners: [int] -> List of u_ids of owners.
    is_public: bool
    is_standup_active: bool
    time_finish: datetime -> None if there is no standup active on the channel.
    standup_queue: [string] -> List of messages in the current standup queue, gets cleared when standup finished.
"""
channels = DB("channels", "channel_id")

"""
Message Record:
    message_id: int
    channel_id: int
    u_id: int
    message: str
    is_pinned: bool
    time_created: datetime
"""
messages = DB("messages", "message_id")

"""
React Record:
    id: int -> Record ID = Message ID.
    1: [] -> Lists that store the users that have used this react_id
    2: []
    3: []
    4: []
    5: []
    6: []
    7: []
    
"""
reacts = DB("reacts", "message_id")


##########################
# Helpers
##########################


def get_full_message(u_id, message_id):
    message_details = messages.get(message_id)
    message_reacts = reacts.get(message_id)
    reacts_returned = []
    for key in message_reacts:
        if key != "message_id" and message_reacts[key] != []:
            reacts_returned.append(
                {
                    "react_id": key,
                    "u_ids": message_reacts[key],
                    "is_this_user_reacted": u_id in message_reacts[key],
                }
            )
    return {
        "message_id": message_details["message_id"],
        "u_id": message_details["u_id"],
        "message": message_details["message"],
        "time_created": message_details["time_created"],
        "is_pinned": message_details["is_pinned"],
        "reacts": reacts_returned,
    }


def get_user_profile(u_id):
    user = users.get(u_id)
    return {
        "email": user["email"],
        "name_first": user["first_name"],
        "name_last": user["last_name"],
        "handle_str": user["handle_str"],
        "profile_img_url": user["img_url"],
    }
