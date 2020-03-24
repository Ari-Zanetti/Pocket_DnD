import random
from typing import Dict, Text, Any, List, Union, Optional
from rasa.core.slots import Slot
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import Restarted
from rasa_sdk.events import FollowupAction
from rasa_sdk.forms import FormAction

MONSTER = 0
TREASURE = 1
EXIT = 2
NOTHING = 3

adjectives = ["Occult", "Forsaken", "Ancient", "Enchanted", "Crystal", "Haunted", "Emerald", "Laughing", "Wicked", "Whispering"]
nouns = ["Dungeon", "Forest", "Catacombs", "Pit", "Tomb", "Cavern", "Tunnel", "Mine", "Vault", "Crypt"]

weapon_adjectives = ["Twilight", "Lone Victory", "Silence", "Oblivion", "Eternal Bloodlust", "Shadows", "Assassin", "Oracle", "Timeless Battle"]
weapon_nouns = ["Bow", "Sword", "Dagger", "Rifle", "Shotgun", "Hammer", "Scythe", "Lasso", "Spear"]

monsters = ["troll", "vampire", "demon"]

MAX_ROOMS = 5

MAX_MONSTERS = 2
MAX_TREASURES = 3

rooms_db = {}


def get_new_user_id() :
	current_user = len(rooms_db) + 1
	return current_user

def get_next_room_number(user_id) :
	current_rooms = list(rooms_db[user_id].keys())
	current_rooms.sort(reverse=True)
	return current_rooms[0] + 1


def random_bool() :
	return random.choice([True, False])


def roll_die() :
	return random.randint(1, 6)


class User:
	def __init__(self, user_id, life, n_rooms, weapons=[]):
		self.user_id = user_id
		self.weapons = weapons
		self.life = life
		self.n_rooms = n_rooms


class Room:
	def __init__(self, number, previous, min_doors = 1, max_doors = 2):
		self.id = number
		self.monsters = random.randint(0, MAX_MONSTERS)
		self.found_monsters = []
		self.treasures = random.randint(1, MAX_TREASURES)
		self.found_treasures = []
		self.doors = random.randint(min_doors, max_doors) if max_doors > 0 else 0
		self.right_path = 0 if self.doors == 0 else random.randrange(self.doors)
		self.previous = previous
		self.next = []
        
	def add_new_room(self, user):
		room_number = get_next_room_number(user.user_id)
		min_doors = 1
		user_rooms = rooms_db[user.user_id]
		remaining_rooms = user.n_rooms - len(user_rooms)
		if user.n_rooms == len(user_rooms):
			remaining_rooms += 1
		if len(self.next) != self.right_path:
			min_doors = 0 # Not on the right path, so it can be a dead end.
		new_room = Room(room_number, self.id, min_doors, remaining_rooms - 1)
		self.next.append(room_number)
		user_rooms[room_number] = new_room
		return room_number

	def move(self, user):
		if self.monsters > 0:
			is_monster = random_bool()
			if is_monster:
				self.monsters -= 1
				found_monst = random.choice(monsters)
				self.found_monsters.append(found_monst)
				return MONSTER, found_monst
		if self.treasures > 0:
			is_treasure = random_bool()
			if is_treasure:
				self.treasures -= 1 
				weapon = random.choice(weapon_nouns) + " of the " + random.choice(weapon_adjectives)
				user.weapons.append(weapon)
				return TREASURE, weapon
		if len(self.next) < self.doors and random_bool():
			room_number = self.add_new_room(user)
			return EXIT, room_number
		return NOTHING, "nothing"


class ActionGenerateLabyrinth(Action):

	def name(self) -> Text:
		return "action_generate_labyrinth"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		name = random.choice(adjectives) + " " + random.choice(nouns)
		n_rooms = random.randint(1, MAX_ROOMS) + 1
		userid = get_new_user_id()
		first_room = Room(0, None)
		rooms_db[userid] = {0: first_room}
		
		return [SlotSet("name", name), SlotSet("n_rooms", n_rooms), SlotSet("user", userid)]


def get_room(user, rooms, room_id):
	for room in rooms:
		if int(room) == int(room_id): 
			return rooms_db[user.user_id][room]
	return None


def get_current_user_room(tracker):
	user = User(tracker.get_slot("user"), tracker.get_slot("life"), tracker.get_slot("n_rooms"), tracker.get_slot("weapons"))
	current_room = tracker.get_slot("current_room")
	user_rooms = rooms_db[user.user_id]
	room = user_rooms[int(current_room)]
	return user, room


