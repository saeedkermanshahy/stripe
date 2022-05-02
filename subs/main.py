import re
from turtle import end_fill
from typing import List, Tuple
from datetime import time
from unittest import result


en_text_pattern = r"<c.mono_sans>(.*?)</c.mono_sans>"
de_text_pattern = r"<c.bg_transparent>(.*?)</c.bg_transparent>"
digit_pattern = r"\d\d:\d\d:\d\d.\d\d\d"


def read_subtitle_file(path: str) -> List[str]:
    with open(path) as f:
        lines = f.readlines()
    return lines


def clean_lines(lines: List[str]) -> List[str]:
    edited_lines = [line for line in lines[15:] if not re.findall("\A\s+", line)]
    edited_lines = [re.sub("\n", "", line) for line in edited_lines]
    edited_lines = [line for line in edited_lines if len(line) > 3]
    return edited_lines


def find_pattern(line: str, pattern: str) -> str:
    return re.findall(pattern, line, flags=re.DOTALL)


def list_of_lists(lines: List[str], text_pattern: str) -> List[List[str]]:
    output = []
    temp = []
    temp_text = ""
    found_text = False
    for line in lines:
        time_res = find_pattern(line, digit_pattern)
        text_res = find_pattern(line, text_pattern)

        if len(time_res):
            if len(temp) > 0:
                temp.append(temp_text)
                found_text = False
                temp_text = ""
                output.append(temp)
            temp = [time_res]

        elif len(text_res):
            if found_text:
                temp_text += "\n"

            found_text = True
            temp_text += text_res[0]

    return output


def main():
    en_lines = read_subtitle_file("en_70105212.vtt")
    de_lines = read_subtitle_file("de_70105212.vtt")

    en_lines = clean_lines(en_lines)
    de_lines = clean_lines(de_lines)

    en_lines = list_of_lists(en_lines, text_pattern=en_text_pattern)
    de_lines = list_of_lists(de_lines, text_pattern=de_text_pattern)

    de_subtitle = ""
    en_subtitle = ""
    sub_time = ""

    output = []
    start_time = ""
    en_counter = 77
    de_counter = 41

    while en_counter < len(en_lines) or de_counter < len(de_lines):
        print(f"en_counder: {en_counter}\tde_counter:{de_counter}")
        if de_subtitle == '':
            de_line_current = de_lines[de_counter]
            de_time_current = de_line_current[0]
            de_subtitle += de_line_current[1]

            de_time_current_start = time(
                hour=int(de_time_current[0][0:2]),
                minute=int(de_time_current[0][3:5]),
                second=int(de_time_current[0][6:8]),
            )
            de_time_current_stop = time(
                hour=int(de_time_current[1][0:2]),
                minute=int(de_time_current[1][3:5]),
                second=int(de_time_current[1][6:8]),
            )

        en_line_current = en_lines[en_counter]
        en_time_current = en_line_current[0]
        en_time_current_start = time(
            hour=int(en_time_current[0][0:2]),
            minute=int(en_time_current[0][3:5]),
            second=int(en_time_current[0][6:8]),
        )
        en_time_current_stop = time(
            hour=int(en_time_current[1][0:2]),
            minute=int(en_time_current[1][3:5]),
            second=int(en_time_current[1][6:8]),
        )

        if start_time == '':
            if en_time_current_start.hour != 0:
                start_time = f"{en_time_current_start.hour}:{en_time_current_start.minute}:{en_time_current_start.second}"
            elif en_time_current_start.minute != 0:
                start_time = f"{en_time_current_start.minute}:{en_time_current_start.second}"
            else:
                start_time = f"{en_time_current_start.second}s"

        if en_time_current_start <= de_time_current_start:
            if en_time_current_stop < de_time_current_stop:
                en_subtitle = en_subtitle + ' ' + en_line_current[1]
                en_counter += 1
            
            elif en_time_current_start < de_time_current_stop:
                en_subtitle = en_subtitle + ' ' + en_line_current[1]
                en_counter += 1

            elif en_time_current_stop >= de_time_current_stop:
                # en_subtitle += en_line_current[1]
                # de_subtitle += de_line_current[1]
                if len(en_subtitle) == 0:
                    en_subtitle = en_line_current[1]
                    en_counter += 1
                output.append((en_subtitle, de_subtitle))
                en_subtitle = ''
                de_subtitle = ''
                # en_counter += 1
                de_counter += 1

        elif en_time_current_start >= de_time_current_start:
            if en_time_current_stop < de_time_current_stop:
                en_subtitle = en_subtitle + ' ' + en_line_current[1]
                en_counter += 1

            elif en_time_current_start < de_time_current_stop:
                en_subtitle = en_subtitle + ' ' + en_line_current[1]
                en_counter += 1

            elif en_time_current_stop >= de_time_current_stop:
                # en_subtitle += en_line_current[1]
                # de_subtitle += de_line_current[1]
                if len(en_subtitle) == 0:
                    en_subtitle = en_line_current[1]
                    en_counter += 1
                output.append((start_time, en_subtitle, de_subtitle))
                en_subtitle = ''
                de_subtitle = ''
                # en_counter += 1
                de_counter += 1
                start_time = ''

    return output

if __name__ == "__main__":
    output = main()
    print('end')
