from cosmicac import db, create_user, model, create_room, create_userHistory

db.create_all()


create_room( 'Lab1', 'PKI 260', 'Computer lab', 'Computer lab for doing stuff', 'image')
create_room( 'Lab2', 'PKI 170', 'Computer lab2', 'Computer lab for doing stuff2', 'image2')
create_user('admin', 'admin@example.com', 'password', is_admin=True)
create_user('user1', 'user1@example.com', 'password', is_admin=False)
create_user('user2', 'user2@example.com', 'password', is_admin=False)
create_user('user3', 'user3@example.com', 'password', is_admin=False)
create_user('user4', 'user4@example.com', 'password', is_admin=False)
create_user('user5', 'user5@example.com', 'password', is_admin=False)
create_user('user6', 'user6@example.com', 'password', is_admin=False)
create_user('user7', 'user7@example.com', 'password', is_admin=False)
create_userHistory('user1', 'Lab1')
create_userHistory('user2', 'Lab2')
create_userHistory('user3', 'Lab2')