import zmq
from time import sleep
import sqlite3 as lite
import threading 
###############################
con = lite.connect('user.db')
cur = con.cursor()
#################################cleint

port_c = "5556"
context_c = zmq.Context()
socket_c = context_c.socket(zmq.REP) 
socket_c.bind("tcp://*:%s" % port_c)

####################################master
port_m = "3333"
context_m = zmq.Context()
socket_m = context_m.socket(zmq.REQ) 
socket_m.connect("tcp://localhost:%s" % port_m)
##################################FLAG -shared between threads
flag=False
message =''
#####################################blocks on master and executes query from master or replys with ready
def masterThread():
    con = lite.connect('user.db')
    cur = con.cursor()
    while(1):		  
        socket_m.send_string('9') 
        sleep(1)
        queryArr=socket_m.recv_pyobj()
        if (len(queryArr) >1):
            flag =True
            for query in queryArr:
                cur.execute(query)
                con.commit()
            flag =False   
        else: 
            if (queryArr[0] == '9'):
                print('received ready')
              
            else:
                cur.execute(queryArr[0])
                print('received query')
                con.commit()
                
                
              
				  
############################################################ blocks on client and waits for flag before executing        
def clientThread():
    con = lite.connect('user.db')
    cur = con.cursor()
    sleep(3)
    while(1):
        data = socket_c.recv_pyobj()
        while (flag):
            continue
        name = data[0]
        password = data[3]
        query = "select * from user where name ="+ "\""+name+"\""
        cur.execute (query)
        check = cur.fetchall()
        
        if (len(check) ==0):
            reply = 'user doesnt exist'
        else :
            if (check[0][3] == password):
                reply = 'sign in successfully!!'
            else:
                reply = 'incorrect passsowrd'    
		#socket_c.send_string("sign up successfully")
        print (data)
        socket_c.send_string(reply)
##########################################################
c1=threading.Thread(target = masterThread )
c2=threading.Thread(target = clientThread )

c1.start()
c2.start()


c1.join()
c2.join()           
                     