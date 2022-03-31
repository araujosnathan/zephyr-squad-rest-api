from enum import IntEnum


class TestStatus(IntEnum):
    PASS = 1
    FAIL = 2
    WIP = 3
    BLOCKED = 4
    NOT_EXECUTED = -1
