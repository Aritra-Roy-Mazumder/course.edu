# Main components
This progject can be broken down into python code for the flask application, a sqlite3 database named "course.db", a set of HTML templates and css files.


# Basic Functionality
The first step was to allow users to create accounts and log in. To that end, I created the users table in my database(Discussed in greater detail below),
and used Session from flask_session to keep track of whos logged in. For new users, there is a registration page that quaries in the new user into the users
database. The login page takes credentials and quaries the database to see if the username password combos are valid. If they are, it logs the user in by
adding their id to the session. If the user wishes to log out, the flask script simply removes the user's id from the session.


# Database Design
The program has a database titled "course.db" containing 5 data tables.
1) users: The users database stores information of each user with columns for an unique user id, username, and password.
2) courses: This stores information on unique courses with columns for a unique course id, title of class, teacher's id, and rating.
            # Note: The unique ids for each of the course is based on a combination of the room number and block of that particular class.
            I made this design decision because I wanted a way to alwaus know what a particular class's ID is, and at the same time store
            as much information about the class in the ID itself.
3) course_relations: This stores information mapping each user to several courses that they are taking. Columns are an id, the user_id of
                    the user taking the course, and the course id of the course from the courses data table. I made this to map a many to
                    many relation between the users and the courses
4) friend relations: This stores information mapping "friend" relations between different users. It stores an id, the user_id of the first
                        friend, and that of the second friend. For ease of coding some functions discussed later, each "friendship" is entered
                        twice with first friend and second friend's places swapped.
5) friend_requests: This maps friend quests sent from one person to another. It stores an id for the friend request, id of the person who sent
            it, and the id of the person to recieve it

# Storing Courses

1) Adding courses: In order to add courses an user is taking, they may go to the add page by clicking on the add courses button on their homepage.
Upon doing so, they can enter the room number, a custom title, and block/period for the class. The room number and block is used
to generate the id that the course is supposed to have. Furthermore, if the course isn't uniquely identified in the courses table,
the new course is added. The relationship between the user and that course is mapped by an entry to the course relations database.



# Interpersonal Functionality
1) Search: The users can search user in the search bar once they are loged in. The user may enter a search term and the database will
be quaried for users with similar usernames and a table of users will be returned along with a button allowing us to visit their profiles.

2) Friends: The idea of two users being "friends" is that they will have access to each other's course information. If an user visits the
profile of another user, they are either friends, in which case the user an see the person's courses and has the option to remove them as a friend.
Otherwise, if they are not friends, the user has the option to send a friend request, and cancel the friend request if the user wants to.
If the user has recieved a friend request from the person, the user can accept that request.

To manipulate how the profile page appears depending on what relationships exists between the two users, I mapped each scinario to a friend relation id.
For instance 0 = user's own profile, 1 = not friends, can send request, 2 = has sent request, can cancel request, 3 Friends, can see courses, can remove friend
4 = has recieved friend request from, can accept friend. Then, there friend case codes are passed down to the html template of the profile page,
and the correct version of the profile page is generated.

# Information Access

There are a few "information access" pages. For instance, the friends page that quaries the user's friends and presents them in a table along with
buttons to visit their profile. The friend requests page that gets all of the user's recieved friend requests and displays them, along with a
button to visit the profiles of the people, and a button to accept the requests directly. Finally, the with whom page shows whom the user has a class
with by quarying the intersection between the users, course_relations, and friend_relations tables.

