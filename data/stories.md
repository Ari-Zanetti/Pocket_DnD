## path move
* greet
  - action_generate_labyrinth
  - utter_greet
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
* affirm
  - action_move{"level":"1", "weapons":[], "current_monster":"vampire"}
  
## path fight
* greet
  - action_generate_labyrinth
  - utter_greet
* fight_form
  - fight_form
  - form{"name": "fight_form"}
  - form{"name": null}
* affirm
  - utter_next_action
    
## incorrect
* deny
  - utter_next_action
  
## move
* move_form {"direction": "forward"}
  - move_form
  - form{"name": "move_form"}
  - form{"name": null}
* affirm
  - action_move{"level":"1", "weapons":[], "current_monster":"vampire"}
  
## fight
* fight_form
  - fight_form
  - form{"name": "fight_form"}
  - form{"name": null}
* affirm
  - utter_next_action