######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from collections import Counter
from flask.ext.login import current_user
import operator

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = '2003ub313'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'bostonYN@2701'
app.config['MYSQL_DATABASE_DB'] = 'scape'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()
gaid = 0

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			<p> or </p>\
			</br><a href='/register'>sign up</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		gender = request.form.get('gender')
		email=request.form.get('email')
		password=request.form.get('password')
		date_of_birth = request.form.get('date_of_birth')
		hometown = request.form.get('hometown')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print cursor.execute("INSERT INTO Users (first_name, last_name, gender, email, password, date_of_birth, hometown) VALUES ('{0}','{1}', '{2}','{3}','{4}', '{5}','{6}')".format(first_name, last_name, gender, email, password, date_of_birth, hometown))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

def getUsersPhotosFinal(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM photos WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall()

# def getUsersPhotos(uid):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT data, photo_id, caption FROM photos WHERE user_id = '{0}'".format(uid))
# 	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
def getAlbumIdFromUserId(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id  FROM albums WHERE owner_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUsersAlbums(uid):
        cursor = conn.cursor()
        cursor.execute("SELECT album_id, name FROM albums WHERE owner_id = '{0}'".format(uid))
        return cursor.fetchall()

def getfriendlist(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT u.email,u.first_name,u.last_name from users u where u.user_id != '{0}' AND u.user_id IN(select f.friend_id from friends f where f.user_id = '{0}' and f.friend_id = u.user_id)".format(uid))
	return cursor.fetchall()

def getlist(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT u.email,u.first_name,u.last_name,u.user_id from users as u where u.user_id != '{0}' AND u.user_id NOT IN(select f.friend_id from friends f where f.user_id = '{0}' and f.friend_id = u.user_id)".format(uid))
	return cursor.fetchall()


#end login code



@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",albums= getUsersAlbums(uid) )

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		space = ''
		tag = []
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tags')
		#tag = tags.split(' ').strip('#')
		tag = [x.strip('#') for x in tags.split(' ')]
		if space in tag:
			tag.remove('')


		album_id = request.args.get('values')
		gaid = album_id

		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO photos (data, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}' )".format(photo_data, uid, caption,album_id))
		conn.commit()

		cursor = conn.cursor()
		cursor.execute("SELECT photo_id FROM photos WHERE user_id = '{0}' AND caption = '{1}'".format(uid,caption))
		pid = cursor.fetchone()[0]

		for i in tag:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO tags (photo_id,tag_name) VALUES ('{0}','{1}')".format(pid, i))
			conn.commit()

		return render_template('albums.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotosFinal(album_id), album_id=album_id )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		album_id = request.args.get('values')
		gaid = album_id
		return render_template('upload.html', album_id=album_id)
#end photo uploading code 


#default page  
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')

#display album's photos
@app.route('/albums')
@flask_login.login_required
def showPhotos():
	album_id=request.args.get('values')
	return render_template('albums.html', photos=getUsersPhotosFinal(album_id), album_id= album_id)

@app.route('/delete', methods=['POST'])
@flask_login.login_required
def delete_photos():
	album_id =request.args.get('values')
	photo_id = request.args.get('values2')
	cursor = conn.cursor()
	cursor.execute("DELETE FROM photos WHERE album_id = '{0}' AND photo_id = '{1}'".format(album_id,photo_id))
	conn.commit()
	return render_template('albums.html', photos=getUsersPhotosFinal(album_id), album_id= album_id)

@app.route('/add_albums', methods=['POST','GET'])
@flask_login.login_required
def add_album():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		name = request.form.get('album_name')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO albums (name, owner_id) VALUES ('{0}',{1})".format(name,uid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",albums= getUsersAlbums(uid))
	else:
		return render_template('add_albums.html', name=flask_login.current_user.id, message="Please type the album to add!")

@app.route('/delete_album',methods=['POST'])
@flask_login.login_required
def delete_album():
	album_id = request.args.get('values')
	cursor = conn.cursor()
	cursor.execute("DELETE FROM albums WHERE album_id = '{0}' ".format(album_id))
	conn.commit()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",albums= getUsersAlbums(uid))

@app.route("/showuserlist")
@flask_login.login_required
def showuserlist():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('userlist.html', userlist=getlist(uid))

@app.route('/userlist')
@flask_login.login_required
def add_friends():
	uid2= request.args.get('values')
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO friends(user_id,friend_id) Values ('{0}','{1}')".format(uid,uid2))
	conn.commit()
	return render_template('hello.html', message ='Friend Added!')

@app.route("/listfriends")
@flask_login.login_required
def listmyfriends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	print(getfriendlist(uid))
	return render_template('list_friends.html', friendlist=getfriendlist(uid))

@app.route('/search',methods=['GET','POST'])
def search():
	if request.method == 'POST':
		space = ''
		table_rename = []
		search = request.form.get('tsearch')
		tag = [x.strip('#') for x in search.split(' ')]
		if space in tag:
			tag.remove('')
		query_string = 'SELECT p.data, p.photo_id,p.caption FROM photos p WHERE p.photo_id IN( SELECT t1.photo_id FROM '
		count = 1
		for i in range(len(tag)):
			if(i<(len(tag)-1)):
				query_string += ('tags t'+str(count)+', ')
				rename = 't'+str(count)
				table_rename.append(rename)
			else:
				query_string += ('tags t'+str(count)+' ')
				rename = 't'+str(count)
				table_rename.append(rename)
			count+=1
		query_string += 'WHERE '
		# print(query_string)
		# print(table_rename)
		#for j in range(len(tag)-2):
		for k in range(len(tag)-1):
			query_string += table_rename[k]+'.photo_id ='+table_rename[k+1]+'.photo_id AND '
		
		for m in range(len(tag)):
			if(m<(len(tag)-1)):
				query_string += table_rename[m]+'.tag_name = '+ '\"' + tag[m] +'\"'+' AND '
			else:
				query_string += table_rename[m]+'.tag_name = '+ '\"' +tag[m] + '\"' +')'
		
		cursor = conn.cursor()
		cursor.execute(query_string)
		#cursor.fetchall()
		return render_template('search.html', display=cursor.fetchall())
		#for k in range(len())
	else:
		return render_template('search.html')

@app.route('/bytagsgen', methods=['GET'])
def bytagsgen():
	cursor = conn.cursor()
	cursor.execute('SELECT distinct tag_name from tags')
	return render_template('bytags.html', display=cursor.fetchall())

@app.route('/showallphotobytags')
def showallphotobytags():
	tag = request.args.get('values')
	cursor = conn.cursor()
	cursor.execute("SELECT p.data, p.caption, p.photo_id from photos p where p.photo_id IN(select t.photo_id from tags t where t.tag_name = '{0}')".format(tag))
	return render_template('bytags.html', show=cursor.fetchall())	

@app.route('/bytagsmy', methods=['GET'])
@flask_login.login_required
def bytagsmy():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT distinct t.tag_name from tags t where t.photo_id IN (select p.photo_id from photos p where p.photo_id = t.photo_id and p.user_id ='{0}')".format(uid))
	return render_template('bytags.html', displaymy=cursor.fetchall())

@app.route('/showmyphotobytags')
@flask_login.login_required
def showmyphotobytags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	tag = request.args.get('values')
	cursor = conn.cursor()
	cursor.execute("SELECT p.data, p.caption, p.photo_id from photos p where p.photo_id IN(select t.photo_id from tags t where t.tag_name = '{0}') and p.user_id='{1}'".format(tag,uid))
	return render_template('bytags.html', showmy=cursor.fetchall())

@app.route('/bypopulartags', methods=['GET'])
def bypopulartags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag_name, count(tag_name) from tags group by tag_name order by count(tag_name) desc limit 10")
	return render_template('bytags.html', display=cursor.fetchall())

@app.route('/addcomment',methods=['POST'])
def addcomment():
	if current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
	else:
		uid = None
	photo_id = int(request.args.get('values2'))
	comment = request.form.get('comment')
	cursor = conn.cursor()
	cursor.execute("SELECT p.photo_id from photos p where p.user_id = '{0}'".format(uid))
	current_user_pid = cursor.fetchall()
	pid = []
	for i in current_user_pid:
		pid.append(i[0])
	if photo_id in pid:
		return render_template('error.html', message="You cannot comment on your photo!")

	if(uid != None):
		cursor = conn.cursor()
		cursor.execute("INSERT INTO comments(owner_id,text,photo_id) VALUES ('{0}','{1}','{2}')".format(uid,comment, photo_id))
		conn.commit()
	else:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO comments (text, photo_id) VALUES ('{0}',{1})".format(comment, photo_id))
		conn.commit()
	return render_template('hello.html', message="Comment Added!")

@app.route('/showcomments',methods=['POST'])
def showcomments():
	photo_id = request.args.get('values2')
	cursor = conn.cursor()
	cursor.execute("SELECT c.text,c.comment_date,u.first_name,u.last_name from comments c, users u where c.owner_id = u.user_id and c.photo_id='{0}'".format(photo_id))
	reg_user = cursor.fetchall()
	cursor = conn.cursor()
	cursor.execute("SELECT c.text, c.comment_date from comments c where c.photo_id='{0}' AND c.owner_id IS NULL".format(photo_id))
	anonymous = cursor.fetchall()
	return render_template('comments.html', message="Here are the comments of the selected photo!", display=reg_user, anon =anonymous)

@app.route('/tagrecommendation', methods=['POST'])
def tagrecommendation():
	tags_input = request.form.get('tsuggestions')
	tag = [x.strip('#') for x in tags_input.split(' ')]
	cursor = conn.cursor()
	cursor.execute("SELECT t.photo_id from tags t where t.tag_name ='{0}' or t.tag_name = '{1}' ".format(tag[0],tag[1]))
	photo_id = cursor.fetchall()
	suggest = []
	for i in photo_id:
		cursor = conn.cursor()
		cursor.execute("SELECT t.tag_name from tags t where t.photo_id ='{0}' ".format(i[0]))
		toappend = cursor.fetchall()
		for j in toappend:
			if j[0] in tag:
				continue
			else:
				suggest.append(j[0])
	counts = Counter(suggest)
	suggestions = sorted(set(suggest), key=counts.get, reverse=True)
	suggestions = suggestions[0:5]
	return render_template('suggestions.html', suggestions=suggestions)

@app.route('/showall')
def showall():
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name from albums")
	return render_template('showall.html', albums=cursor.fetchall())

@app.route('/showallphotos')
def showallPhotos():
	album_id=request.args.get('values')
	return render_template('showall.html', photos=getUsersPhotosFinal(album_id), album_id= album_id)

@app.route('/top10users')
def showtop10users():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, first_name, last_name, email from users")
	top10users = cursor.fetchall()
	print(top10users)
	user_activity = {}
	for i in top10users:
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) from photos where user_id = {0}".format(i[0]))
		photo_count = cursor.fetchall()[0]
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) from comments where owner_id = {0}".format(i[0]))
		comment_count = cursor.fetchall()[0]
		#print(comment_count[0],photo_count[0])
		rank_count = int(comment_count[0]) + int(photo_count[0])
		user_activity[str(i[1]+" "+i[2]+" "+i[3])] =rank_count
	user_activity = sorted(user_activity.items(), key=operator.itemgetter(1) ,reverse=True)
	user_activity = user_activity[0:11]
	return render_template('top10users.html', user_activity=user_activity)

@app.route('/youmaylike')
@flask_login.login_required
def youmaylike():
	final_display = ()
	uid= getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT t.tag_name from tags t, photos p where t.photo_id = p.photo_id AND p.user_id = '{0}' group by t.tag_name order by count(t.tag_name) desc limit 5".format(uid))	
	top5_tags = cursor.fetchall()
	print(top5_tags)
	
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id from photos where user_id <> '{0}' ".format(uid))
	all_pid = cursor.fetchall()
	print(all_pid)


	recommended_pid = {}
	for i in all_pid:
		for j in top5_tags:
			cursor = conn.cursor()
			cursor.execute("SELECT p.photo_id from photos p, tags t where t.photo_id = p.photo_id and t.tag_name ='{0}' and t.photo_id = '{1}' ".format(j[0],i[0]))
			match = cursor.fetchall()
			if match:
				if i[0] not in recommended_pid:
					recommended_pid[i[0]] = 1
				else:
					recommended_pid[i[0]] += 1
	#print(recommended_pid)
	sorted_reco = sorted(recommended_pid.items(), key=operator.itemgetter(1), reverse = True)
	#print(sorted_reco)
	t_count = []
	for k1,v1 in sorted_reco:
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) from tags where photo_id = {0}".format(k1))
		t_count.append(cursor.fetchall()[0][0])
	print(t_count)

	for k ,v in sorted_reco:
		cursor=conn.cursor()
		cursor.execute("SELECT p.data, p.caption,p.photo_id from photos p where p.photo_id='{0}' ".format(k))
		final_display += cursor.fetchall()
	return render_template('youmayalsolike.html', display=final_display)





@app.route('/likephoto',methods=['POST'])
@flask_login.login_required
def likephoto():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_id = request.args.get('values')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO likes(user_id,photo_id) VALUES ('{0}','{1}')".format(uid,photo_id))
	conn.commit()
	return render_template('hello.html', message="Like Added!")

@app.route('/showuserslikes', methods=['POST'])
def showuserslikes():
	photo_id = request.args.get('values')
	cursor = conn.cursor()
	cursor.execute("SELECT u.first_name,u.last_name from  likes l, users u where l.user_id = u.user_id and l.photo_id='{0}'".format(photo_id))
	reg_user = cursor.fetchall()
	cursor = conn.cursor()
	cursor.execute("SELECT count(*) from likes l where l.photo_id='{0}' AND l.user_id = 0".format(photo_id))
	anonymous = cursor.fetchall()
	cursor = conn.cursor()
	cursor.execute("SELECT count(*) from likes l where l.photo_id='{0}'".format(photo_id))
	total_likes = cursor.fetchall()
	return render_template('likes.html', message="Here are the users who liked the selected photo!", display=reg_user, anon =anonymous, total =total_likes)



if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
