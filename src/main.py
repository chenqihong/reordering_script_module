from ast_parser_module import MyAstParser
from helper import *
from collections import defaultdict
import sys


def reorder_script(my_parsed_object):
    global_call_list = my_parsed_object.get_global_full_statement_list()
    function_implementation_dict = dict(my_parsed_object.get_function_implementation_dict())
    class_dict = dict(my_parsed_object.get_class_dict())
    result_list = list()
    variable_class_dict = defaultdict()
    while global_call_list:
        full_statement_call, line_number = global_call_list[0]
        global_call_list.pop(0)
        if full_statement_call.strip().startswith("#") or full_statement_call.strip() == '':
            continue
        if '# ' in full_statement_call.strip():
            full_statement_call = full_statement_call.split("#", 1)[0].strip()
        variable, statement = get_left_right(full_statement_call.strip())
        if full_statement_call.strip().startswith("def"):
            result_list.append((full_statement_call, line_number))
            continue
        # print("doing full statement = ", full_statement_call, " line number = ", line_number)

        if not is_call_statement(full_statement_call):  # Regular assignment statement
            result_list.append((full_statement_call, line_number))
            continue
        else:  # call statement
            method_call_object_name, function_pure_name = analysis_call_statement(statement)
            if method_call_object_name is None:
                is_self_defined_class_result, class_name, class_definition, class_start_line_number = is_self_defined_class(class_dict, function_pure_name)
                result_list.append((full_statement_call, line_number))
                if function_pure_name in function_implementation_dict: # not lib api call
                    function_implementation_list = function_implementation_dict[function_pure_name]
                    function_implementation_list_copy = function_implementation_list.copy()
                    function_implementation_list_copy.reverse()
                    for function_implementation_line, function_implementation_line_number in function_implementation_list_copy:
                        global_call_list.insert(0, (function_implementation_line, function_implementation_line_number))
                elif is_self_defined_class_result:
                    if variable is not None:
                        variable_class_dict[variable] = function_pure_name
                    init_method_implementation_list = class_dict[(class_name, class_definition, class_start_line_number)]['__init__']
                    init_method_implementation_list_copy = init_method_implementation_list.copy()
                    init_method_implementation_list_copy.insert(0, (class_definition, class_start_line_number))
                    init_method_implementation_list_copy.reverse()
                    for init_implementation_line, init_implementation_line_number in init_method_implementation_list_copy:
                        global_call_list.insert(0, (init_implementation_line, init_implementation_line_number))
            else: # class method call
                result_list.append((full_statement_call, line_number))
                try:
                    class_name = variable_class_dict[method_call_object_name]
                except KeyError:
                    is_self_defined_class_result, class_name, class_definition, class_start_line_number = is_self_defined_class(class_dict, method_call_object_name)
                    if not is_self_defined_class_result:
                        continue
                    class_name = method_call_object_name
                is_self_defined_class_result, class_name, class_definition, class_start_line_number = is_self_defined_class(class_dict, class_name)
                method_implementation_list = class_dict[(class_name, class_definition, class_start_line_number)][function_pure_name]
                method_implementation_list_copy = method_implementation_list.copy()
                method_implementation_list_copy.reverse()
                for method_implementation_line, method_implementation_line_number in method_implementation_list_copy:
                    global_call_list.insert(0, (method_implementation_line, method_implementation_line_number))
            parameter_call_list = get_parameter_call_list(statement)
            parameter_call_list_copy = parameter_call_list.copy()
            parameter_call_list_copy.reverse()
            for parameter in parameter_call_list_copy:
                if is_call_statement(parameter):
                    global_call_list.insert(0, (parameter, line_number))

    return result_list


def main():
    if len(sys.argv) != 2:
        print("not enough arguments")
        exit(0)
    script_dir = sys.argv[1]
#    script_dir = "/Users/qihongchen/Desktop/reordering_script_module/inputs/a.py"
    my_parsed_object = MyAstParser(script_dir)
    reordering_list = reorder_script(my_parsed_object)
    for line, line_num in reordering_list:
        print("line = ", line, " line_num = ", line_num)
    return reordering_list

if __name__ == '__main__':
    main()