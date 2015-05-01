import os
import cosmicac
from cosmicac import db, create_user, model, create_room, create_userHistory

if not os.path.isdir(cosmicac.UPLOAD_FOLDER):
    os.mkdir(cosmicac.UPLOAD_FOLDER)

db.drop_all()
db.create_all()
long_desc1 = """ 
## This is the Civil Engineering Lab

## What we do
Civil engineering applies the laws and principles of 
the basic sciences, primarily mechanics, to the design,
modification, construction, and building of structures
of all kinds, to resist and harness the forces of 
nature, and to improve the quality of life. Civil 
engineers are responsible for planning, designing, 
constructing, and operating structures, water-supply and 
waste-disposal systems, air- and water- pollution-control
systems, flood-control systems, and transportation 
systems. In essence, civil engineers are concerned with 
the environment of modern society.

## ABET Accreditation
Our undergraduate program is accredited by the 
Engineering Accreditation Commission of ABET.

"""

long_desc3 = """ 
## This is the Computer Science Lab

## What we do
Computer Science (CS) is the fundamental discipline in 
information technology. As a member of the UNO community 
for more than 30 years, the CS department has left a 
lasting imprint on the College of Information Science 
and Technology (IS&T). The department boasts a culture
of collaboration and an agile approach, which allows 
it to evolve with changing technologies.

## Here are a few things you should know :
* UNO was the first Nebraska university to receive computer science accreditation from the Computing Accreditation Commission of ABET
* Computer Science professionals build tools and software for all kinds of people, from video gamers to scientists to CEOs involved in global business
* For motivated students who wish to gain quicker access to the job market, we offer an integrated undergraduate-graduate program. This intensive program of study allows students to complete a bachelors and masters degree in five years
* We have faculty and students conducting research in software development, language systems, robotics, data mining, high performance computing and other related areas

"""

create_room( 'CS Lab', 'PKI 260', 'Computer Science Lab', long_desc3, 'lab.jpg')
create_room( 'CE Lab', 'PKI 170', 'Engineering Lab', long_desc1, 'lab2.jpg')
long_desc2 = """
We are Architectural Engineering Lab
=================

## What is Architectural Engineering

As an architectural engineer, you will
blend the fundamental principles of
engineering with knowledge of all building
systems, while using new and emerging 
technologies, to plan and design integrated
building systems, such as acoustics, 
communications and controls, electric power, 
lighting, mechanical (heating, ventilation 
and air-conditioning), and structural. 

## At UNO we offer three concentrations:

* Structural Design
* Electrical/Lighting
* Mechanical/Acoustics

"""
create_room( 'AE Lab', 'PKI 270', 'Architectural Engineering Lab', long_desc2, 'lab3.jpg')

create_user('admin', 'admin@example.com', 'password', is_admin=True)
create_user('user', 'user@example.com', 'password', is_admin=False)
create_user('user1', 'user1@example.com', 'password', is_admin=False)
create_user('user2', 'user2@example.com', 'password', is_admin=False)
create_user('user3', 'user3@example.com', 'password', is_admin=False)
create_user('user4', 'user4@example.com', 'password', is_admin=False)
create_user('user5', 'user5@example.com', 'password', is_admin=False)
create_user('user6', 'user6@example.com', 'password', is_admin=False)
create_user('user7', 'user7@example.com', 'password', is_admin=False)

create_userHistory('user1@example.com', 'CS Lab')
create_userHistory('user2@example.com', 'CE Lab')
create_userHistory('user3@example.com', 'AE Lab')
