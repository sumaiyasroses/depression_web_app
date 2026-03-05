import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

user_id = 1

contacts = {
"Aisha":[
("contact","Hey you didn’t reply yesterday. Everything okay?"),
("user","Yeah just tired."),
("contact","You sure? You sound different."),
("user","Didn't sleep much."),
("contact","Again?"),
("user","Yeah my mind keeps racing."),
("contact","Try to get some rest please."),
("user","It's already 2am and I'm still awake."),
("contact","You should sleep 😔"),
("user","I wish it was that easy.")
],

"Rahul":[
("contact","Bro where were you today"),
("user","Skipped class."),
("contact","You never skip."),
("user","Didn't feel like going."),
("contact","Everything alright?"),
("user","Just tired of everything."),
("contact","Come play football later"),
("user","Maybe"),
("contact","You've been quiet lately"),
("user","Yeah… just thinking a lot")
],

"Sara":[
("contact","Did you eat today?"),
("user","Not really."),
("contact","That's not good."),
("user","I forgot honestly."),
("contact","You should take care of yourself."),
("user","I'll try."),
("contact","You were online at 3am."),
("user","Couldn't sleep."),
("contact","You need proper rest."),
("user","Yeah I know.")
],

"Zain":[
("contact","Movie tonight?"),
("user","Not feeling like going out."),
("contact","Why?"),
("user","Just low energy."),
("contact","You’ve been saying that a lot."),
("user","Yeah sorry."),
("contact","Talk to me if something's wrong."),
("user","Maybe later."),
("contact","I'm here."),
("user","Thanks.")
],

"Fatima":[
("contact","You didn't come to lunch"),
("user","Wasn't hungry"),
("contact","That’s unlike you"),
("user","Just not feeling great"),
("contact","Are you stressed?"),
("user","Maybe"),
("contact","Don't keep everything inside"),
("user","I'll try"),
("contact","Promise?"),
("user","Yeah")
],

"Omar":[
("contact","Game tonight?"),
("user","Maybe not"),
("contact","You always play"),
("user","Just tired"),
("contact","Everything okay?"),
("user","Just bad sleep"),
("contact","You need rest"),
("user","I know"),
("contact","Take care bro"),
("user","Thanks")
],

"Lina":[
("contact","Why were you awake at 4am"),
("user","Couldn't sleep"),
("contact","Again insomnia?"),
("user","Yeah"),
("contact","Did something happen"),
("user","Just overthinking"),
("contact","You should relax more"),
("user","Trying"),
("contact","Talk anytime"),
("user","Thank you")
],

"Adnan":[
("contact","Assignment done?"),
("user","Not yet"),
("contact","Deadline is tomorrow"),
("user","I know"),
("contact","You okay?"),
("user","Hard to focus lately"),
("contact","Maybe take a break"),
("user","Yeah maybe"),
("contact","You'll manage"),
("user","Hope so")
],

"Nadia":[
("contact","Coffee later?"),
("user","Maybe another day"),
("contact","You sound tired"),
("user","Didn't sleep"),
("contact","Again?"),
("user","Yeah"),
("contact","That's not healthy"),
("user","I know"),
("contact","Take care please"),
("user","Thanks")
],

"Ibrahim":[
("contact","Gym today?"),
("user","Skipping"),
("contact","You never skip"),
("user","Just no energy"),
("contact","Rough day?"),
("user","Yeah"),
("contact","Rest then"),
("user","Probably"),
("contact","See you tomorrow"),
("user","Sure")
],

"Yusuf":[
("contact","Group study tonight"),
("user","I might pass"),
("contact","Why"),
("user","Hard to focus"),
("contact","You alright"),
("user","Just tired"),
("contact","Take a break"),
("user","Yeah"),
("contact","We'll catch up"),
("user","Okay")
],

"Hana":[
("contact","You looked upset today"),
("user","Did I"),
("contact","Yeah"),
("user","Just stressed"),
("contact","Want to talk"),
("user","Not now"),
("contact","Whenever you're ready"),
("user","Thanks"),
("contact","I'm here"),
("user","I know")
],

"Ali":[
("contact","Match tonight"),
("user","Skipping"),
("contact","Everything good"),
("user","Just low energy"),
("contact","Take rest"),
("user","Yeah"),
("contact","We'll play tomorrow"),
("user","Sure"),
("contact","Don't disappear"),
("user","I'll try")
],

"Maryam":[
("contact","Did you finish the report"),
("user","Not yet"),
("contact","Deadline soon"),
("user","I know"),
("contact","You seem stressed"),
("user","A little"),
("contact","Take it step by step"),
("user","Yeah"),
("contact","You'll manage"),
("user","Hope so")
],

"Bilal":[
("contact","Where are you these days"),
("user","Home mostly"),
("contact","Not going out?"),
("user","Not really"),
("contact","Everything okay"),
("user","Just tired"),
("contact","Call me sometime"),
("user","Sure"),
("contact","Take care"),
("user","Thanks")
],

"Amina":[
("contact","You sound sad"),
("user","Just tired"),
("contact","Want to talk"),
("user","Maybe later"),
("contact","Okay"),
("user","Thanks"),
("contact","Don't keep things inside"),
("user","I'll try"),
("contact","Promise"),
("user","Yeah")
],

"Farhan":[
("contact","Gaming tonight"),
("user","Not today"),
("contact","You okay"),
("user","Just tired"),
("contact","You say that often"),
("user","Yeah"),
("contact","Take care"),
("user","Thanks"),
("contact","See you later"),
("user","Sure")
],

"Rida":[
("contact","Why were you online at 3am"),
("user","Couldn't sleep"),
("contact","Again insomnia"),
("user","Yeah"),
("contact","Try relaxing"),
("user","Trying"),
("contact","Don't overthink"),
("user","Hard not to"),
("contact","Talk if needed"),
("user","Okay")
],

"Salman":[
("contact","Football tomorrow"),
("user","Maybe"),
("contact","You sure"),
("user","Depends"),
("contact","On what"),
("user","How I feel"),
("contact","Rest well"),
("user","I'll try"),
("contact","See you"),
("user","Yeah")
],

"Zoya":[
("contact","You seem distant lately"),
("user","Just tired"),
("contact","Something bothering you"),
("user","Maybe"),
("contact","Talk to me"),
("user","Later maybe"),
("contact","Okay"),
("user","Thanks"),
("contact","Take care"),
("user","You too")
]
}

now = datetime.now()

for contact, messages in contacts.items():

    time = now - timedelta(days=random.randint(3,10))

    for sender, msg in messages:

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO ai_chat (user_id, contact_name, sender, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,(user_id,contact,sender,msg,timestamp))

        time += timedelta(hours=random.randint(1,6))

conn.commit()
conn.close()

print("20 contacts with realistic chats inserted")