class ActionMoveTo(Action):

	def name(self) -> Text:
		return "action_moveto"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		returned = [SlotSet("object", None), SlotSet("next_action", None)]
		user, room = get_current_user_room(tracker)
		current_room = tracker.get_slot("current_room")
		value = tracker.get_slot("object")
		# Check if it is a treasure or monster in the room
		if isinstance(value,str) and not value.isnumeric():
			if value.lower() == "monster":
				if len(room.found_monsters) > 0:
					current_monster = room.found_monsters[0]
					room.monsters -= 1
					dispatcher.utter_message(text="You reach a " + current_monster+ ". What do you do?")
					returned.append(SlotSet("current_monster", current_monster))
				else:
					dispatcher.utter_message(text="You don't see any monster here.")
				return returned
			elif value.lower() == "treasure":
				if len(room.found_treasures) > 0:
					current_treasure = room.found_treasures.pop(0)
					room.treasures -= 1
					user.weapons.append(current_treasure)
					dispatcher.utter_message(text="<speak><emphasis level='strong'>You now have the "+ current_treasure + ".</emphasis><break time='0.1'/> What do you want to do?</speak>")
					returned.append(SlotSet("weapons", user.weapons))
				else:
					dispatcher.utter_message(text="You don't see any treasure here.")
				return returned
			elif value.lower() == "next":
				value = room.next[-1] if len(room.next) > 0 else 0
			elif value.lower() == "previous":
				value = room.previous
				if value is None:
					dispatcher.utter_message(text="This is the first room!")
					return returned
			else:
				dispatcher.utter_message(text="You can't go here, what do you want to do?")
				return returned
		new_room = None
		reachable_rooms = []
		reachable_rooms = room.next
		if room.previous is not None:
			reachable_rooms.append(room.previous)
		new_room = get_room(user, reachable_rooms, value)
		if not new_room:
			dispatcher.utter_message(text="You cannot reach this room from here.")
			return returned

		if str(value) == str(user.n_rooms):
			dispatcher.utter_message(text="<speak><emphasis level ='moderate'>You have reached the final room! <prosody pitch='high'>You win!!</prosody></emphasis></speak>")
			return [Restarted()]
		else:
			dispatcher.utter_message(text="Welcome to room number " + str(value) + ", what do you want to do?")
		returned.append(SlotSet("current_room", value))
		return returned


class ActionMove(Action):

	def name(self) -> Text:
		return "action_move"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user, room = get_current_user_room(tracker)

		choice, result = room.move(user)
		slots = [SlotSet("weapons", user.weapons)]
		
		if choice == MONSTER:
			dispatcher.utter_message(text="You encountered a " + result + " what do you want to do?")
			slots.append(SlotSet("current_monster", result))
		elif choice == EXIT:
			dispatcher.utter_message(text="You found the door to room number " + str(result) + ". What do you want to do?")
			slots.append(SlotSet("object", result))
		else:
			slots.append(SlotSet("object", None))
			dispatcher.utter_message(text="You found " + result + ". What do you want to do next?")

		slots.append(SlotSet("direction", None))
		slots.append(SlotSet("next_action", None))
		return slots


class ActionExplore(Action):

	def name(self) -> Text:
		return "action_explore"
	
	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user, room = get_current_user_room(tracker)
		revealed_monsters = 0
		for i in range(room.monsters):
			if roll_die() > 3:
				revealed_monsters += 1
				room.found_monsters.append(random.choice(monsters))
				room.monsters -= 1
		revealed_treasures = 0
		for i in range(room.treasures):
			if roll_die() > 4:
				revealed_treasures += 1
				room.found_treasures.append(random.choice(weapon_nouns) + " of the " + random.choice(weapon_adjectives))
				room.monsters -= 1
		revealed_doors = 0
		for i in range(room.doors):
			if roll_die() > 5:
				revealed_doors += 1
				room.add_new_room(user)
		if (revealed_monsters == 0 and revealed_treasures == 0 and revealed_doors == 0):
			dispatcher.utter_message(text="There is a thick fog in the room, you can't see anything.")
		else:
			message = "You can see "
			comma = False
			if int(revealed_monsters) > 0:
				comma = True
				if int(revealed_monsters) > 1:
					message += str(revealed_monsters) + " monsters"
				else:
					message+="1 monster"
			if int(revealed_treasures) > 0:
				if comma:
					message += ", "    
				comma = True
				if int(revealed_treasures) > 1:
					message += str(revealed_treasures) + " treasures"
				else:
					message+="1 treasure"
			if int(revealed_doors) > 0:
				if comma:
					message += ", "    
				if int(revealed_doors) > 1:
					message += str(revealed_doors) + " doors"
				else:
					message+="1 door"
			message +="."
			dispatcher.utter_message(text=message)
		return [SlotSet("next_action", None)]


