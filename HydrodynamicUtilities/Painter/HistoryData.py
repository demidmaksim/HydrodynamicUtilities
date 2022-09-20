from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicModelAnalysis.Models import WellMeasurement, WellHistory
    from HydrodynamicModelAnalysis.Models import TimeSeries
    from HydrodynamicModelAnalysis.Models.Strategy.Frame import ScheduleSheet
    from typing import Optional


import plotly.graph_objects as go
from plotly.subplots import make_subplots


class HistoryDataPainter:
    def __init__(self) -> None:
        pass

    def print_oil(
        self,
        wch: ScheduleSheet,
        measurement: WellMeasurement,
        fig: go.Figure,
    ) -> None:
        time = wch.Time
        value = wch.OilFlowRate.values
        trace = go.Scatter(
            x=time,
            y=value,
            name="Schedule",
            legendgroup="oil",
            line_shape="hv",
            line={"color": "red", "width": 1},
        )
        fig.add_trace(trace)

        measurement: Optional[TimeSeries] = measurement.OilProd.drop_nan()
        time_moment = measurement.get_time().to_datetime64()
        if measurement is not None:
            trace = go.Scatter(
                x=time_moment,
                y=measurement.values,
                mode="markers",
                name="measurement",
                legendgroup="oil",
                marker={"color": "red", "size": 10},
            )

            fig.add_trace(trace)

    def print_wat(
        self,
        wch: ScheduleSheet,
        measurement: WellMeasurement,
        fig: go.Figure,
    ) -> None:
        time = wch.Time
        value = wch.WaterFlowRate.values
        trace = go.Scatter(
            x=time,
            y=value,
            name="Schedule",
            legendgroup="wat",
            line_shape="hv",
            line={"color": "blue", "width": 1},
        )
        fig.add_trace(trace)

        measurement: Optional[TimeSeries] = measurement.WatProd.drop_nan()
        time_moment = measurement.get_time().to_datetime64()
        if measurement is not None:
            trace = go.Scatter(
                x=time_moment,
                y=measurement.values,
                mode="markers",
                name="measurement",
                legendgroup="wat",
                marker={"color": "blue", "size": 10},
            )

            fig.add_trace(trace)

    def print_gas(
        self,
        wch: ScheduleSheet,
        measurement: WellMeasurement,
        fig: go.Figure,
    ) -> None:
        time = wch.Time
        value = wch.GasFlowRate.values
        trace = go.Scatter(
            x=time,
            y=value,
            name="Schedule",
            legendgroup="gas",
            line_shape="hv",
            line={"color": "gray", "width": 1},
        )
        fig.add_trace(trace, secondary_y=True)

        measurement: Optional[TimeSeries] = measurement.GasProd.drop_nan()
        time_moment = measurement.get_time().to_datetime64()
        if measurement is not None:
            trace = go.Scatter(
                x=time_moment,
                y=measurement.values,
                mode="markers",
                name="measurement",
                legendgroup="gas",
                marker={"color": "gray", "size": 10},
            )

            fig.add_trace(trace, secondary_y=True)

    def do(self, wh: WellHistory) -> None:
        tv = wh.get_time_vector("D", 1)
        wconhist = wh.get_wconhist(tv)
        measurement = wh.Measurement
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        self.print_oil(wconhist, measurement, fig)
        self.print_wat(wconhist, measurement, fig)
        self.print_gas(wconhist, measurement, fig)
        fig.show()
