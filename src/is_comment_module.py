def is_target_statement(current_line: str, current_line_count: int, full_line: str, line_number: int) -> bool:
    """
    This function checks whether the current processing line is the target line
    :param current_line: The current checking line
    :param current_line_count: The current checking line's line count
    :param full_line: The passing target line
    :param line_number: The passing target line's line number
    :return: return True if the checking line is the target line False otherwise
    """
    if current_line == full_line and line_number == current_line_count:
        return True
    return False


def is_comment(full_line: str, line_number: int, full_content: list) -> bool:
    """
    This function checks whether the passing line is a comment or not
    :param full_line: the checking line
    :param line_number: The line count
    :param full_content: The full content of the file that line belongs to
    :return: return True if the passing line is a comment False otherwise
    """
    relevant_content = full_content[: line_number + 1]
    full_line = full_line.strip()
    single_quote_occurrence = 0
    double_quote_occurrence = 0
    is_comment_now = False
    is_multi_line_str = False
    multi_line_str_start_mark = ""
    for current_line_count in range(len(relevant_content)):
        current_line = relevant_content[current_line_count].strip()
        if not is_multi_line_str and ("'''" in current_line or '"""' in current_line) and (
                current_line[:3] != "'''" and current_line[:3] != '"""'):
            is_multi_line_str = True
            if '"""' in current_line:
                multi_line_str_start_mark = '"""'
            else:
                multi_line_str_start_mark = "'''"
        if is_multi_line_str and multi_line_str_start_mark is not None and current_line[
                                                                           :3] == multi_line_str_start_mark:
            if is_target_statement(current_line, current_line_count, full_line, line_number):
                return False
            is_multi_line_str = False
            is_comment_now = False
            multi_line_str_start_mark = None
            continue
        if current_line == "" and is_target_statement(current_line, current_line_count, full_line, line_number):
            return is_comment_now
        if current_line == "" and not is_target_statement(current_line, current_line_count, full_line, line_number):
            continue
        if current_line.startswith("#"):
            if is_target_statement(current_line, current_line_count, full_line, line_number):
                if is_multi_line_str:
                    return False
                else:
                    return True
            if (single_quote_occurrence == 0 or single_quote_occurrence == 2) and (
                    double_quote_occurrence == 0 or double_quote_occurrence == 2):
                is_comment_now = False
        if not is_comment_now and "'" not in current_line[0] and '"' not in current_line[0] and is_target_statement(
                current_line, current_line_count, full_line, line_number):  # 这是处理当目前不是comment，但是在结尾有个quote的情况，直接false
            return False
        if ("'" in current_line[0:4] or "'" in current_line[-4:]) and single_quote_occurrence < 2:
            if current_line.count("'") == 3:
                single_quote_occurrence += 1
            if is_target_statement(current_line, current_line_count, full_line, line_number):
                if is_multi_line_str:
                    return False
                else:
                    return True
            if single_quote_occurrence == 1 and not is_comment_now and not (current_line.count("'") > 3):
                if is_multi_line_str:
                    is_comment_now = False
                else:
                    is_comment_now = True
            if single_quote_occurrence == 1 and not is_comment_now and current_line.count("'") > 3 and (
                    double_quote_occurrence == 0 or double_quote_occurrence == 2):
                is_comment_now = False
                single_quote_occurrence += 1
            if single_quote_occurrence == 2 and current_line.count("'") == 3:
                if double_quote_occurrence == 0 or double_quote_occurrence == 2:
                    is_comment_now = False
                if double_quote_occurrence == 1:
                    if is_multi_line_str:
                        is_comment_now = False
                    else:
                        is_comment_now = True
                single_quote_occurrence = 0

        if ('"' in current_line[0:4] or '"' in current_line[-4:]) and double_quote_occurrence < 2:
            if current_line.count('"') == 3:
                double_quote_occurrence += 1
            if is_target_statement(current_line, current_line_count, full_line, line_number):
                if is_multi_line_str:
                    return False
                else:
                    return True
            if double_quote_occurrence == 1 and not is_comment_now and not (current_line.count('"') > 3):
                if is_multi_line_str:
                    is_comment_now = False
                else:
                    is_comment_now = True
            if double_quote_occurrence == 1 and not is_comment_now and current_line.count('"') > 3 and (
                    single_quote_occurrence == 0 or single_quote_occurrence == 2):
                is_comment_now = False
                double_quote_occurrence += 1
            if double_quote_occurrence == 2 and current_line.count('"') == 3:
                if single_quote_occurrence == 0 or single_quote_occurrence == 2:
                    is_comment_now = False
                if single_quote_occurrence == 1:
                    if is_multi_line_str:
                        is_comment_now = False
                    else:
                        is_comment_now = True
                double_quote_occurrence = 0
    return is_comment_now
