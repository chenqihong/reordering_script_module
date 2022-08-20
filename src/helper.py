def read_file(file_dir):
    with open(file_dir, 'r') as f:
        file_content = f.read()
    return file_content



def extract_pure_function_name_from_function_signature(function_definition: str) -> str:
    """
    Extract pure function name from a def function signature
    :param function_definition: def hi():
    :return: hi
    """
    function_definition = function_definition.strip()
    split_list = function_definition.split(" ")
    if function_definition.count(" ") == 1:
        x = split_list[1].split("(")[0]
        if len(x) > 0 and x[-1] == ")":
            return x[:-1]
        return x
    x = function_definition.split("(")[0].split(" ")[-1]
    if len(x) > 0 and x[-1] == ")":
        return x[:-1]
    return x


def extract_pure_class_name_from_class_signature(class_definition: str) -> str:
    """
    Extract class name from a class definition signature
    :param class_definition: class h(k): or class h
    :return: h
    """
    class_line = class_definition.split("\n")[0]
    if '(' not in class_line:
        if class_line[-1] == ':':
            return class_line.split(' ')[1].strip()[:-1]
        else:
            return class_line.split(' ')[1].strip()
    else:
        return class_line.split(' ')[1].split('(')[0].strip()


def find_class_start_line_number(class_name, file_dir):
    target_line = "class {}".format(class_name)
    with open(file_dir, 'r') as f:
        full_content = f.readlines()
    for line_count, line in enumerate(full_content):
        if target_line in line:
            return line_count


def find_function_start_line_number(function_name, file_dir):
    with open(file_dir, 'r') as f:
        full_content = f.readlines()
    target_line = "def " + function_name
    for line_count, line in enumerate(full_content):
        if target_line in line:
            return line_count


def find_line_scope(line_count, line_info_dict):
    for line, scope, name in line_info_dict:
        start_line_num, end_line_num = line_info_dict[(line, scope, name)]
        if start_line_num <= line_count <= end_line_num:
            return scope, name
    return 'global', None


def analysis_call_statement(statement):
    """ This function takes a call statement, and gets the method call object name and function_pure_name """
    if '.' in statement:
        method_call_object_name, function_pure_name = statement.split(".", 1)
        method_call_object_name = method_call_object_name.strip()
        function_pure_name = function_pure_name.split("(", 1)[0].strip()
    else:
        method_call_object_name = None
        function_pure_name = statement.split('(', 1)[0].strip()
    return method_call_object_name, function_pure_name


def is_call_statement(statement):
    """ This function checks if it is a call i.e. hello() or a.b() """
    if '(' not in statement:
        return False
    else:
        index = statement.index('(')
        prev_char = statement[index-1]
        if prev_char == '.' or prev_char.isalpha():
            return True
        else:
            return False


def get_left_right(call_statement):
    if '=' in call_statement and '(' in call_statement:
        if call_statement.index('=') > call_statement.index("("):
            return None, call_statement
    if '=' in call_statement:
        left, right = call_statement.split('=', 1)
        left = left.strip()
        right = right.strip()
    else:
        left = None
        right = call_statement.strip()
    return left, right


def is_self_defined_class(class_dict, function_pure_name):
    for class_name, class_definition, class_start_line_number in class_dict:
        if class_name == function_pure_name:
            return True, class_name, class_definition, class_start_line_number
    return False, None, None, None


def get_parameter_call_list(statement):
    print("statement = ", statement)
    if '(' not in statement:
        return []
    statement = statement.split("(", 1)[1].strip()
    parameter_list = statement.split(",")
    return parameter_list