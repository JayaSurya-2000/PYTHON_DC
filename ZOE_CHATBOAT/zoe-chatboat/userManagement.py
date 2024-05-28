from .main import app, auth, execute_db_query
from flask import request
from passlib.apps import custom_app_context
import simplejson
import json

@app.route('/add-user', methods=['POST'])
@auth.login_required(role=['admin'])
def addUser():
    """Adds a new user to access the api. Only users with 'admin' role can execute this.
    Only admin can execute this."""

    if not request.data:
        return "[ERROR]: Request should contain data which is used as input.", 400
    else:
        reqJ = json.loads(request.data)
    mandatory_list = ['username', 'password', 'email', 'fullName']
    for item in mandatory_list:
        itemValue = reqJ[item]
        if itemValue is None or itemValue == '':
            return f"[Error]: {item} cannot be none or empty({itemValue})", 400

    username = reqJ['username']
    password = reqJ['password']
    email = reqJ['email']
    fullName = reqJ['fullName']
    role = reqJ.get('role', '')
    group = reqJ.get('group', '')
    password_hash = custom_app_context.encrypt(password)
    usersWithUsername = execute_db_query(f"SELECT USER_ID FROM DCHUB.BI.MP_SPARK_API_USERS WHERE USER_NAME = '{username}'")
    if len(usersWithUsername) > 0:
        return "[ERROR]: User with username already exists! Choose a different username", 409
    execute_db_query(
        f"INSERT INTO DCHUB.BI.MP_SPARK_API_USERS(USER_NAME, PASSWORD, FULL_NAME, EMAIL, ROLE, USER_GROUP) "
        f"VALUES('{username}', '{password_hash}', '{fullName}', '{email}', '{role}', '{group}')")
    return "User created"

@app.route('/fetch-users', methods=['GET', 'POST'])
@auth.login_required(role=['admin'])
def fetchUsers():
    """Fetch the list of existing users. Only users with 'admin' role can execute this.
    Only admin can execute this."""

    query = "SELECT USER_ID, USER_NAME, FULL_NAME, EMAIL, ROLE, USER_GROUP FROM DCHUB.BI.MP_SPARK_API_USERS WHERE USER_ID > 0 "
    reqJ = {}
    if request.get_data(): reqJ = json.loads(request.get_data())
    if reqJ.get('username', None): query = query + f" AND USER_NAME = '{reqJ['username']}' "
    if reqJ.get('email', None): query = query + f" AND EMAIL = '{reqJ['email']}' "
    if reqJ.get('fullName', None): query = query + f" AND FULL_NAME = '{reqJ['fullName']}' "

    qRes = execute_db_query(query)
    finalResult = []
    for rec in qRes:
        entry = {}
        for key in rec.keys():
            entry[key] = rec[key]
        finalResult.append(entry)
    return simplejson.dumps(finalResult)

@app.route('/update-user', methods=['POST'])
@auth.login_required(role=['admin'])
def updateUser():
    """Update existing user with the given details.
    Only admin can execute this.
    Username is the key here and the entry with the given username as username will be updated with the details.
    Note that if the username doesn't exists nothing gets updated, but will be give positive response. This will be changed soon."""

    if not request.data:
        return "[ERROR]: Request should contain data which is used as input", 400
    else:
        reqJ = json.loads(request.data)
    mandatory_list = ['username', 'email', 'fullName', 'role', 'group']
    for item in mandatory_list:
        itemValue = reqJ[item]
        if itemValue is None:
            return f"Error: {item} cannot be none.", 400

    username = reqJ['username']
    email = reqJ['email']
    fullName = reqJ['fullName']
    role = reqJ['role']
    group = reqJ['group']

    #TODO: Check if the user exists, and if not, through and error and return appropriate http status code and message.
    query = f"UPDATE DCHUB.BI.MP_SPARK_API_USERS " \
                f"SET FULL_NAME = '{fullName}', EMAIL = '{email}', ROLE = '{role}', USER_GROUP = '{group}' " \
            f"WHERE USER_NAME = '{username}'"
    execute_db_query(query)
    return "User updated"

@app.route('/delete-user', methods=['DELETE'])
@auth.login_required(role=['admin'])
def deleteUser():
    """
    Deletes the user entry with the given user name.
    Only admin can execute this.
    Note that one cannot delete oneself. This logic is implemented to make atleast one admin user stay in the database to acces teh api
    """
    if not request.data:
        return "[ERROR]: Request should contain data which is used as input", 400
    else:
        reqJ = json.loads(request.data)
    mandatory_list = ['username']
    for item in mandatory_list:
        itemValue = reqJ[item]
        if itemValue is None:
            return f"Error: {item} cannot be none.", 400

    currentUser = auth.current_user()
    userToBeDeleted = reqJ['username']
    if currentUser == userToBeDeleted:
        return "[ERROR]: Cannot delete self!", 406
    else:
        query = f"DELETE FROM DCHUB.BI.MP_SPARK_API_USERS WHERE USER_NAME = '{reqJ['username']}'"
        execute_db_query(query)
        return f"User '{reqJ['username']}' is deleted!"

