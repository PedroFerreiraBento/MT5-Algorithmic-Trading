import sys
import matplotlib

# matplotlib.use("QtAgg")
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy, QWidget
import PyQt6.QtGui as QtGui
import mplfinance as mpf
import matplotlib.pyplot as plt
from pandas import DataFrame
import sys


class MplCanvas(FigureCanvas):
    def __init__(
        self,
        title: str = None,
        parent: QWidget = None,
        width: int = 10,
        height: int = 7,
        dpi: int = 200,
    ) -> None:
        """PyQt6 Figure Canvas

        Args:
            title (str, optional): Figure Title. Defaults to None.
            parent (QWidget, optional): Figure Parent. Defaults to None.
            width (int, optional): Figure Width. Defaults to 10.
            height (int, optional): Figure Height. Defaults to 7.
            dpi (int, optional): Figure dots(pixes) per inches. Defaults to 200.
        """

        # Create figure
        fig = Figure(figsize=(width, height), dpi=dpi)

        # Create a subplot for shared price/volume axis
        self.price_ax = plt.subplot2grid((7, 1), (0, 0), rowspan=5, colspan=1, fig=fig)

        # Create a subplot for net worth axis
        self.net_worth_ax = plt.subplot2grid(
            (7, 1), (5, 0), rowspan=2, colspan=1, fig=fig, sharex=self.price_ax
        )

        # Initialize a figure canvas with the created figure
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        # Plot axes
        self.price_ax.plot()
        self.net_worth_ax.plot()

        # Set figure
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        FigureCanvas.updateGeometry(self)
        self.setWindowTitle("Trading Environment")

    def config_axes(self) -> None:
        """Configure axes"""
        # Hide X axis from upper subplots
        plt.setp(self.price_ax.get_xticklabels(), visible=False)

        # Set axes labels
        self.price_ax.set_ylabel("Price")
        self.net_worth_ax.set_ylabel("Balance")

        # Set yaxis ticks and label to right
        self.price_ax.yaxis.tick_right()
        self.net_worth_ax.yaxis.tick_right()
        self.price_ax.yaxis.set_label_position("left")
        self.net_worth_ax.yaxis.set_label_position("left")

    def start_app(self) -> None:
        """Start a PyQt6 Application"""
        app = QtGui.QGuiApplication.instance()

        if app is None:
            app = QtGui.QApplication(sys.argv)

        return app


class CandleStickWindow(MplCanvas):
    """Simple canvas with a sine plot."""

    def __init__(self, backtest_env, **kwargs):
        super().__init__(**kwargs)

        self.app = self.start_app()
        self.backtest_env = backtest_env
        self.setStyleSheet("padding: 15px")

    def show(self, *args, **kwargs):
        super().show(*args, **kwargs)
        self.showMaximized()
        self.update_figure()
        self.app.processEvents()

    def update_figure(self):
        # Define render range
        self.start_range = (
            0
            if self.backtest_env.render_range > self.backtest_env.current_step
            else (self.backtest_env.current_step - self.backtest_env.render_range + 1)
        )
        self.end_range = (
            self.backtest_env.render_range
            if self.backtest_env.render_range > self.backtest_env.current_step
            else self.backtest_env.current_step + 1
        )

        # Set Datetime as index for mplfinance plot
        self.data = self.backtest_env.df.set_index("Datetime")
        self.candles = self.data[self.start_range : self.end_range]

        # Clear axes
        self.price_ax.cla()
        self.net_worth_ax.cla()

        # Reset alines
        self.alines = {
            "lines": [],
            "colors": [],
            "linewidths": [],
        }

        # Reset vlines
        self.vlines = {
            "lines": [],
            "colors": [],
            "linewidths": [],
        }

        # Add support and resistance trend lines
        self.__add_support_and_resistance_trend_lines()

        # Plot candlestick chart on price Axes
        mpf.plot(
            self.candles,
            ax=self.price_ax,
            type="candle",
            style="charles",
            vlines=dict(
                vlines=self.vlines["lines"],
                colors=self.vlines["colors"],
                linewidths=self.vlines["linewidths"],
            ),
            alines=dict(
                alines=self.alines["lines"],
                colors=self.alines["colors"],
                linewidths=self.alines["linewidths"],
            ),
        )

        # Configure Axes
        self.config_axes()

        # Draw Figure
        self.draw()

    def __get_line_points(self, line_points):
        idx = self.candles.index
        line_i = len(self.candles) - len(line_points)
        assert line_i >= 0
        points = []
        for i in range(
            line_i,
            len(self.candles),
        ):
            points.append((idx[i], line_points[i - line_i]))
        return points

    def __add_support_and_resistance_trend_lines(self):
        if (
            self.backtest_env.support_coefs_c is not None
            and self.backtest_env.resist_coefs_c is not None
        ):
            support_line_c = (
                self.backtest_env.support_coefs_c[0]
                * np.arange(len(self.backtest_env.trend_line_interval_values))
                + self.backtest_env.support_coefs_c[1]
            )
            resist_line_c = (
                self.backtest_env.resist_coefs_c[0]
                * np.arange(len(self.backtest_env.trend_line_interval_values))
                + self.backtest_env.resist_coefs_c[1]
            )

            support_line = self.__get_line_points(support_line_c)
            resistance_line = self.__get_line_points(resist_line_c)

            self.alines["lines"].extend([support_line, resistance_line])
            self.alines["colors"].extend(["b", "b"])
            self.alines["linewidths"].extend([1, 1])
