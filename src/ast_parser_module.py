from collections import defaultdict
from helper import *
import ast
from is_comment_module import is_comment


class MyNodeVisitor(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.class_dict = defaultdict(str)
        self.function_dict = defaultdict(str)

    def visit_FunctionDef(self, node):
        function_definition = ast.get_source_segment(self.source, node)
        function_name = extract_pure_function_name_from_function_signature(function_definition)
        self.function_dict[function_name] = function_definition

    def visit_ClassDef(self, node):
        class_definition = ast.get_source_segment(self.source, node)
        class_name = extract_pure_class_name_from_class_signature(class_definition)
        self.class_dict[class_name] = class_definition

    def get_all_dicts(self):
        return self.class_dict, self.function_dict


class MyAstParser:
    def __init__(self, file_dir):
        self.file_dir = file_dir
        self.file_content = read_file(self.file_dir)
        self.class_dict = defaultdict(lambda: defaultdict(list))
        self.function_implementation_dict = defaultdict(list)
        self.line_info_dict = defaultdict(tuple)
        self.global_full_statement_list = list()
        self.function_parameter_variable_associate_dict = defaultdict(list)
        self.parse_file()

    def refine_results(self, class_dict, function_implementation_dict):
        self.refine_class_dict(class_dict)
        self.refine_function_implementation_dict(function_implementation_dict)
        self.build_line_info_dict()
        self.build_global_full_statement_list()

    def parse_file(self):
        try:
            tree = ast.parse(self.file_content)
        except:
            return None
        visitor = MyNodeVisitor(self.file_content)
        visitor.visit(tree)
        class_dict, function_implementation_dict = visitor.get_all_dicts()
        self.refine_results(class_dict, function_implementation_dict)

    def refine_class_dict(self, class_dict):
        """ Changes from function_imp str to function statement list """
        for class_name in class_dict:
            class_start_line_number = find_class_start_line_number(class_name, self.file_dir)
            class_definition_list = class_dict[class_name].split('\n')
            class_definition_line = class_definition_list[0]
            method_line_dict = defaultdict(list)
            method_pure_name = None
            for line_count, line in enumerate(class_definition_list[1:], class_start_line_number + 1):
                if "def " in line.strip():
                    method_pure_name = extract_pure_function_name_from_function_signature(line)
                if method_pure_name is not None:
                    method_line_dict[method_pure_name].append((line, line_count))
            self.class_dict[(class_name, class_definition_line, class_start_line_number)] = method_line_dict

    def refine_function_implementation_dict(self, function_implementation_dict):
        """ This function reformat the function implementation dict from str to list """
        for function_name in function_implementation_dict:
            function_start_line_number = find_function_start_line_number(function_name, self.file_dir)
            for line_num, line in enumerate(function_implementation_dict[function_name].split('\n'),
                                            function_start_line_number):
                line = line.strip()
                self.function_implementation_dict[function_name].append((line, line_num))

    def build_line_info_dict(self):
        with open(self.file_dir, 'r') as f:
            full_content = f.readlines()
        line_count = 0
        while line_count < len(full_content):
            line = full_content[line_count].strip()
            if 'import ' in line or 'from ' in line:
                self.line_info_dict[(line, 'global', "import", line_count)] = (line_count, line_count)
                line_count += 1
                continue
            elif 'def ' in line:
                function_name = extract_pure_function_name_from_function_signature(line)
                length = len(self.function_implementation_dict[function_name])
                self.line_info_dict[(line, 'function', function_name, line_count)] = (line_count, line_count + length - 1)
                line_count += length
                continue
            elif 'class ' in line:
                class_name = extract_pure_class_name_from_class_signature(line)
                class_implementation_dict = self.class_dict[(class_name, line, line_count)]
                length = 0
                for method_name in class_implementation_dict:
                    length += len(class_implementation_dict[method_name])
                length += 1  # + 1 for class definition line
                self.line_info_dict[(line, 'class', class_name, line_count)] = (line_count, line_count + length - 1)
                line_count += length
                continue
            else:
                self.line_info_dict[(line, 'global', "None", line_count)] = (line_count, line_count)
                line_count += 1
                continue

    def build_global_full_statement_list(self):
        """ This function builds a list of all global full statements """
        with open(self.file_dir, 'r') as f:
            full_content = f.readlines()
        for line, scope, name, line_count in self.line_info_dict:
            if scope == 'global' and name == 'None':
                line_number = self.line_info_dict[(line, scope, name, line_count)][0]
                if is_comment(line, line_number, full_content):
                    continue
                # print("appending line = ", line, " line number = ", line_number)
                self.global_full_statement_list.append((line, line_number))

    def get_file_dir(self):
        return self.file_dir

    def get_class_dict(self):
        return self.class_dict

    def get_function_implementation_dict(self):
        return self.function_implementation_dict

    def get_line_info_dict(self):
        return self.line_info_dict

    def get_global_full_statement_list(self):
        return self.global_full_statement_list
