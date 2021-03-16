import Database 

db = Database.Db("GuyHub.db")


guy = db.add_user("Guy","PassGuy")
rud = db.add_user("Rudich","PassRud")
dan = db.add_user("Dan","PassDan")
elon = db.add_user("Elon","$TSLA")

db.add_repo(db.get_user("Elon"),"Tesla")
db.add_repo(db.get_user("Guy"),"Blender")
db.add_repo(db.get_user("Guy"),"Godot")

db.add_user_to_repo(db.get_user("Dan"),db.get_repo("Blender"))