class ActionFight(Action):

	def name(self) -> Text:
		return "action_fight"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		user, room = get_current_user_room(tracker)
		monster = tracker.get_slot("current_monster")
		weapon = tracker.get_slot("fight_with")
		all_weapons = tracker.get_slot("weapons")
		life = int(tracker.get_slot("life"))

		returned = [SlotSet("next_action", None)]
		if roll_die() > 4:
			life += 1
			dispatcher.utter_message(text="You defeated the monster! What do you want to do?")
			if monster == "monster":
				room.found_monsters.pop(0)
			else:
				room.found_monsters.remove(monster)
			returned.append(SlotSet("current_monster", None))
			returned.append(SlotSet("fight_with", None))
		else :
			life -= 1
			if life == 0 :
				dispatcher.utter_message(template="utter_lose")
				return [Restarted()]
			lose_weapon = random_bool()
			message = "The monster hits you, you now have "
			if int(life) > 1:
				message += str(life) + " lives"
			elif int(life) == 1:
				message += "1 life"
			if weapon in all_weapons and lose_weapon:
				message += " and you lost your " + weapon
				all_weapons.remove(weapon)
				returned.append(SlotSet("weapons", all_weapons))
			dispatcher.utter_message(text=message +". What do you want to do?")
			returned.append(SlotSet("current_monster", monster))
		returned.append(SlotSet("life", life))
		returned.append(FollowupAction("action_listen"))
		return returned


class ActionEscape(Action):

	def name(self) -> Text:
		return "action_escape"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		if random_bool():
			dispatcher.utter_message(text="<speak><emphasis level='strong'>Nice escape!</emphasis></speak>")
			return [SlotSet("current_monster", None)]
		current_monster = tracker.get_slot("current_monster")
		message = "Oh no, the " + current_monster + " is following you!!"
		life = int(tracker.get_slot("life"))
		life -= 1
		if life == 0 :
			message += " You don't have any more lives. You lost!"
			dispatcher.utter_message(text=message)
			return [Restarted()]
		else:
			message+= " You now have "
		if int(life) > 1:
			message += str(life) + " lives"
		elif int(life) == 1:
			message += "1 life."
		dispatcher.utter_message(text=message)
		return [SlotSet("next_action", None), SlotSet("life", life)]


class MoveForm(FormAction):

	def name(self) -> Text:
		return "move_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		if tracker.get_slot("object"):
			return []
		else :
			return ["direction"]

	def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
		return {
			"direction": self.from_entity(entity="direction"),
			"object": self.from_entity(entity="object"),
		}
    
	def validate_direction(self, value, dispatcher, tracker, domain):
		return {"direction": value, "object": None}


	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict]:
		next_action = "move" 
		returned = []
		if tracker.get_slot("object") is not None:
			next_action += " to " + str(tracker.get_slot("object"))
			returned.append(FollowupAction("action_moveto"))
		elif tracker.get_slot("direction"):
			next_action += " " + str(tracker.get_slot("direction"))
			returned.append(FollowupAction("action_move"))
		returned.append(SlotSet("next_action", next_action))
		return returned
        
    
class FightForm(FormAction):

	def name(self) -> Text:
		return "fight_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		return ["current_monster", "fight_with"]

	def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
		return {
			"fight_with": self.from_entity(entity="fight_with"),
			"current_monster": self.from_entity(entity="current_monster"),
		}
    
	def validate_fight_with(self, value, dispatcher, tracker, domain):
		weapon = None
		for weapon_name in tracker.get_slot("weapons"):
			if value.lower() == weapon_name.lower():
				weapon = value
		if weapon is not None:
			return {"fight_with": weapon}
		else:
			dispatcher.utter_message(text="You don't have a " + value + ", please choose a weapon.")
			return {"fight_with": None}

	def validate_current_monster(self, value, dispatcher, tracker, domain):
		user, room = get_current_user_room(tracker)
		if value in room.found_monsters:
			return {"current_monster": value}
		else :
			dispatcher.utter_message(text="There is no " + value + " in this room.")
			return {"current_monster": None}

	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict]:
		next_action = "fight with " +  tracker.get_slot("fight_with")
		return [SlotSet("next_action", next_action), FollowupAction("action_fight")]