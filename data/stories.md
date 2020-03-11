## day path
* greet
  - utter_greet
* affirm
  - utter_wh_person
* inform_person{"person":"Vlad Maraev"}
  - utter_wh_day
* inform_day{"date":"Monday"}
  - utter_all_day
* affirm
  - utter_yn_correct_day
  
## time path
* greet
  - utter_greet
* affirm
  - utter_wh_person
* inform_person{"person":"Vlad Maraev"}
  - utter_wh_day
* inform_day{"date":"Monday"}
  - utter_all_day
* deny
  - utter_wh_time
* inform_time{"time":"10 am"}
  - utter_yn_correct_time
    
## incorrect
* deny
  - slot{"person": null}
  - slot{"date": null}
  - slot{"time": null}
  - utter_wh_person
  
## correct
* affirm
  - utter_inform