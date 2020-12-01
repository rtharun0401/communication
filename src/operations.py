import json
import enum
from flask import abort,current_app,jsonify
import re


class deviceType(enum.Enum):
    COMPUTER = 1
    REPEATER = 2


class Operations:
    def __get_type(self,body):
        """[This method is get device type from the body]

        Args:
            body ([dict]): [The dictonary containing device type]

        Returns:
            [string]: [type of the device]
        """        
        if "type" in body:
            if body["type"] == deviceType.COMPUTER.name or body["type"] == deviceType.REPEATER.name:
                return body["type"]
        return ""
    def create_device(self,content_type,command_body):
        """[This method is used to create device]

        Args:
            content_type ([string]): [Contains content type header]
            command_body ([string]): [the string containing command body]

        Returns:
            [response]: [response code and description]
        """        
        if content_type == ' application/json':
            body = json.loads(command_body)
            if "name" in body:
                body_type = self.__get_type(body)
                if body_type:
                    if body["name"] not in current_app.config["data"]:
                        if body_type == deviceType.COMPUTER.name:
                            current_app.config['data'][body["name"]] = {"type":body["type"],"connections":[],"strength":5}
                            current_app.config["connections"][body["name"]] = []
                        else:
                            current_app.config['data'][body["name"]] = {"type":body["type"],"connections":[]}
                        return jsonify({"msg":"Sucessfully added %s"% body["name"]}),200
                    else:
                        abort(400,"Device already exists")
                
        abort(500)
   

    def connect_devices(self,content_type,command_body):
        """[This method is used to connect devices]

        Args:
            content_type ([string]): [Contains content type header]
            command_body ([string]): [the string containing command body]

        Returns:
            [response]: [response code and description]
        """        
        if content_type == ' application/json':
            body = json.loads(command_body)
            if "source" in body and "targets" in body:
                if body["source"] in current_app.config["data"]:
                    if body["targets"]:
                        for device in body["targets"]:
                            if body["source"] != device:
                                if device in current_app.config["data"]:
                                    current_app.config["data"][body["source"]]["connections"].append(device)

                        current_app.config["connections"][body["source"]] = current_app.config["data"][body["source"]]["connections"]        
                        return jsonify({"msg":"Successfully connected"}),200

                    else:
                        return jsonify({"msg":"no targets to create connection"}),200
                
                else:
                    abort(400,"Node %s not found"% body["source"])
            else:
                abort(400,"Invalid command syntax")

        abort(500)


    def fetch_devices(self):
        """[This method is used to fetch devices]

        Returns:
            [response]: [response code and description]
        """        
        devices = []
        for key in current_app.config["data"]:
            element = {'type':current_app.config["data"][key]["type"],'name':key}
            devices.append(element)
        
        if devices:
            return jsonify({"devices":devices}),200
        else:
            return jsonify({"msg":"No devices to fetch"}),200

            

    def change_device_strength(self,content_type,command_body,command):
        """[This method is modify the device strength]

        Args:
            content_type ([string]): [Contains content type header]
            command_body ([string]): [the string containing command body]
            command ([string]): [The string contains device details]

        Returns:
            [response]: [response code and description]
        """        
        device_name = command.split("/")[-2]
        if content_type == ' application/json':
            body = json.loads(command_body)
            if "value" in body:
                if type(body["value"]) == int:
                    if device_name in current_app.config["data"] and current_app.config["data"][device_name]["type"] == deviceType.COMPUTER.name:
                        current_app.config["data"][device_name]["strength"] == body["value"]
                        return jsonify({"msg":"Successfully defined strength"}),200

                    else:
                        abort(404,"Device not found")
                else:
                    abort(400,"value must be integer")
            else:
                abort(400,"value must be present")

    def find_path(self,connections,source,destination,path=[]):
        """[THis method is used to find path between source and destination]

        Args:
            connections ([list]): [The alist containing all connections]
            source ([string]): [The source device]
            destination ([destination]): [The destination device]
            path (list, optional): [The path from the function]. Defaults to [].

        Returns:
            [string]: [The path between source and destination]
        """        
        path = path + [source]
        print("destination is",destination)
        print("path is "+str(path))
        if source == destination:
            return path
        for node in connections[source]:
            if node not in path:
                newpath = self.find_path(connections,node,destination,path)
                if newpath:
                    return newpath

    def find_routes(self,source,destination):
        """[This method is used to find routes and format the path and return the response]

        Args:
            source ([string]): [The source device]
            destination ([string]): [The destination device]

        Returns:
            [response]: [response code and description]
        """        
        final_path = ""
        path = self.find_path(current_app.config["connections"],source,destination)
        print(path)
        if len(path) == 0:
             abort(404,"No Route found")
        elif len(path) == 1:
            print("soure is ",source)
            print("destination is ",destination)
            return jsonify({"msg":"Route is {}->{}".format(source,destination)}),200
        else:
            final_path = "->".join(i for i in path)
            return jsonify({"msg":"Route is %s" %final_path}),20

    def fetch_route_info(self,command_list):
        """[This method is used to fetch the route info and perform validations and return appropriate error messages]

        Args:
            command_list ([list]): [The list containing the commands]

        Returns:
            [response]: [response code and description]
        """        
        string_to_split = command_list.split(' ')[1]
        source_device_search = re.search(r'from=(.*)&', string_to_split)
        destination_device_search = re.search(r'to=(.*)', string_to_split)
        if source_device_search and destination_device_search:
            source_device = source_device_search.group(1)
            destination_device = destination_device_search.group(1)
            if source_device in current_app.config["data"]:
                if destination_device in current_app.config["data"]: 
                    if current_app.config["data"][source_device]["type"] == deviceType.COMPUTER.name and current_app.config["data"][destination_device]["type"] == deviceType.COMPUTER.name:
                        return self.find_routes(source_device,destination_device)
                    else:
                        abort(400,"Route cannot be calculated with repeater")
                else:
                    abort(400,"Node %s not found" % destination_device)
            else:
                abort(400,"Node %s not found" % source_device)
        else:
            abort(400,"Invalid Request")