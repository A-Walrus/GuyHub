import Database 

db = Database.Db("GuyHub.db")


# guy = db.add_user("Guy","PassGuy")
# rud = db.add_user("Rudich","PassRud")
# dan = db.add_user("Dan","PassDan")
# elon = db.add_user("Elon","$TSLA")

# db.add_repo(db.get_user("Elon"),"Tesla")
# db.add_repo(db.get_user("Guy"),"Blender")
# db.add_repo(db.get_user("Guy"),"Godot")

# db.add_user_to_repo(db.get_user("Dan"),db.get_repo("Blender"))
# db.add_branch("Feature2",1,db.get_user("Elon"),1)
# db.add_commit("Continuerer Feature","continuinging",4,8,db.get_user("Elon"))
for i in range(10,20):
	db.add_commit("Test %s"%i,"test",1,i,db.get_user("Elon"))