import asyncio
import os
from datetime import datetime
from typing import Union, Literal, List
import pandas as pd

from .table import Table
from .toolbox import ToolBox
from .topbar import TopBar
from .util import (
    IDGen, jbool, Pane, Events, TIME, NUM, FLOAT,
    LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, CROSSHAIR_MODE, PRICE_SCALE_MODE,
    line_style, marker_position, marker_shape, crosshair_mode, price_scale_mode,
)

JS = {}
current_dir = os.path.dirname(os.path.abspath(__file__))
for file in ('pkg', 'funcs', 'callback', 'toolbox', 'table'):
    with open(os.path.join(current_dir, 'js', f'{file}.js'), 'r', encoding='utf-8') as f:
        JS[file] = f.read()

TEMPLATE = f"""
<!DOCTYPE html>
<html lang="">
<head>
    <title>lightweight-charts-python</title>
    <script>{JS['pkg']}</script>
    <meta name="viewport" content ="width=device-width, initial-scale=1">
    <style>
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
            Cantarell, "Helvetica Neue", sans-serif;
    }}
    #wrapper {{
        width: 100vw;
        height: 100vh;
        background-color: #000000;
    }}
    </style>
</head>
<body>
    <div id="wrapper"></div>
    <script>
    {JS['funcs']}
    {JS['table']}
    </script>
</body>
</html>
"""


class Window:
    _id_gen = IDGen()
    handlers = {}

    def __init__(self, script_func: callable = None, js_api_code: str = None, run_script: callable = None):
        self.loaded = False
        self.script_func = script_func
        self.scripts = []
        self.final_scripts = []

        if run_script:
            self.run_script = run_script

        if js_api_code:
            self.run_script(f'window.callbackFunction = {js_api_code}')

    def on_js_load(self):
        if self.loaded:
            return
        self.loaded = True
        [self.run_script(script) for script in self.scripts]
        [self.run_script(script) for script in self.final_scripts]

    def run_script(self, script: str, run_last: bool = False):
        """
        For advanced users; evaluates JavaScript within the Webview.
        """
        if self.loaded:
            self.script_func(script)
            return
        self.scripts.append(script) if not run_last else self.final_scripts.append(script)

    def create_table(self, width: NUM, height: NUM, headings: tuple, widths: tuple = None,
                     alignments: tuple = None, position: FLOAT = 'left', draggable: bool = False,
                     func: callable = None
                     ) -> 'Table':
        return Table(self, width, height, headings, widths, alignments, position, draggable, func)

    def create_subchart(self, position: FLOAT = 'left', width: float = 0.5, height: float = 0.5,
                        sync: str = None, scale_candles_only: bool = False, toolbox: bool = False
                        ) -> 'AbstractChart':
        subchart = AbstractChart(self, width, height, scale_candles_only, toolbox, position=position)
        if not sync:
            return subchart
        sync_id = sync
        self.run_script(f'''
        syncCrosshairs({subchart.id}.chart, {sync_id}.chart)
        {sync_id}.chart.timeScale().subscribeVisibleLogicalRangeChange((timeRange) => {{
            {subchart.id}.chart.timeScale().setVisibleLogicalRange(timeRange)
        }})
        {subchart.id}.chart.timeScale().setVisibleLogicalRange(
            {sync_id}.chart.timeScale().getVisibleLogicalRange()
        )
        ''', run_last=True)
        return subchart


