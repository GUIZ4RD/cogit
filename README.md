### DISCLAIMER: This framework is released for internal purporse, it is buggy, incompleted and it need a lot of refactoring. It shouldn't be used for production. It is released under Open Source License, do what you prefer at your own risk.

# COGIT
## A framework to build multiplatform intelligent bots

## HOW IT WORK
### INITIAL CONFIGURATION
Configure your bot in settings.py file.


Define user-bot interaction in json files inside the corpora folder with the following constants:

- __PLATFORM__ the platform where the bot will run, currently the only supported platform is Messenger.
- __BASE_PATH__ the full path to the bot.py file (dumb thing sorry).
- __DB_NAME__ if you want to use the Sqlite ORM specify your db username here.
- __DB_USER__ if you want to use the Sqlite ORM specify your db username here.
- __DB_PSW__ if you want to use the Sqlite ORM specify your db password here.
- __MESSENGER_TOKEN__ your bot's private token for the messenger platform.
- __MESSENGER_VERIFY_TOKEN__ your bot's verify token for the messenger platform webhook configuration.
- __ALGORITHM__ the algorithm that will power your bot brain, options are "standard" for full-matching or "probabilistic" for TF/IDF.
- __PROBA_THRESHOLD__ if you want to use the probabilistic algorithm set the threshold here.
- __UNDER_MAINTENANCE__ put your bot under maintance, your bot will answer with UNDER_MAINTENANCE_MSG at each user except the DEV.
- __UNDER_MAINTENANCE_MSG__ the message shown when the bot is under maintenance.
- __DEV_ID__ if your bot is under maintenance it can interact only with this user.
- __PORT__ the port where the bot app will run.
- __DEBUG__ enable debug mode.

### DEFINE USER-BOT INTERACTION
You can define interactions in json files inside corpora folder.
An example of brain.json from Hi Coach:
```
{
	"revision": "1.1",

	"base": {
		"IS-STRING": {
			"text": "Hello there, what you want to do today ?",
			"choose": [
				["Choose a workout"],
				["Start your plan"],
				["Set a reminder"],
				["Nutrition facts"]
			],
			"context": "start-training"
		},
		"DEFAULT": {
			"text": "Sorry dude, I don't understand",
			"buttons": [
				["Hi Coach"],
				["Contact support", "Rate the Coach"]
			]
		},
		"hi coach": {
			"action": "stopWorkout",
			"id": true,
			"result": {
				"ok": {
					"text": "Hello there, what you want to do today ?",
					"choose": [
						["Choose a workout"],
						["Start your plan"],
						["Set a reminder"],
						["Nutrition facts"]
					],
					"context": "start-training"
				}
			}
		},
    "about me": {
			"text": "Hello there, I am Coach Bot, I can create personalized bodyweight workout for you every time that you need it, then I listen to your feedback to make the training perfect for you. Just tell me what you want to do.",
			"choose": [
				["Choose a workout"],
				["Start your plan"],
				["Set a reminder"],
				["Nutrition facts"]
			],
			"context": "start-training"
		},
		
		"motivate me":
		{
						"action": "getMotivation",
						"id": true,
						"result": {
						"ARRAY": {
					"template": "$TEXT. Check out this video $VIDEO",
					"context": "base"
				}
			}
		},

		"facebook page": {
			"text": "Follow Avada's Facebook Page for fitness tips fb.me/avadatech",
			"context": "base"
		},
		"rate the coach": {
			"text": "Do you want more training programs ? Rate the coach and we will add new workouts https://telegram.me/storebot?start=the_coach_bot",
			"context": "base"
		},
		"get avada app": {
			"text": "Download Avada iOS App for free and you will get full personalized functional bodyweight workouts https://itunes.apple.com/it/app/avada-training/id1078235590?mt=8&ign-mpt=uo%3D4&ls=1",
			"context": "base"
		},
		"contact support": {
			"text": "Contact us for support and feedback https://telegram.me/coachbot_support",
			"context": "base"
		},
		"back": {
			"text": "Okay, let me know when you want to workout",
			"context": "base"
		},
		"cancel": {
			"text": "Okay, let me know when you want to workout",
			"context": "base"
		}
	},

	"set-time": {
		"IS-STRING": {
			"action": "setAlertDays",
			"id": true,
			"result": {
				"ok": {
					"text": "At what time do you want to workout ? Insert it in 24h format",
					"context": "set-reminder"
				}
			}
		}
	},
}
```


In the examples above:
- __CONTEXTS__ are  "base" and "set-time
- __PATTERNS__  are "hi coach", "about you", "motivate me" ecc
- __PATTERNS PLACEHOLDER__ are "IS-STRING" and "DEFAULT", those repleace pattern for particular cases, DEFAULT is the answer for unmatched patterns, IS-STRING and IS-INT are used to handle variables.
- __ACTION__ are functions defined in functions.py they will be executed before sending the response, you can create conditional responses based on the result, if "id" is true the function will receive the user id as input.
You can define template for action response, you can use them returning a dict in function (with lowercase keys) and use the keys in the template as $KEY (uppercase key).
