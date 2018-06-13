
import os
import time
import re
import urllib.request, json
from slackclient import SlackClient

# create Slack Client
android_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# bot userID in slack: value created after bot is online
android_id = None


# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == android_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    
    matches = re.search(MENTION_REGEX, message_text)
    
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    
    demand = command.split()
    head, tail = demand[0], demand[1:]
    
    default_response = "You make no sense... Try *{}*.".format(EXAMPLE_COMMAND)
    response = None
    
    #Assign1 command echos anything that ends in ?
    if command.endswith("?"):
        response = str(command)
    else:
        if command.startswith("who") or command.startswith("what") or command.startswith("where") or command.startswith("which") or command.startswith("why") or command.startswith("how"):
            response = "Huh? Are you trying to ask me a question? If so try ending it with ?"
        
    #personality
    if command == "dab" or command == "hit em with the dab":
        response = ":dab-squidward:"
    
    #personality
    if command == "school time":
        response = ":feels_bad: damn..."
    
    #personality
    if command.startswith("echo") or command.startswith("Echo"):
        response = " ".join(tail)
    
    #personality    
    if "do you do anything useful" in command:
        response = "do YOU do anything useful?"

    #personality
    if "whats the correct way of using curly brackets" in command:
        response = "function (param1, param2){\n}\nOf course. @Jacob Klimach knows."
    else:
        #This command is for "do"
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sounds good, tell me more info and i'll execute your wishes"
        
    if command.startswith("weather in"):
        split_command = command.split()
        if len(split_command) < 3 or len(split_command) > 4 or split_command[2] == '':
            response = "I dont understand. Which city do you want to know the current weather? Try \"@Android 21 weather in city country (optional)\""
        else:
            try:
                if len(split_command) == 3:
                    city = split_command[2]
                elif len(split_command) == 4:
                    city = split_command[2] + "," + split_command[3]
                query = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&APPID=d294f4b244f9be903cc8edf476c19ddb&units=metric"
                with urllib.request.urlopen(query) as url:
                    data = json.loads(url.read().decode())
                    print(data)
                    response = "Heres the weather in " + data['name'] + ", " + data['sys']['country'] + ":\n"
                    response += data['weather'][0]['description'] + "\n"
                    response += str(data['main']['temp']) + " degrees celsius\n"
                    print(data['weather'][0]['main'])
                    print(type (data['weather']))
            except urllib.error.HTTPError:
                response = "I dont understand. Which city do you want to know the current weather? Try \"@Android 21 weather in city country (optional)\""




    android_client.api_call("chat.postMessage", channel=channel, text=response or default_response)

if __name__ == "__main__":
    if android_client.rtm_connect(with_team_state=False):
        print("Systems running 100%, I'm Alive!!!")
        # read bots user ID by calling web apr method 'auth.test'
        android_id = android_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(android_client.rtm_read())
            
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Systems offline...")


