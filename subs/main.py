import re
from typing import List, Tuple
from datetime import time


# This patters is used to find text from english subtitles
EN_TEXT_PATTERN = r"<c.mono_sans>(.*?)</c.mono_sans>"

# This pattern is used to find text from Deutsch subtitles
DE_TEXT_PATTERN = r"<c.bg_transparent>(.*?)</c.bg_transparent>"

# This pattern is used to find time of subtitles
DIGIT_PATTERN = r"\d\d:\d\d:\d\d.\d\d\d"

ENGLISH_SUBTITLE_PATH = "en_70105212.vtt"
DEUTSCH_SUBTITLE_PATH = "de_70105212.vtt"


def read_subtitle_file(path: str) -> List[str]:
    """
    path: Path to subtitle file
    return: lines of subtitle file as a list of strings
    """
    with open(path) as file:
        lines = file.readlines()
    return lines


def clean_lines(lines: List[str]) -> List[str]:
    """
    lines: List of lines of a subtitle file
    return: cleaned lines with no white spaces, new lines and number of each
    subtitle text
    """
    # Remove blank lines
    cleaned_lines = [line for line in lines[15:] if not re.findall("\A\s+", line)]
    # Replace new lines with white space
    cleaned_lines = [re.sub("\n", "", line) for line in cleaned_lines]
    # Remove lines with length less than 3 characters
    cleaned_lines = [line for line in cleaned_lines if len(line) > 3]
    return cleaned_lines


def find_pattern(line: str, pattern: str) -> str:
    """
    line: A string line
    pattern: pattern which should be found
    return: content that satisifes the patters otherwise an empty list
    """
    return re.findall(pattern, line, flags=re.DOTALL)


def create_list_of_time_and_subtitle(
    lines: List[str], text_pattern: str
) -> List[List[str]]:
    """
    lines: A list of lines of subtitle file
    text_pattern: Pattern of subtitle, english or deutsh
    return: A list of lists in following format:
        [
            [[start_time, end_time], text],
            .
            .
            .
        ]
    """

    # A list of [[start_time, end_time], text]s
    output = []
    # Temporary list to keep [[start_time, end_time], text]
    temp_list = []
    # Temporary text, to keep multiple lines of subtitles of each timing
    # In Deutsch in some cases for one timing we have two lines of
    # subtitles
    temp_text = ""
    # To check if we have found a subtitle
    found_text = False

    for line in lines:
        time_res = find_pattern(line, DIGIT_PATTERN)
        text_res = find_pattern(line, text_pattern)

        # if we have found time
        if len(time_res):
            if len(temp_list) > 0:
                temp_list.append(temp_text)
                # Set it False cause we have found time
                found_text = False
                # Erase it for saving new subtitles
                temp_text = ""
                output.append(temp_list)
            temp_list = [time_res]

        # If we have found subtitle text
        elif len(text_res):
            # If we have found text before (not time)
            # This happens only for Deutsch subtitle
            if found_text:
                temp_text += "\n"

            # Set it True cause we have found subtitle text
            found_text = True
            temp_text += text_res[0]

    return output


def convert_to_time(sub_time: str) -> Tuple[time, time]:
    """
    sub_time: time in string format
    return: starting and ending time with time format
    """
    return time(
        hour=int(sub_time[0][0:2]),
        minute=int(sub_time[0][3:5]),
        second=int(sub_time[0][6:8]),
    ), time(
        hour=int(sub_time[1][0:2]),
        minute=int(sub_time[1][3:5]),
        second=int(sub_time[1][6:8]),
    )


def read():
    """
    Reads two subtitle files, clean them and make list of lists of
    [[start_time, end_time], text] format and returns the result
    """
    en_lines = read_subtitle_file(ENGLISH_SUBTITLE_PATH)
    de_lines = read_subtitle_file(DEUTSCH_SUBTITLE_PATH)

    en_lines = clean_lines(en_lines)
    de_lines = clean_lines(de_lines)

    en_lines = create_list_of_time_and_subtitle(en_lines, text_pattern=EN_TEXT_PATTERN)
    de_lines = create_list_of_time_and_subtitle(de_lines, text_pattern=DE_TEXT_PATTERN)

    return en_lines, de_lines


def create_time_format(current_time: time) -> str:
    """
    current_time: current time to change its format to string
            in hour:minute:second or minute:second is seconds format
    return: string format of input current time
    """
    if current_time.hour != 0:
        start_time = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
    elif current_time.minute != 0:
        start_time = f"{current_time.minute}:{current_time.second}"
    else:
        start_time = f"{current_time.second}s"

    return start_time


def main():
    en_lines, de_lines = read()
    de_subtitle = ""
    en_subtitle = ""
    sub_time = ""

    # List of lists of [start_time, en_subtitle_line, de_subtitle_line] format
    output = []
    # to hold start time of each subtitle line
    start_time = ""
    en_counter = 77
    de_counter = 41

    while en_counter < len(en_lines) or de_counter < len(de_lines):
        print(f"en_counder: {en_counter}\tde_counter:{de_counter}")

        # Cause for each line of Deutsch the is two English lines
        # we read Deutsch lines if it is necessary
        if de_subtitle == "":
            de_line_current = de_lines[de_counter]
            de_time_current = de_line_current[0]
            de_subtitle += de_line_current[1]

            # Convert to time format to make comparisons easy
            de_time_current_start, de_time_current_end = convert_to_time(
                de_time_current
            )

        en_line_current = en_lines[en_counter]
        en_time_current = en_line_current[0]

        # Convert to time format to make comparisons easy
        en_time_current_start, en_time_current_end = convert_to_time(en_time_current)

        if start_time == "":
            start_time = create_time_format(en_time_current_start)

        # To check if english is started earlier
        if en_time_current_start <= de_time_current_start:
            # If detsch is inside english
            if en_time_current_end >= de_time_current_end:
                # If we it is first english subtitle we observe
                if len(en_subtitle) == 0:
                    en_subtitle = en_line_current[1]
                    en_counter += 1
                output.append((en_subtitle, de_subtitle))
                en_subtitle = ""
                de_subtitle = ""
                de_counter += 1

            # If english subtitle is before deutch
            else:
                en_subtitle = en_subtitle + " " + en_line_current[1]
                # increment counter to fetch another english line
                en_counter += 1

        # Check if english is started later than deutsch
        elif en_time_current_start >= de_time_current_start:
            # There is no overlap or deutsch is completely inside english
            if en_time_current_end >= de_time_current_end:
                if len(en_subtitle) == 0:
                    en_subtitle = en_line_current[1]
                    en_counter += 1
                output.append((start_time, en_subtitle, de_subtitle))
                en_subtitle = ""
                de_subtitle = ""
                de_counter += 1
                start_time = ""
            # There is overlap
            else:
                en_subtitle = en_subtitle + " " + en_line_current[1]
                en_counter += 1

    return output


if __name__ == "__main__":
    output = main()
    print("end")
