from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterator, Optional, Dict, Tuple, Union
    import numpy as np
    from pathlib import Path

from copy import deepcopy
from .Frame import ScheduleDataframe, ScheduleSheet
from HydrodynamicUtilities.Models.Time import NonLinearTime, TimePoint, TimeVector

# from Writer.Schedule import create_schedule


class ReportSteps(NonLinearTime):
    def __init__(
        self,
        start: TimePoint,
        finish: TimePoint,
        base_step: Tuple[str, int],
        additional_control: Dict[TimePoint, Tuple[str, int]] = None,
    ) -> None:
        super().__init__(start, finish, base_step, additional_control)


class Strategy:
    def __init__(
        self,
        events: ScheduleDataframe = None,
        report_steps: ReportSteps = None,
    ) -> None:
        self.Events = events
        self.ReportSteps = report_steps

    def __add__(self, other: Strategy) -> Strategy:

        if self.Events is not None and other.Events is not None:
            events = self.Events + other.Events
        elif self.Events is not None:
            events = self.Events
        elif other.Events is not None:
            events = other.Events
        else:
            events = None

        return Strategy(events, self.ReportSteps)

    def __iter__(self) -> Iterator[ScheduleSheet]:
        if self.Events is not None:
            for sheet in self.Events:
                yield sheet

    def get_steps(self) -> Optional[TimeVector]:
        return self.ReportSteps.get_time_vector()

    def set_time_steps_settings(
        self,
        start: TimePoint,
        finish: TimePoint,
        base_step: Tuple[str, int],
        additional_control: Dict[TimePoint, Tuple[str, int]] = None,
    ) -> None:
        self.ReportSteps = ReportSteps(
            start,
            finish,
            base_step,
            additional_control,
        )

    def drop_nan_time(self, in_place: bool = True) -> Optional[Strategy]:
        if in_place:
            if self.Events is not None:
                self.Events.drop_nan_time(in_place)
                return None
        else:
            if self.Events is not None:
                new_events = self.Events.drop_nan_time(in_place=False)
                new = deepcopy(self)
                new.Events = new_events
                return new

    """
    def to_schedule(self, path: Union[str, Path] = "Results.sch") -> None:
        sdf = self.Events
        create_schedule(sdf, path=path)
    """
