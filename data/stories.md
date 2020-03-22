## path greet
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
  - slot{"life": 3, "current_monster": "vampire", "weapons": ["the Rifle of the Shadows", "the Axe of the Silence"]}
  
## path move 2
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
* affirm
  - action_move
  - slot{"life": 2, "current_monster": "vampire", "weapons": []}
  
## path move 3
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - action_move
  - slot{"life": 3, "current_monster": "vampire", "weapons": ["the Rifle of the Shadows", "the Axe of the Silence"]}
  
## path move 4
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - action_move
  - slot{"life": 3, "current_monster": "vampire", "weapons": [], "object": null}
  
## path move 5
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - action_moveto
  - slot{"life": 3, "current_monster": "vampire", "weapons": [], "object": 1}
  
## path fight 1
* fight_form
  - fight_form
  - form{"name": "fight_form"}
  - form{"name": null}
  - action_fight
  - slot{"current_monster": "vampire", "life": 2, "weapons": ["the Axe of the Silence"]}
* affirm
  - utter_next_action
  
## path fight 2
* fight_form
  - fight_form
  - form{"name": "fight_form"}
  - form{"name": null}
  - action_fight
  - slot{"current_monster": null, "life": 2, "weapons": ["the Axe of the Silence"]}
* affirm
  - utter_next_action
  
## path escape
* escape
  - action_escape
  
## path move 6
* move_form {"object": "1"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - action_moveto
  - slot{"life": 3, "current_monster": "vampire", "weapons": ["the Axe of the Silence"], "object": "monster"}
  
## path move 7
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - slot{"life": 3, "current_monster": "vampire", "weapons": ["the Axe of the Silence"], "object": "treasure"}
 
 ## path move 8
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
  - action_moveto
  - slot{"life": 3, "current_monster": null, "weapons": [], "object": "2"}
  
## path move 9
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}  
  - action_moveto
  - slot{"life": 3, "current_monster": "vampire", "weapons": [], "object": "next"}
  
## path explore
* explore
  - action_explore
    
## incorrect
* deny
  - utter_next_action