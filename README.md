# Scape---Photo-Sharing-Website

The project uses Flask which is a micro web framework written in Python along with MySQL and Python to implement a photo sharing website. The functionalities are quite similar to Flickr! 


Description of use-cases:
A user can have multiple friends and it is stored in the database as a self-relation to the users. A user can post comments on photos. Each comment must be posted by a user and associated with a single user, however a user can post multiple comments. Each Comment is associated with exactly one photo. A photo can have multiple comments. A photo has total participation in relationship with the users. Photos have a weak entity called tags which contain the names of all the tags associated with that photo. Two photos can have the same tag.  A photo is always contained in an album. An album can have multiple photos. Similarly, A user can have multiple albums but an album must be associated to one or more users. 

Relational Schema:

Users :
user_id	first_name	last_name	gender	email 	password	date_of_birth	hometown

Albums :
album_id	name	date_of_creation	owner(user)_id

Photos :
photo_id	no_of_likes	data	caption	user_id	date	album_id

Comments :
comment_id	comment_date	text	photo_id	owner_id

Friends_with :
friend(user)_id	user_id

Tags :
tag_name	photo_id


Likes :
user_id	photo_id




SQL Queries:

CREATE TABLE Users
( user_id INTEGER NOT NULL AUTO_INCREMENT,
first_name CHAR(30) NOT NULL,
last_name CHAR(30),
email CHAR(30),
password CHAR(32) NOT NULL,
date_of_birth DATE,
hometown CHAR(20),
gender VARCHAR(10),
PRIMARY KEY(user_id));

CREATE TABLE Albums
(album_id INTEGER NOT NULL AUTO_INCREMENT,
name CHAR(30),
date_of_creation DATETIME default CURRENT_TIMESTAMP,
owner_id INTEGER NOT NULL,
PRIMARY KEY (album_id),
FOREIGN KEY(owner_id) REFERENCES Users(user_id) ON DELETE CASCADE);

CREATE TABLE Photos
(photo_id INTEGER NOT NULL AUTO_INCREMENT,
data LONGBLOB,
caption VARCHAR(255),
user_id INTEGER NOT NULL,
date DATETIME default CURRENT_TIMESTAMP,
album_id INTEGER NOT NULL,
PRIMARY KEY (photo_id),
FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
FOREIGN KEY(album_id) REFERENCES Albums(album_id) ON DELETE CASCADE);

CREATE TABLE Comments
(comment_id INTEGER NOT NULL AUTO_INCREMENT,
comment_date DATETIME default CURRENT_TIMESTAMP,
text TEXT,
photo_id INTEGER NOT NULL,
owner_id INTEGER NOT NULL,
PRIMARY KEY(comment_id),
FOREIGN KEY(owner_id) REFERENCES Users(user_id),
FOREIGN KEY(photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE);

Additional Assumptions:
The name of the site is assumed as Scape! A user can like a photo only once.


CREATE TABLE Friends
(friend_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
PRIMARY KEY(friend_id, user_id),	
FOREIGN KEY(friend_id) REFERENCES Users(user_id),
FOREIGN KEY(user_id) REFERENCES Users(user_id)); 

CREATE TABLE Tags
(tag_name VARCHAR(255),
photo_id INTEGER NOT NULL,
PRIMARY KEY(tag_name, photo_id),
 FOREIGN KEY(photo_id) REFERENCES Photos(photo_id) 
ON DELETE CASCADE);

CREATE TABLE Likes
(user_id INTEGER,
photo_id INTEGER NOT NULL,
PRIMARY KEY(user_id, photo_id),
 FOREIGN KEY(user_id) REFERENCES Users(user_id),
FOREIGN KEY(photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE);
