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

long_desc4 = """
We are the C-MANTIC Robotics Lab
=================

## What the C-MANTIC Robotics Lab researches

The main research topics in the lab are autonomous, adaptive, multi-agent/multi-robot systems, multi-robot motion and path planning, multi-robot task planning/allocation, game theory and computational economics and swarm robotics. Some of the research problems we have worked on include distributed robotic terrain or area coverage, multi-robot task allocation, multi-robot formation control, algorithms for dynamic reconfiguration of modular robots, distributed information aggregation using prediction markets, etc.
The laboratory features state-of-the-art equipment for conducting research in robotics and multi-agent systems. We have all-terrain Coroware Explorer and AscTec Pelican robots, several robots that can be used within the laboratory for conducting experiments such as TurtleBot, Corobot, Khepera II and e-puck, and several licenses of the commercial robot simulator Webots.

## What tools are available

The laboratory features state-of-the-art equipment for conducting research in robotics and multi-agent systems. We have all-terrain Coroware Explorer and AscTec Pelican robots, several robots that can be used within the laboratory for conducting experiments such as TurtleBot, Corobot, Khepera II and e-puck, and several licenses of the commercial robot simulator Webots.

"""
create_room( 'C-MANTIC Lab', 'PKI 369', 'C-MANTIC Robotics Lab', long_desc4, 'lab4.jpg')

long_desc5 = """
We are the Widgets Rule club
=================

## What the Widgets Rule club researches

We research widges of all kinds! Small ones, big ones, and ones that your momma eats for breakfast

## What our favorite widgets are

Our favorite kind of widgets include chocolate, basketball, and linoleum. These widgets zap packets faster than brown bagged semicolons.
We would love for you to join our widget zapping club!

"""
create_room( 'Widgets club', 'PKI 200', 'Widgets Rule Lab', long_desc5, 'lab4.jpg')

long_desc6 = """
We are the PKI Robotics Lab
=================

## Where the RC^2 Robotics Lab meets

We meet in the RC^2 Robotics Lab (PKI313), which is on the third floor of the Peter Kiewit Institute (1110 S 67th St, Omaha, NE 68182).

## What PKI Robotics does

Our robotics club is interested in providing students with experiences and opportunities that enhance their understanding of and skill set in robotics through participating in fun, yet challenging, robotics competitions.

This year, we are focusing on the CREATE Open challenge. The 2014 CREATE Open game is similar to VEX Skyrise, but includes some differences in rules, including the allowance of non-VEX building materials and control systems in the robot.

"""
create_room( 'PKI Lab', 'PKI 313', 'PKI Robotics Lab', long_desc6, 'lab2.jpg')

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
