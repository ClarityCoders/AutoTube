from typing import Tuple


class Utils(object):
    def __init__(self):
        pass

    @staticmethod
    def _get_day_suffix(day: int) -> str:
        if day == 1 or day == 21 or day == 31:
            return "st"
        elif day == 2 or day == 22:
            return "nd"
        elif day == 3 or day == 23:
            return "rd"
        else:
            return "th"

    @staticmethod
    def _add_return_comment(comment: str) -> Tuple[str, int]:
        need_return = 30
        new_comment = ""
        return_added = 0
        if comment:
            return_added += comment.count('\n')
            for i, letter in enumerate(comment):
                if i > need_return and letter == " ":
                    letter = "\n"
                    need_return += 30
                    return_added += 1
                new_comment += letter
        return new_comment, return_added
