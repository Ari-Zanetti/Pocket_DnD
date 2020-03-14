## path move
* greet
  - action_generate_labyrinth
  - slot{"name": "Enchanted Forest", "n_rooms": 5, "user": 1}
  - utter_greet
  
## path move 1
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
* affirm
  - action_move
  - slot{"level": 1, "current_monster": "vampire", "weapons": ["the Rifle of the Shadows", "the Axe of the Silence"]}
  
## path move 2
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
* affirm
  - action_move
  - slot{"level": 1, "current_monster": "vampire", "weapons": []}
  
## path fight
* fight_form
  - fight_form
  - form{"name": "fight_form"}
  - form{"name": null}
* affirm
  - utter_next_action
  
## path escape
* escape
  - action_escape
  
## path new_room
* new_room
  - action_newroom
    
## incorrect
* deny
  - utter_next_action