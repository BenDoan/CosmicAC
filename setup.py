from server import db, create_user, model

db.create_all()

create_user('admin', 'admin@example.com', 'password', is_admin=True)
create_user('user', 'user@example.com', 'password', is_admin=False)
