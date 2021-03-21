import Database 
import json

db = Database.Db("GuyHub.db")

# db.add_user("Ron","PassRon")
# db.add_user_to_repo({"id":5},{"id":3})
print(json.dumps(db.get_commits("Repos.id=1")))