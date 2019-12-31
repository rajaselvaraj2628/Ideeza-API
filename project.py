from flask import Flask, jsonify
from flask import request
from py2neo import Graph, Node, Relationship,cypher

app = Flask(__name__)

graph = Graph("http://localhost:7474/db/data/")

#create project and assign it to the users
@app.route('/createproj', methods=['POST']) 
def createproj():
    print(request.is_json)
    content = request.get_json()
    print(content)
    id=request.args['UserId']
    query=""" 
    WITH {jsonobj} as value
    match(u:User)
    where u.UserId=toInt({ID})
    create(p:project{UserId:value.UserId,EmailAddress:value.EmailAddress,ProjectName:value.ProjectName,Description:value.Description,Duration:value.Duration,Status:value.Status,Members:value.Members})
    create(u)-[r:upload]->(p)
    """
    graph.run(query,jsonobj=content,ID=id)
    return jsonify(content)

#Edit project details
@app.route('/Editproj', methods=['POST'])
def Editproj():
    id=request.args['UserId']
    project_name = request.args['ProjectName']
    content = request.get_json()
    print(content)
    print(id)
    query=""" 
    WITH {jsonobj} as value
    match(p:project) 
    where p.UserId=toInt({ID}) and p.ProjectName={ProjectNM}
    SET p.UserId=value.UserId,p.EmailAddress=value.EmailAddress,p.ProjectName=value.ProjectName,p.Description=value.Description,p.Duration=value.Duration,p.Status=value.Status,p.Members=value.Members
    """
    graph.run(query,jsonobj=content,ID=id,ProjectNM=project_name)
    return "successful"

#Delete Project details and relationship 
@app.route('/deleteproj', methods=['GET']) 
def deleteproj():
    ProjectName=request.args['ProjectName']
    UserId=request.args['UserId']
    query=""" 
    match(p:project)  
    where p.ProjectName={ProjectName} and p.UserId=toInt({UserId})
    detach delete p
    """
    graph.run(query,ProjectName=ProjectName,UserId=UserId)
    return "Project deleted Successfully"

#Get project details
@app.route('/getproject', methods=['GET'])
def getproject():
    ID=request.args['UserId']
    project=request.args['ProjectName']
    query = '''
         match(p:project)  
         where p.UserId=toInt({ID}) and p.ProjectName={ProjectNm}
         RETURN p 
        '''
    result = []
    for res in graph.run(query, ID=ID,ProjectNm=project):
        result.append(str(res[0]))


    return jsonify(result) 

#Get all project details
@app.route('/getallprojects', methods=['GET'])
def getallprojects():
    ID=request.args['UserId']
    query = '''
         match(p:project)  
         where p.UserId=toInt({ID})
         RETURN p
        '''
    result = []
    for res in graph.run(query, ID=ID):
        result.append(str(res[0]))

    return jsonify(result) 

#Search Projects based on filter condition
@app.route('/searchprojects', methods=['GET']) 
def searchprojects():
    Status=request.args['Status']
    
    query=""" 
    match(p:project) where p.Status={Status} RETURN p
    """
    result = []
    for res in graph.cypher.execute(query, Status=Status):
        result.append(str(res[0]))
    return jsonify(result) 

#User assigns Technician to the project based on the user type
@app.route('/assigntech',methods=['POST'])
def assigntech():
    print(request.is_json)
    content = request.get_json()
    print(content)

    type = request.args['UserType']
    Status=request.args['Status']
    assign_tech="""
    WITH {jsonobj} as value
    
    match(u:User),(p:project)
    where u.UserType={type} and p.Status={Status}
    create(p)-[r:assigned_to]->(u)
    """

    graph.cypher.execute(assign_tech,jsonobj=content,type=type,Status=Status)
    #return jsonify(content)
    return "Technician Assigned Sucessfully"

app.run(host='127.0.0.1', port=5000)
