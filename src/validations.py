from flask import abort
from flask.json import jsonify
from src.operations import Operations
command_type_list = ['CREATE','FETCH','MODIFY']

def get_content_type(headers_list):
    """[This method is used to get content type from headers list]

    Args:
        headers_list ([list]): [The list of headers]

    Returns:
        [string]: [content type]
    """    #

    for i in headers_list:
        if 'content-type' in i:
            content_type_list =i.split(':')
            return content_type_list[-1]
        
    return ""

def do_validation(list_of_body):
    """This method is used to do validations and call the corresponding endpoint

    Args:
        list_of_body ([list]): [The list containing the body of the command]

    Returns:
        [response]: [The code and description of the response]
    """    
    #getting command list and type
    command_list = list_of_body[0]
    command_type = command_list.split(' ')[0]
    obj = Operations()

    if command_type in command_type_list:
        if command_type == "FETCH":
            command = command_list.split(' ')[1]
            if command == "/devices":
                return obj.fetch_devices()
            else:
                return obj.fetch_route_info(command_list)
        else:
            if len(command_list) >= 4:
                command = command_list.split(' ')[1]
                #getting command body
                print(list_of_body)
                command_body = list_of_body[-1]

                #getting contenttype header
                new_line_index = list_of_body.index('')
                headers_list = list_of_body[1:new_line_index]
                content_type = get_content_type(headers_list)
                if content_type == "":
                    abort(400)
                if command_type == "CREATE":
                    if command == "/devices":
                        print(command)
                        return obj.create_device(content_type,command_body)
                    elif command == "/connections":
                        return obj.connect_devices(content_type,command_body)
                elif command_type == "MODIFY":
                    return obj.change_device_strength(content_type,command_body,command)
            else:
                abort(404)
        
    else:
        abort(404)
