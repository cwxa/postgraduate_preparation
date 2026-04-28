from typing import List, Tuple, Dict, Optional

Job2M = Tuple[int, int]
Job = Tuple[int, int]
JobM = Tuple[int, ...]
Sequence = List[int]
Schedule = Dict[str, List[Tuple[int, int, int]]]
ScheduleResult = Tuple[Schedule, int, int]

DynamicJob = Tuple[int, List[int], Optional[float], Optional[int]]
DynamicSchedule = Dict[str, List[Tuple[int, int, int, Optional[float]]]]
