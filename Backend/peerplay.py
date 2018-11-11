from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from urllib.parse import urlparse
import json
import datetime
import random

states = {"Pending":0, 
          "Connected":1,
         }

curdir = "./"
print(curdir)
sep = '/'

key_pair = {}

def split_query(query):
    value_pairs = {}
    splited = query.split("&")
    for item in splited:
        [key, value] = item.split("=")
        value_pairs[key] = value
    return value_pairs

def construct_and_store_new_id():
    id = int(random.random()*10000000)
    while id in key_pair:
        id = int(random.random()*10000000)
    key_pair[id] = {"state": states["Pending"]}
    response_map = {"id" : id}
    return response_map

def construct_pair_peer(query):
    queries = split_query(query)
    response_map = {}
    if int(queries["myid"]) in key_pair and int(queries["peerid"]) in key_pair:
        key_pair[int(queries["myid"])]["state"] = states["Connected"]
        key_pair[int(queries["peerid"])]["state"] = states["Connected"]
        key_pair[int(queries["myid"])]["peer"] = int(queries["peerid"])
        key_pair[int(queries["peerid"])]["peer"] = int(queries["myid"])
        response_map["status"] = "ok"
    else:
        response_map["status"] = "invalid id"
    return response_map

def construct_and_store_play_state_change(query):
    queries = split_query(query)
    response_map = {}
    if int(queries["myid"]) in key_pair and int(queries["peerid"]) in key_pair:
        print(queries["state"])
        if queries["state"] == "play":
            #key_pair[int(queries["myid"])]["seconds"] = float(queries["time"])
            key_pair[int(queries["peerid"])]["seconds"] = float(queries["time"])
            key_pair[int(queries["peerid"])]["updated"] = True
        else:
            key_pair[int(queries["peerid"])]["seconds"] = -1
            key_pair[int(queries["peerid"])]["updated"] = True
        response_map["status"] = "ok"
    else:
        response_map["status"] = "invalid id"
    return response_map

def construct_pulse_state(query):
    queries = split_query(query)
    response_map = {}
    if int(queries["myid"]) in key_pair:
        if  "updated" in key_pair[int(queries["myid"])] and key_pair[int(queries["myid"])]["updated"]:
            response_map["seconds"] = key_pair[int(queries["myid"])]["seconds"]
            key_pair[int(queries["myid"])]["updated"] = False
            response_map["updated"] = "true"
        else:
            response_map["updated"] = "false"
        response_map["status"] = "ok"
    else:
        response_map["status"] = "invalid id"
        response_map["updated"] = "false"
    return response_map


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        #sendReply = False
        querypath = urlparse(self.path)
        getpath, query = querypath.path, querypath.query
        print(querypath)
        #print(filepath)
        #print(query)
        json_r = {}
        if "getid" in getpath:
            json_r = construct_and_store_new_id()
        elif "pairpeer" in getpath:
            json_r = construct_pair_peer(query)
        elif "playstate" in getpath:
            json_r = construct_and_store_play_state_change(query)
        elif "pulse" in getpath:
            json_r = construct_pulse_state(query)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(json_r), 'utf-8'))
        print("sent" + json.dumps(json_r))
        '''
        if filepath.endswith('/'):
            filepath += 'index.html'
        filename, fileext = path.splitext(filepath)
        for e in mimedic:
            if e[0] == fileext:
                mimetype = e[1]
                sendReply = True

        if sendReply == True:
            try:
                with open(path.realpath(curdir + sep + filepath),'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type',mimetype)
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)
        '''
        
def run():
    port = 81
    print('starting server, port', port)

    # Server settings
    server_address = ('', port)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

#if __name__ == '__main__':
run()