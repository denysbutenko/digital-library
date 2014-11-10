from app import db, init_db
db.drop_all()
db.create_all()
init_db()
