from flask import Flask, jsonify
from flask import request
from py2neo import Graph, Node, Relationship,cypher

app = Flask(__name__)

graph = Graph("http://localhost:7474/db/data/")

#Create user 
@app.route('/adduser', methods=['POST'])  #successs
def adduser():
    print(request.is_json)
    content = request.get_json()
    print(content)

    query=""" 
    WITH {jsonobj} as value
    create(U:User{FirstName:value.FirstName,LastName:value.LastName,EmailAddress:value.EmailAddress,Password:value.Password,UserId:value.UserId,UserType:value.UserType})
    """
    graph.cypher.execute(query,jsonobj=content)
    
    return "User added successfully"

#Get user  details
@app.route('/getuser', methods=['GET'])
def getuser():
    ID=request.args['UserId']
    print(ID)
    query = '''
         match(u:User)  
         where u.UserId=toInt({ID})
         RETURN (apoc.map.merge(u,{}))  as user
        '''
    result = []
    for res in graph.cypher.execute(query, ID=ID):
        result.append(str(res[0]))

    return jsonify(result)

#Edit User details
@app.route('/edituser', methods=['POST']) 
def edituser():
    id=request.args['UserId']
    # print(request.is_json)
    content = request.get_json()
    print(content)
    print(id)
    query=""" 
    WITH {jsonobj} as value
    match(u:User) 
    where u.UserId=toInt({ID})
    SET u.FirstName=value.FirstName,u.LastName=value.LastName,u.EmailAddress=value.EmailAddress,u.Password=value.Password,u.UserId=value.UserId,u.UserType=value.UserType
    """
    graph.cypher.execute(query,jsonobj=content,ID=id)
    return "User details edited successfully"

#Delete user 
@app.route('/deleteuser', methods=['GET'])
def deleteuser():
    id=request.args['UserId']
    print(id)
    query=""" 
    match(u:User)  
    where u.UserId=toInt({ID})
    detach delete u 
    """
    graph.cypher.execute(query,ID=id)
    return "User deleted Successfully"

#Get all users based on User type
@app.route('/getallusers', methods=['GET'])
def getallusers():
    ID=request.args['UserType']
    query = '''
         match(u:User)  
         where u.UserType={ID}
         RETURN u 
        '''
    
    result = []
    for res in graph.cypher.execute(query, ID=ID):
        result.append(str(res[0]))

    return jsonify(result) 

#Change Password
@app.route('/change_pass', methods=['POST'])
def change_pass():
    id=request.args['UserId']
    print(request.is_json)
    content = request.get_json()
    print(content)
    query='''
    WITH {jsonobj} as value
    match(u:User)
    where u.UserId=toInt({ID}) and u.EmailAddress=value.EmailAddress and u.Password=value.oldPassword
    set u.Password=value.newPassword
    return u
    '''
    graph.cypher.execute(query,jsonobj=content,ID=id)
    return "Password changed successfully"

app.run(host='0.0.0.0', port=5000)

