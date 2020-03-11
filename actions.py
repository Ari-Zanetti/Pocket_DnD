from typing import Any, Text, Dict, List
from rasa.core.slots import Slot
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import random

adjectives = ["Occult", "Forsaken", "Ancient", "Enchanted", "Crystal", "Haunted", "Emerald", "Laughing", "Wicked", "Whispering"]
nouns = ["Dungeon", "Forest", "Catacombs", "Pit", "Tomb", "Cavern", "Tunnel", "Mine", "Vault", "Crypt"]

weapon_adjectives = ["Twilight", "Lone Victory", "Silence", "Oblivion", "Eternal Bloodlust", "Shadows", "Assassin", "Oracle", "Timeless Battle"]
weapon_nouns = ["Axe", "Bow", "Sword", "Dagger", "Rifle", "Shotgun", "Hammer", "Scythe", "Lasso", "Spear"]

monsters = [("Zombie", 3), ("Vampire", 4), ("Demon", 5)]

MAX_ROOMS = 5

MAX_SIZE = 6
MAX_MONSTERS = 2
MAX_TREASURES = 2

rooms_db = {}
int current_user = 0

def get_user_id() :
	current_user += 1
	return current_user

def random_bool() :
	return random.choice([True, False])

class User:
	def __init__(self, level=0, weapons=[]):
		self.current_level = level
		self.current_weapons = weapons

class Room:
	def __init__(self, user):
		self.monsters = random.randrange(MAX_MONSTERS)
		self.treasures = random.randrange(MAX_TREASURES)
		self.size = random.randrange(MAX_SIZE)
		self.next = None

	def move(self):
		if self.monsters > 0:
			is_monster = random_bool()
			if is_monster:
				self.monsters -= 1
				return 0, random.choice(monsters)
		if self.treasures > 0:
			is_treasure = random_bool()
			if is_treasure:
				self.treasures -= 1 
				self.user.level +=1
				weapon = random.choice(weapon_nouns) + " of the " + random.choice(weapon_adjectives)
				self.user.weapons.append(weapon)
				return 1, weapon
		if random_bool():
			return 2, "new_room"
		return 3, "nothing"


class ActionGenerateLabyrinth(Action):

	def name(self) -> Text:
		return "action_generate_labyrinth"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		name = random.choice(adjectives) + " " + random.choice(nouns)
		n_rooms = random.randrange(MAX_ROOMS)
		user = get_user_id()

		first_room = Room(user)
		rooms_db[user] = [first_room]
		
		return [SlotSet("name", name), SlotSet("n_rooms", n_rooms), SlotSet("user", user)]


class ActionEnterRoom(Action):

	def name(self) -> Text:
		return "action_enter_room"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user = User(tracker.get_slot("level"), tracker.get_slot("weapons"))
		current_room = tracker.get_slot("current_room")
		max_rooms = tracker.get_slot("n_rooms")
		user_rooms = rooms_db[user]
		room = user_rooms[current_room]
		if room.next:
			current_room = room.next
		else : #new room
			current_room +=1
			room.next = current_room
			user_rooms.append(Room())
			if len(user_rooms) == n_rooms:
				dispatcher.utter_message(text="You have reached the final room!")


		return [SlotSet("current_room", current_room)]


class ActionMove(Action):

	def name(self) -> Text:
		return "action_move"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user = User(tracker.get_slot("level"), tracker.get_slot("weapons"))
		current_room = tracker.get_slot("current_room")
		room = rooms_db[user][current_room]
		result = room.move()
		return [SlotSet("level", user.level), SlotSet("weapons", user.weapons)]