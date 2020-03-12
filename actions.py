from typing import Dict, Text, Any, List, Union, Optional
from rasa.core.slots import Slot
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.forms import FormAction

import random

MONSTER = 0
TREASURE = 1
EXIT = 2
NOTHING = 3

adjectives = ["Occult", "Forsaken", "Ancient", "Enchanted", "Crystal", "Haunted", "Emerald", "Laughing", "Wicked", "Whispering"]
nouns = ["Dungeon", "Forest", "Catacombs", "Pit", "Tomb", "Cavern", "Tunnel", "Mine", "Vault", "Crypt"]

weapon_adjectives = ["Twilight", "Lone Victory", "Silence", "Oblivion", "Eternal Bloodlust", "Shadows", "Assassin", "Oracle", "Timeless Battle"]
weapon_nouns = ["Axe", "Bow", "Sword", "Dagger", "Rifle", "Shotgun", "Hammer", "Scythe", "Lasso", "Spear"]

monsters = [("Zombie", 3), ("Vampire", 4), ("Demon", 5)]

MAX_ROOMS = 5

MAX_MONSTERS = 2
MAX_TREASURES = 3

rooms_db = {}

def get_new_user_id() :
	current_user = len(rooms_db) + 1
	return current_user

def random_bool() :
	return random.choice([True, False])

class User:
	def __init__(self, user_id, level=0, weapons=[]):
		self.user_id = user_id
		self.current_level = level
		self.current_weapons = weapons

class Room:
	def __init__(self, user):
		if user.current_level == 0:
			self.monsters = 0
		else :
			self.monsters = random.randrange(MAX_MONSTERS*user.current_level)
		self.treasures = random.randrange(MAX_TREASURES)
		self.user = user
		self.door = False
		self.next = None

	def move(self):
		if self.monsters > 0:
			is_monster = random_bool()
			if is_monster:
				self.monsters -= 1
				return MONSTER, random.choice(monsters)
		if self.treasures > 0:
			is_treasure = random_bool()
			if is_treasure:
				self.treasures -= 1 
				self.user.current_level +=1
				weapon = random.choice(weapon_nouns) + " of the " + random.choice(weapon_adjectives)
				self.user.current_weapons.append(weapon)
				return TREASURE, weapon
		if random_bool():
			door = True ##Visible?????
			return EXIT, "new_room"
		return NOTHING, "nothing"


class ActionGenerateLabyrinth(Action):

	def name(self) -> Text:
		return "action_generate_labyrinth"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		name = random.choice(adjectives) + " " + random.choice(nouns)
		n_rooms = random.randrange(MAX_ROOMS) + 1
		userid = get_new_user_id()

		first_room = Room(User(userid))
		rooms_db[userid] = [first_room]
		
		return [SlotSet("name", name), SlotSet("n_rooms", n_rooms), SlotSet("user", userid)]


class ActionEnterRoom(Action):

	def name(self) -> Text:
		return "action_enter_room"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user = User(tracker.get_slot("level"), tracker.get_slot("weapons"))
		current_room = tracker.get_slot("current_room")
		max_rooms = tracker.get_slot("n_rooms")
		user_rooms = rooms_db[tracker.get_slot("user")]
		room = user_rooms[current_room]
		if room.next:
			current_room = room.next
		else : #new room
			current_room +=1
			room.next = current_room
			user_rooms.append(Room(user))
			if len(user_rooms) == n_rooms:
				dispatcher.utter_message(text="You have reached the final room!")

		return [SlotSet("current_room", current_room)]


class ActionMove(Action): ##Go to should be a different action???

	def name(self) -> Text:
		return "action_move"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user = User(tracker.get_slot("level"), tracker.get_slot("weapons"))
		current_room = tracker.get_slot("current_room")
		room = rooms_db[tracker.get_slot("user")][current_room]
		choice, result = room.move()
		slots = [SlotSet("level", user.current_level), SlotSet("weapons", user.current_weapons)]
		if choice == MONSTER:
			dispatcher.utter_message(text="You encountered a " + result + " what do you want to do?")
			slots.append(SlotSet("current_monster", result))
		return slots

class ActionExplore(Action):

	def name(self) -> Text:
		return "action_explore"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		current_room = tracker.get_slot("current_room")
		room = rooms_db[tracker.get_slot("user")][current_room]
		dispatcher.utter_message(text="In this room there are " + room.monsters + " monsters and " + room.treasures + " treasures.")
		return []	


class ActionFight(Action):

	def name(self) -> Text:
		return "action_fight"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		current_room = tracker.get_slot("current_room")
		room = rooms_db[tracker.get_slot("user")][current_room]
		dispatcher.utter_message(text="You win!")
		return []	

class ActionEscape(Action):

	def name(self) -> Text:
		return "action_escape"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		if random_bool():
			dispatcher.utter_message(text="Nice escape!")
			return [SlotSet("current_monster", None)]
		current_monster = tracker.get_slot("current_monster")
		dispatcher.utter_message(text="Oh no, the " + current_monster + " is following you!!")
		return []


class NextActionForm(FormAction):

	def name(self) -> Text:
		return "next_action_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		if "move" == tracker.get_slot("next_action"):
			if not tracker.get_slot("object"):
				return ["direction"]
		elif "fight" == tracker.get_slot("next_action"):
			return ["fight_with"]
		return ["next_action"]

	def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
		return {
			"next_action": [self.from_intent(intent="move", value="move"),
							self.from_intent(intent="fight", value="fight"),
							self.from_intent(intent="explore", value="explore")],
			"fight_with": self.from_entity(entity="fight_with"),
			"direction": self.from_entity(entity="direction"), ##??? Left/Right/... but also objects?? use intents???
		}
		
	def validate_fight_with(self, value, dispatcher, tracker, domain):
		if value in tracker.get_slot("weapons"):
			return {"fight_with": value}
		else:
			dispatcher.utter_message(text="You don't have a " + value + "please choose a weapon.")
		
	def validate_direction(self, value, dispatcher, tracker, domain):
		#####
		return {"direction": value}

	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict]:
		next_action = tracker.get_slot("next_action") 
		if "move"== next_action:
			next_action = "move to " + tracker.get_slot("direction")
			if tracker.get_slot("object"):
				next_action += " to " + tracker.get_slot("object")
		elif "fight" == next_action:
			next_action = "fight with " +  tracker.get_slot("fight_with")

		dispatcher.utter_message(template="utter_confirm")
		return [SlotSet("next_action", next_action)]