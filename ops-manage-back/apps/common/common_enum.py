from enum import Enum, IntEnum, unique

@unique
class QtScanStatus(IntEnum):
    # 0: 未开始执行，1: 排队执行，2: 正在执行，3: 执行成功，4: 执行失败
    unstarted = 0
    queuing = 1
    running = 2
    success = 3
    failed = 4