class SeriesCommon(Pane):
    def __init__(self, chart: 'AbstractChart'):
        super().__init__(chart.win)
        self._chart = chart
        self._interval = pd.Timedelta(seconds=1)
        self._last_bar = None
        self.num_decimals = 2

    def _set_interval(self, df: pd.DataFrame):
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        common_interval = df['time'].diff().value_counts()
        if common_interval.empty:
            return
        self._interval = common_interval.index[0]
        self.run_script(
            f'if ({self.id}.toolBox) {self.id}.toolBox.interval = {self._interval.total_seconds() * 1000}'
        )

    @staticmethod
    def _format_labels(data, labels, index, exclude_lowercase):
        def rename(la, mapper):
            return [mapper[key] if key in mapper else key for key in la]
        if 'date' not in labels and 'time' not in labels:
            labels = labels.str.lower()
            if exclude_lowercase:
                labels = rename(labels, {exclude_lowercase.lower(): exclude_lowercase})
        if 'date' in labels:
            labels = rename(labels, {'date': 'time'})
        elif 'time' not in labels:
            data['time'] = index
            labels = [*labels, 'time']
        return labels

    def _df_datetime_format(self, df: pd.DataFrame, exclude_lowercase=None):
        df = df.copy()
        df.columns = self._format_labels(df, df.columns, df.index, exclude_lowercase)
        self._set_interval(df)
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        df['time'] = df['time'].astype('int64') // 10 ** 9
        return df

    def _series_datetime_format(self, series: pd.Series, exclude_lowercase=None):
        series = series.copy()
        series.index = self._format_labels(series, series.index, series.name, exclude_lowercase)
        series['time'] = self._single_datetime_format(series['time'])
        return series

    def _single_datetime_format(self, arg):
        if not pd.api.types.is_datetime64_any_dtype(arg):
            arg = pd.to_datetime(arg)
        interval_seconds = self._interval.total_seconds()
        arg = interval_seconds * (arg.timestamp() // interval_seconds)
        return arg

    def marker(self, time: datetime = None, position: MARKER_POSITION = 'below',
               shape: MARKER_SHAPE = 'arrow_up', color: str = '#2196F3', text: str = ''
                ) -> str:
        """
        Creates a new marker.\n
        :param time: Time location of the marker. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The id of the marker placed.
        """
        try:
            time = self._last_bar['time'] if not time else self._single_datetime_format(time)
        except TypeError:
            raise TypeError('Chart marker created before data was set.')
        marker_id = self.win._id_gen.generate()
        self.run_script(f"""
            {self.id}.markers.push({{
                time: {time if isinstance(time, float) else f"'{time}'"},
                position: '{marker_position(position)}',
                color: '{color}',
                shape: '{marker_shape(shape)}',
                text: '{text}',
                id: '{marker_id}'
                }});
            {self.id}.series.setMarkers({self.id}.markers)""")
        return marker_id

    def remove_marker(self, marker_id: str):
        """
        Removes the marker with the given id.\n
        """
        self.run_script(f'''
           {self.id}.markers.forEach(function (marker) {{
               if ('{marker_id}' === marker.id) {{
                   {self.id}.markers.splice({self.id}.markers.indexOf(marker), 1)
                   {self.id}.series.setMarkers({self.id}.markers)
                   }}
            }});''')

    def horizontal_line(self, price: NUM, color: str = 'rgb(122, 146, 202)', width: int = 2,
                        style: LINE_STYLE = 'solid', text: str = '', axis_label_visible: bool = True,
                        func: callable = None
                        ) -> 'HorizontalLine':
        """
        Creates a horizontal line at the given price.
        """
        return HorizontalLine(self, price, color, width, style, text, axis_label_visible, func)

    def remove_horizontal_line(self, price: NUM = None):
        """
        Removes a horizontal line at the given price.
        """
        self.run_script(f'''
        {self.id}.horizontal_lines.forEach(function (line) {{
            if ({price} === line.price) line.deleteLine()
        }})''')

    def clear_markers(self):
        """
        Clears the markers displayed on the data.\n
        """
        self.run_script(f'''{self.id}.markers = []; {self.id}.series.setMarkers([])''')

    def clear_horizontal_lines(self):
        """
        Clears the horizontal lines displayed on the data.\n
        """
        self.run_script(f'''
        {self.id}.horizontal_lines.forEach(function (line) {{{self.id}.series.removePriceLine(line.line);}});
        {self.id}.horizontal_lines = [];
        ''')

    def price_line(self, label_visible: bool = True, line_visible: bool = True, title: str = ''):
        self.run_script(f'''
        {self.id}.series.applyOptions({{
            lastValueVisible: {jbool(label_visible)},
            priceLineVisible: {jbool(line_visible)},
            title: '{title}',
        }})''')

    def precision(self, precision: int):
        """
        Sets the precision and minMove.\n
        :param precision: The number of decimal places.
        """
        self.run_script(f'''
        {self.id}.precision = {precision}
        {self.id}.series.applyOptions({{
            priceFormat: {{precision: {precision}, minMove: {1 / (10 ** precision)}}}
        }})''')
        self.num_decimals = precision

    def hide_data(self):
        self._toggle_data(False)

    def show_data(self):
        self._toggle_data(True)

    def _toggle_data(self, arg):
        self.run_script(f'''
        {self.id}.series.applyOptions({{visible: {jbool(arg)}}})
        if ('volumeSeries' in {self.id}) {self.id}.volumeSeries.applyOptions({{visible: {jbool(arg)}}})
        ''')


class HorizontalLine(Pane):
    def __init__(self, chart, price, color, width, style, text, axis_label_visible, func):
        super().__init__(chart.win)
        self.price = price
        self.run_script(f'''
        {self.id} = new HorizontalLine(
            {chart.id}, '{self.id}', {price}, '{color}', {width},
            {line_style(style)}, {jbool(axis_label_visible)}, '{text}'
        )''')
        if not func:
            return

        def wrapper(p):
            self.price = float(p)
            func(chart, self)

        async def wrapper_async(p):
            self.price = float(p)
            await func(chart, self)

        self.win.handlers[self.id] = wrapper_async if asyncio.iscoroutinefunction(func) else wrapper
        self.run_script(f'if ("toolBox" in {chart.id}) {chart.id}.toolBox.drawings.push({self.id})')

    def update(self, price):
        """
        Moves the horizontal line to the given price.
        """
        self.run_script(f'{self.id}.updatePrice({price})')
        self.price = price

    def label(self, text: str):
        self.run_script(f'{self.id}.updateLabel("{text}")')

    def delete(self):
        """
        Irreversibly deletes the horizontal line.
        """
        self.run_script(f'{self.id}.deleteLine()')
        del self


class Line(SeriesCommon):
    def __init__(self, chart, name, color, style, width, price_line, price_label, crosshair_marker=True):
        super().__init__(chart)
        self.color = color
        self.name = name
        self.run_script(f'''
        {self.id} = {{
            series: {chart.id}.chart.addLineSeries({{
                color: '{color}',
                lineStyle: {line_style(style)},
                lineWidth: {width},
                lastValueVisible: {jbool(price_label)},
                priceLineVisible: {jbool(price_line)},
                crosshairMarkerVisible: {jbool(crosshair_marker)},
                {"""autoscaleInfoProvider: () => ({
                    priceRange: {
                        minValue: 1_000_000_000,
                        maxValue: 0,
                        },
                    }),""" if chart._scale_candles_only else ''}
                }}),
            markers: [],
            horizontal_lines: [],
            name: '{name}',
            color: '{color}',
            precision: 2,
            }}
        {self._chart.id}.lines.push({self.id})
        if ('legend' in {self._chart.id}) {{
            {self._chart.id}.legend.lines.push({self._chart.id}.legend.makeLineRow({self.id}))
        }}''')

    def set(self, df: pd.DataFrame):
        """
        Sets the line data.\n
        :param df: If the name parameter is not used, the columns should be named: date/time, value.
        """
        if df is None or df.empty:
            self.run_script(f'{self.id}.series.setData([])')
            return
        df = self._df_datetime_format(df, exclude_lowercase=self.name)
        if self.name:
            if self.name not in df:
                raise NameError(f'No column named "{self.name}".')
            df = df.rename(columns={self.name: 'value'})
        self._last_bar = df.iloc[-1]
        self.run_script(f'{self.id}.series.setData({df.to_dict("records")})')

    def update(self, series: pd.Series):
        """
        Updates the line data.\n
        :param series: labels: date/time, value
        """
        series = self._series_datetime_format(series, exclude_lowercase=self.name)
        if self.name in series.index:
            series.rename({self.name: 'value'}, inplace=True)
        self._last_bar = series
        self.run_script(f'{self.id}.series.update({series.to_dict()})')

    def _set_trend(self, start_time, start_value, end_time, end_value, ray=False):
        def time_format(time_val):
            time_val = pd.to_datetime(time_val).timestamp()
            return f"'{time_val}'" if isinstance(time_val, str) else time_val

        self.run_script(f'''
        {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: false}})
        {self.id}.series.setData(
            calculateTrendLine({time_format(start_time)}, {start_value}, {time_format(end_time)}, {end_value},
                                {self._chart._interval.total_seconds() * 1000}, {self._chart.id}, {jbool(ray)}))
        {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: true}})
        ''')

    def delete(self):
        """
        Irreversibly deletes the line, as well as the object that contains the line.
        """
        self._chart._lines.remove(self) if self in self._chart._lines else None
        self.run_script(f'''
            {self._chart.id}.chart.removeSeries({self.id}.series)
            if ('legend' in {self._chart.id}) {{
                {self._chart.id}.legend.lines.forEach(line => {{
                    if (line.line === {self.id}) {self._chart.id}.legend.div.removeChild(line.row)
                }})
            }}
            delete {self.id}
        ''')
        del self


class Candlestick(SeriesCommon):
    def __init__(self, chart: 'AbstractChart'):
        super().__init__(chart)
        self._volume_up_color = 'rgba(83,141,131,0.8)'
        self._volume_down_color = 'rgba(200,127,130,0.8)'

        self.candle_data = pd.DataFrame()

        self.run_script(f'{self.id}.makeCandlestickSeries()')

    def set(self, df: pd.DataFrame = None, render_drawings=False):
        """
        Sets the initial data for the chart.\n
        :param df: columns: date/time, open, high, low, close, volume (if volume enabled).
        :param render_drawings: Re-renders any drawings made through the toolbox. Otherwise, they will be deleted.
        """
        if df is None or df.empty:
            self.run_script(f'{self.id}.series.setData([])')
            self.run_script(f'{self.id}.volumeSeries.setData([])')
            self.candle_data = pd.DataFrame()
            return
        df = self._df_datetime_format(df)
        self.candle_data = df.copy()
        self._last_bar = df.iloc[-1]

        bars = df.to_dict(orient='records')
        self.run_script(f'{self.id}.candleData = {bars}; {self.id}.series.setData({self.id}.candleData)')
        toolbox_action = 'clearDrawings' if not render_drawings else 'renderDrawings'
        self.run_script(f"if ('toolBox' in {self._chart.id}) {self._chart.id}.toolBox.{toolbox_action}()")
        if 'volume' not in df:
            return
        volume = df.drop(columns=['open', 'high', 'low', 'close']).rename(columns={'volume': 'value'})
        volume['color'] = self._volume_down_color
        volume.loc[df['close'] > df['open'], 'color'] = self._volume_up_color
        self.run_script(f'{self.id}.volumeSeries.setData({volume.to_dict(orient="records")})')

        # for line in self._lines:
        #     if line.name in df.columns:
        #         line.set()

    def update(self, series: pd.Series, _from_tick=False):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: labels: date/time, open, high, low, close, volume (if using volume).
        """
        series = self._series_datetime_format(series) if not _from_tick else series
        if series['time'] != self._last_bar['time']:
            self.candle_data.loc[self.candle_data.index[-1]] = self._last_bar
            self.candle_data = pd.concat([self.candle_data, series.to_frame().T], ignore_index=True)
            self._chart.events.new_bar._emit(self)
        self._last_bar = series

        bar = series.to_dict()
        self.run_script(f'''
            if (stampToDate(lastBar({self.id}.candleData).time).getTime() === stampToDate({bar['time']}).getTime()) {{
                {self.id}.candleData[{self.id}.candleData.length-1] = {bar}
            }}
            else {self.id}.candleData.push({bar})
            {self.id}.series.update({bar})
        ''')
        if 'volume' not in series:
            return
        volume = series.drop(['open', 'high', 'low', 'close']).rename({'volume': 'value'})
        volume['color'] = self._volume_up_color if series['close'] > series['open'] else self._volume_down_color
        self.run_script(f'{self.id}.volumeSeries.update({volume.to_dict()})')

    def update_from_tick(self, series: pd.Series, cumulative_volume: bool = False):
        """
        Updates the data from a tick.\n
        :param series: labels: date/time, price, volume (if using volume).
        :param cumulative_volume: Adds the given volume onto the latest bar.
        """
        series = self._series_datetime_format(series)
        bar = pd.Series()
        if series['time'] == self._last_bar['time']:
            bar = self._last_bar
            bar['high'] = max(self._last_bar['high'], series['price'])
            bar['low'] = min(self._last_bar['low'], series['price'])
            bar['close'] = series['price']
            if 'volume' in series:
                if cumulative_volume:
                    bar['volume'] += series['volume']
                else:
                    bar['volume'] = series['volume']
        else:
            for key in ('open', 'high', 'low', 'close'):
                bar[key] = series['price']
            bar['time'] = series['time']
            if 'volume' in series:
                bar['volume'] = series['volume']
        self.update(bar, _from_tick=True)

    def price_scale(
            self, mode: PRICE_SCALE_MODE = 'normal', align_labels: bool = True, border_visible: bool = False,
            border_color: str = None, text_color: str = None, entire_text_only: bool = False,
            ticks_visible: bool = False, scale_margin_top: float = 0.2, scale_margin_bottom: float = 0.2):
        self.run_script(f'''
            {self.id}.series.priceScale().applyOptions({{
                mode: {price_scale_mode(mode)},
                alignLabels: {jbool(align_labels)},
                borderVisible: {jbool(border_visible)},
                {f'borderColor: "{border_color}",' if border_color else ''}
                {f'textColor: "{text_color}",' if text_color else ''}
                entireTextOnly: {jbool(entire_text_only)},
                ticksVisible: {jbool(ticks_visible)},
                scaleMargins: {{top: {scale_margin_top}, bottom: {scale_margin_bottom}}}
            }})''')

    def candle_style(
            self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
            wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
            border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.\n
        If only `up_color` and `down_color` are passed, they will color all parts of the candle.
        """
        if border_enabled:
            border_up_color = border_up_color if border_up_color else up_color
            border_down_color = border_down_color if border_down_color else down_color
        if wick_enabled:
            wick_up_color = wick_up_color if wick_up_color else up_color
            wick_down_color = wick_down_color if wick_down_color else down_color
        self.run_script(f"""
        {self.id}.series.applyOptions({{
            upColor: "{up_color}",
            downColor: "{down_color}",
            wickVisible: {jbool(wick_enabled)},
            borderVisible: {jbool(border_enabled)},
            {f'borderUpColor: "{border_up_color}",' if border_enabled else ''}
            {f'borderDownColor: "{border_down_color}",' if border_enabled else ''}
            {f'wickUpColor: "{wick_up_color}",' if wick_enabled else ''}
            {f'wickDownColor: "{wick_down_color}",' if wick_enabled else ''}
        }})""")

    def volume_config(self, scale_margin_top: float = 0.8, scale_margin_bottom: float = 0.0,
                      up_color='rgba(83,141,131,0.8)', down_color='rgba(200,127,130,0.8)'):
        """
        Configure volume settings.\n
        Numbers for scaling must be greater than 0 and less than 1.\n
        Volume colors must be applied prior to setting/updating the bars.\n
        """
        self._volume_up_color = up_color if up_color else self._volume_up_color
        self._volume_down_color = down_color if down_color else self._volume_down_color
        self.run_script(f'''
        {self.id}.volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
            top: {scale_margin_top},
            bottom: {scale_margin_bottom},
            }}
        }})''')


class AbstractChart(Candlestick, Pane):
    def __init__(self, window: Window, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, toolbox: bool = False,
                 autosize: bool = True, position: FLOAT = 'left'):
        Pane.__init__(self, window)

        self._lines = []
        self._scale_candles_only = scale_candles_only
        self.events: Events = Events(self)

        from lightweight_charts.polygon import PolygonAPI
        self.polygon: PolygonAPI = PolygonAPI(self)

        self.run_script(
            f'{self.id} = new Chart("{self.id}", {inner_width}, {inner_height}, "{position}", {jbool(autosize)})')

        Candlestick.__init__(self, self)

        self.topbar: TopBar = TopBar(self)
        if toolbox:
            self.toolbox: ToolBox = ToolBox(self)

    def fit(self):
        """
        Fits the maximum amount of the chart data within the viewport.
        """
        self.run_script(f'{self.id}.chart.timeScale().fitContent()')

    def create_line(
            self, name: str = '', color: str = 'rgba(214, 237, 255, 0.6)',
            style: LINE_STYLE = 'solid', width: int = 2,
            price_line: bool = True, price_label: bool = True
    ) -> Line:
        """
        Creates and returns a Line object.)\n
        """
        self._lines.append(Line(self, name, color, style, width, price_line, price_label))
        return self._lines[-1]

    def lines(self) -> List[Line]:
        """
        Returns all lines for the chart.
        """
        return self._lines.copy()

    def trend_line(self, start_time: TIME, start_value: NUM, end_time: TIME, end_value: NUM,
                   color: str = '#1E80F0', width: int = 2
                   ) -> Line:
        line = Line(self, '', color, 'solid', width, False, False, False)
        line._set_trend(start_time, start_value, end_time, end_value)
        return line

    def ray_line(self, start_time: TIME, value: NUM,
                 color: str = '#1E80F0', width: int = 2
                 ) -> Line:
        line = Line(self, '', color, 'solid', width, False, False, False)
        line._set_trend(start_time, value, start_time, value, ray=True)
        return line

    def time_scale(self, right_offset: int = 0, min_bar_spacing: float = 0.5,
                   visible: bool = True, time_visible: bool = True, seconds_visible: bool = False,
                   border_visible: bool = True, border_color: str = None):
        """
        Options for the timescale of the chart.
        """
        self.run_script(f'''
               {self.id}.chart.applyOptions({{
                   timeScale: {{
                       rightOffset: {right_offset},
                       minBarSpacing: {min_bar_spacing},
                       visible: {jbool(visible)},
                       timeVisible: {jbool(time_visible)},
                       secondsVisible: {jbool(seconds_visible)},
                       borderVisible: {jbool(border_visible)},
                       {f'borderColor: "{border_color}",' if border_color else ''}
                   }}
               }})''')

    def layout(self, background_color: str = '#000000', text_color: str = None,
               font_size: int = None, font_family: str = None):
        """
        Global layout options for the chart.
        """
        self.run_script(f"""
        document.getElementById('wrapper').style.backgroundColor = '{background_color}'
        {self.id}.chart.applyOptions({{
        layout: {{
            background: {{color: "{background_color}"}},
            {f'textColor: "{text_color}",' if text_color else ''}
            {f'fontSize: {font_size},' if font_size else ''}
            {f'fontFamily: "{font_family}",' if font_family else ''}
        }}}})""")

    def grid(self, vert_enabled: bool = True, horz_enabled: bool = True,
             color: str = 'rgba(29, 30, 38, 5)', style: LINE_STYLE = 'solid'):
        """
        Grid styling for the chart.
        """
        self.run_script(f"""
           {self.id}.chart.applyOptions({{
           grid: {{
               vertLines: {{
                   visible: {jbool(vert_enabled)},
                   color: "{color}",
                   style: {line_style(style)},
               }},
               horzLines: {{
                   visible: {jbool(horz_enabled)},
                   color: "{color}",
                   style: {line_style(style)},
               }},
           }}
           }})""")

    def crosshair(self, mode: CROSSHAIR_MODE = 'normal', vert_visible: bool = True,
                  vert_width: int = 1, vert_color: str = None, vert_style: LINE_STYLE = 'large_dashed',
                  vert_label_background_color: str = 'rgb(46, 46, 46)', horz_visible: bool = True,
                  horz_width: int = 1, horz_color: str = None, horz_style: LINE_STYLE = 'large_dashed',
                  horz_label_background_color: str = 'rgb(55, 55, 55)'):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        self.run_script(f'''
        {self.id}.chart.applyOptions({{
            crosshair: {{
                mode: {crosshair_mode(mode)},
                vertLine: {{
                    visible: {jbool(vert_visible)},
                    width: {vert_width},
                    {f'color: "{vert_color}",' if vert_color else ''}
                    style: {line_style(vert_style)},
                    labelBackgroundColor: "{vert_label_background_color}"
                }},
                horzLine: {{
                    visible: {jbool(horz_visible)},
                    width: {horz_width},
                    {f'color: "{horz_color}",' if horz_color else ''}
                    style: {line_style(horz_style)},
                    labelBackgroundColor: "{horz_label_background_color}"
                }}
            }}}})''')

    def watermark(self, text: str, font_size: int = 44, color: str = 'rgba(180, 180, 200, 0.5)'):
        """
        Adds a watermark to the chart.
        """
        self.run_script(f'''
          {self.id}.chart.applyOptions({{
              watermark: {{
                  visible: true,
                  fontSize: {font_size},
                  horzAlign: 'center',
                  vertAlign: 'center',
                  color: '{color}',
                  text: '{text}',
              }}
          }})''')

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, lines: bool = True,
               color: str = 'rgb(191, 195, 203)', font_size: int = 11, font_family: str = 'Monaco'):
        """
        Configures the legend of the chart.
        """
        if not visible:
            return
        self.run_script(f'''
        {self.id}.legend = new Legend(  {self.id}, {jbool(ohlc)}, {jbool(percent)}, {jbool(lines)},
                                        '{color}', {font_size}, '{font_family}')
        ''')

    def spinner(self, visible):
        self.run_script(f"{self.id}.spinner.style.display = '{'block' if visible else 'none'}'")

    def hotkey(self, modifier_key: Literal['ctrl', 'alt', 'shift', 'meta'],
               keys: Union[str, tuple, int], func: callable):
        if not isinstance(keys, tuple):
            keys = (keys,)
        for key in keys:
            key_code = 'Key' + key.upper() if isinstance(key, str) else 'Digit' + str(key)
            self.run_script(f'''
            {self.id}.commandFunctions.unshift((event) => {{
                if (event.{modifier_key + 'Key'} && event.code === '{key_code}') {{
                    event.preventDefault()
                    window.callbackFunction(`{modifier_key, keys}_~_{key}`)
                    return true
                }}
                else return false
            }})''')
        self.win.handlers[f'{modifier_key, keys}'] = func

    def create_table(self, width: NUM, height: NUM,
                     headings: tuple, widths: tuple = None, alignments: tuple = None,
                     position: FLOAT = 'left', draggable: bool = False, func: callable = None
                     ) -> Table:
        return self.win.create_table(width, height, headings, widths, alignments, position, draggable, func)

    def create_subchart(self, position: FLOAT = 'left', width: float = 0.5, height: float = 0.5,
                        sync: Union[str, bool] = None, scale_candles_only: bool = False,
                        toolbox: bool = False) -> 'AbstractChart':
        if sync is True:
            sync = self.id
        return self.win.create_subchart(position, width, height, sync, scale_candles_only, toolbox)
