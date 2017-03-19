from twitter import *
import xml.etree.ElementTree as ET

auth_file="auth.xml"
auth_tree = ET.parse(auth_file)
auth_root = auth_tree.getroot()

token_key=""
token_secret=""
consumer_key=""
consumer_secret=""

for service in auth_root.findall('service') :
    if service.get("name") == "twitter" :
        username = service.find("username").text
        consumer_key=service.find("consumer_key").text
        consumer_secret=service.find("consumer_secret").text
        token_key=service.find("access_token_key").text
        token_secret=service.find("access_token_secret").text

t = Twitter(auth=OAuth(token_key, token_secret, consumer_key, consumer_secret))

# Get your "home" timeline
#print(t.statuses.home_timeline())

query = t.followers.ids(screen_name = username)
print("Found %d followers" % (len(query["ids"])))

#users = t.GetFriends()
#print([u.name for u in users])

for n in range(0, len(query["ids"]), 100):
    ids = query["ids"][n:n+100]
    subquery = t.users.lookup(user_id = ids)
    for user in subquery:
        #print(user["id"])
        print(" [%s] %s" % ("*" if user["verified"] else " ", "@"+user["screen_name"]))
        try:
            print("Added ?")
            k=t.CreateFriendship(user_id=user["id"])
            print(k)
        except TwitterError:
            continue