# importing the modules
import pandas as pd
import datetime
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import HoverTool, ColumnDataSource, BooleanFilter, CDSView, Range1d, Span
from bokeh.models.callbacks import CustomJS

output_file("bokeh_html/nchart.html")


class n_chart:

    def __init__(self, trade):
        self.trade = trade
        self.width = 1200
        self.toolbar_location = "left"
        self.tools = "xpan,xwheel_zoom,reset"
        self.y_axis_location = "right"

        self.red = "#ff3333"
        self.green = "#078F12"
        self.blue = "#0E4EAD"
        self.orange = "#ff9100"
        self.gray = "#ededed"
        self.gray2 = "#888888"
        self.black = "#333333"

        self.min_border_left = 20
        self.min_border_right = 20
        self.min_border_top = 15
        self.min_border_bottom = 0

        self.elements = list()

    def fit(self, i_df, name, indecators=""):
        i_df = i_df.reset_index(drop=True)
        # i_df, nemhasznal = self.trade.time_filter(i_df, "15:30", "22:00")
        # i_df = nddfx_intime.reset_index()
        # print(i_df)
        i_df['Date_str'] = i_df['Date'].astype(str)
        self.elements = list()
        self.elements.append(self.chart_candlestick(i_df, name))
        self.elements.append(self.chart_vol(i_df, name))
        if len(indecators) > 0:
            if 'P10' in indecators:
                self.elements.append(self.chart_p10(i_df, "P10"))
            if 'P10INT' in indecators:
                self.elements.append(self.chart_p10int(i_df, "P10INT"))
            if 'VWAP' in indecators:
                self.elements.append(self.chart_vwap(i_df, "VWAP"))
            if 'MT' in indecators:
                self.elements.append(self.chart_mt(i_df, "MAGIC TREND"))
            if 'GAM' in indecators:
                self.elements.append(self.chart_gam(i_df, "GAM"))
            if 'GAM2' in indecators:
                self.elements.append(self.chart_gam2(i_df, "GAM2"))
            if 'BREAKOUT' in indecators:
                self.elements.append(self.chart_breakout(i_df, "BREAKOUT"))
            if 'CCI21' in indecators:
                self.elements.append(self.chart_cci_21(i_df, "CCI21"))
            if 'SMA30' in indecators:
                self.elements.append(self.chart_sma_30(i_df, "SMA30"))
            if 'SMA60' in indecators:
                self.elements.append(self.chart_sma_60(i_df, "SMA60"))
            if 'SMA5813' in indecators:
                self.elements.append(self.chart_sma5813(i_df, "SMA5813"))
            if 'ICHIMOKU' in indecators:
                self.elements.append(self.chart_ichimoku(i_df, "ICHIMOKU"))
            if 'ADX8' in indecators:
                self.elements.append(self.chart_adx(i_df, "ADX8"))
            if 'RSI14' in indecators:
                self.elements.append(self.chart_rsi(i_df, "RSI14"))
            if 'MACD' in indecators:
                self.elements.append(self.chart_macd(i_df, "MACD"))

    def show(self):

        # x_range összekapcsolása
        for i, e in enumerate(self.elements):
            if i == 0:
                # e.y_range = DataRange1d(only_visible=True)
                e.xaxis.visible = False
            elif i == 1:
                e.x_range = self.elements[0].x_range
                # e.y_range = self.elements[0].y_range
                e.xaxis.visible = False
                e.min_border_top = 0
            else:
                if e.title.text != "ADX8" and \
                        e.title.text != "RSI14" and \
                        e.title.text != "P10" and \
                        e.title.text != "MACD" and \
                        e.title.text != "CCI21":
                    # ADX* és RSI14 nél nem kell összzárni a y rangeotmert az nem egyezik a részvény árfolyammal
                    e.y_range = self.elements[0].y_range
                e.xaxis.visible = False
                e.x_range = self.elements[0].x_range

        self.elements[1].xaxis.visible = True
        i_last = len(self.elements)-1
        if i_last > 1:
            i_bottom_padding = 250
            i_heigh = self.elements[i_last].plot_height
            self.elements[i_last].plot_height = i_heigh + i_bottom_padding
            self.elements[i_last].min_border_bottom = i_bottom_padding

        plots = []
        for e in self.elements:
            plots.append(e)
        c = column(self.elements)
        show(c)

    def chart_candlestick(self, df, name):

        stock = ColumnDataSource(df)

        p = figure(sizing_mode='fixed',
                   tools=self.tools,
                   active_drag='xpan',
                   active_scroll='xwheel_zoom',
                   x_axis_type='datetime',
                   toolbar_location=self.toolbar_location,
                   plot_width=self.width,
                   plot_height=250,
                   y_axis_location=self.y_axis_location,
                   title=name,
                   )

        # p.extra_y_ranges = {"foo": Range1d(start=1, end=9)}

        inc = df['Open'] >= df['Close']
        inc = tuple(inc)
        dec = df['Open'] < df['Close']
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        p.segment(x0='index', x1='index', y0='Low', y1='High', color=self.red, source=stock, view=view_inc)
        p.segment(x0='index', x1='index', y0='Low', y1='High', color=self.green, source=stock, view=view_dec)

        p.vbar(x='index', width=0.7, top='Open', bottom='Close', fill_color=self.red, line_color=self.red,
               source=stock, view=view_inc, name="price")
        p.vbar(x='index', width=0.7, top='Open', bottom='Close', fill_color=self.green, line_color=self.green,
               source=stock, view=view_dec, name="price", legend_label=name)

        p.line('index', 'ohlc4', color=self.black, source=stock)


        # # xaxis labell   ---------------------------------------------------------------------------------------
        # label_dic = {}
        #
        # for i_i, i_date in enumerate(tuple(df['Date'])):
        #     # print(i_date.day)
        #     # dt_obj = datetime.datetime.strptime(i_date, '%Y-%m-%d %H:%M:%S')
        #
        #     label_dic[i_i] = f"{i_date.month}/{i_date.day} {i_date.hour}:{i_date.minute}"
        #
        # p.xaxis.major_label_overrides = label_dic
        # p.x_range.range_padding = 60
        # p.xaxis.ticker.desired_num_ticks = 60
        # p.xaxis.major_label_orientation = 3.14 / 4

        # végére rázúmmol  -------------------------------------------------------------------------------
        df_end = df.shape[0]
        df_start = df_end - 65
        desired_range = (df_start, df_end)
        p.x_range = Range1d(*desired_range)
        i_max = df['High'][df_start:df_end].max()
        i_min = df['Low'][df_start:df_end].min()
        i_pad = (i_max - i_min) * .3
        desired_range2 = (i_min - i_pad, i_max + i_pad)
        p.y_range = Range1d(*desired_range2)
        p.legend.visible = False

        # hover ----------------------------------------------------------------------------
        p.add_tools(HoverTool(

            tooltips=[("Date", "@Date_str"),
                                ("Low, High", "@Low{$0,0.00}, @High{$0,0.00}"),
                                ("Open, Close", "@Open{$0,0.00}, @Close{$0,0.00}"),
                                ("ohlc4", "@ohlc4{$0,0.00}"),
                                ("Volume", "@Volume{($ 0.00 a)}")],

            # formatters={"Date": 'datetime'},


            mode='vline'
        ))

        # start default settings
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 0
        p.outline_line_alpha = 0
        p.outline_line_color = "#ffffff"
        # end default settings
        p.yaxis.axis_label = 'Price (in USD)'

        callback = CustomJS(args=dict(p=p), code="""
        clearTimeout(window._autoscale_timeout);
        var cv_price = cb_obj.plots[0].renderers[0].data_source.data.ohlc4;
        var x_start = p.x_range.start;
        var x_end = p.x_range.end;
        var x_start_int = Math.floor(x_start);
        var x_end_int = Math.floor(x_end);
        x_start_int = Math.max(x_start_int, 1);

        var cv_price_slice = cv_price.slice(x_start_int,x_end_int);
        var cv_max = Math.max(...cv_price_slice);
        var cv_min = Math.min(...cv_price_slice);
        window._autoscale_timeout = setTimeout(function() {
            p.y_range.start = cv_min * .993;
            p.y_range.end = cv_max * 1.005;
        });
        """)

        p.x_range.js_on_change('start', callback)
        return p

    def chart_vol(self, df, name):

        i_cut = df['Volume'].mean() * 3
        df.loc[df.Volume > i_cut, 'Volume'] = i_cut * 1.1
        stock = ColumnDataSource(df)
        # i_max = max(df['Volume'].max(),1000)
        p = figure(sizing_mode='fixed',
                   tools=self.tools,
                   active_drag='xpan',
                   active_scroll='xwheel_zoom',
                   x_axis_type='datetime',
                   toolbar_location=self.toolbar_location,
                   plot_width=self.width,
                   plot_height=150,
                   y_axis_location=self.y_axis_location,
                   background_fill_color=self.gray,
                   title="VOLUME"
                   # y_axis_type="log",
                   # y_range=[0, 200000]
                   )
        p.xgrid.grid_line_color = "#cccccc"
        p.xgrid.grid_line_alpha = 1
        p.ygrid.grid_line_color = "#cccccc"
        p.ygrid.grid_line_alpha = 0
        p.outline_line_width = 0
        p.outline_line_alpha = 0
        p.outline_line_color = "#ffffff"

        # xaxis labell   ---------------------------------------------------------------------------------------
        label_dic = {}
        for i_i, i_date in enumerate(tuple(df['Date'])):
            label_dic[i_i] = f"{i_date.month}/{i_date.day} {i_date.hour}:{i_date.minute}"

        p.xaxis.major_label_overrides = label_dic
        p.x_range.range_padding = 60
        p.xaxis.ticker.desired_num_ticks = 60
        p.xaxis.major_label_orientation = 3.14 / 4

        inc = df['Open'] > df['Close']
        inc = tuple(inc)
        dec = df['Open'] < df['Close']
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        p.vbar(x='index', width=.5,  top="Volume", bottom=0, fill_color=self.red, line_color=self.red,
               source=stock, view=view_inc, name="price", fill_alpha=0.5, line_width=0)
        p.vbar(x='index', width=.5, top="Volume", bottom=0, fill_color=self.green, line_color=self.green,
               source=stock, view=view_dec, name="price", legend_label=name, fill_alpha=0.5, line_width=0)



        # hover ----------------------------------------------------------------------------
        p.add_tools(HoverTool(
            tooltips=[("Datetime", "@Date"), ("Volume", "@Volume{($ 0.00 a)}")],
            formatters={"Date": 'datetime'},
            mode='vline'
        ))

        # start default settings
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        # end default settings
        p.legend.visible = False
        p.title.visible = False
        return p

    def chart_sma_30(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        p.line('index', 'SMA_30', color=self.green, legend_label="SMA_30", source=stock)
        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_vwap(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        p.line('index', 'VWAP_D', color=self.green, legend_label="VWAP_D", source=stock)
        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_sma_60(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        p.line('index', 'SMA_60', color=self.green, legend_label="SMA_60", source=stock)
        p.legend.visible = False

        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_ichimoku(self, df, name):

        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=200,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        inc = df['ISA_9'] > df['ISB_26']
        inc = tuple(inc)
        dec = df['ISA_9'] < df['ISB_26']
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        p.varea('index', 'ISA_9', 'ISB_26',
                color=self.green,
                alpha=0.2,
                # hatch_alpha=ha,
                source=stock)
        p.vbar(x='index', width=1, top='ISA_9', bottom='ISB_26', fill_color=self.green, line_color=self.green,
               source=stock, view=view_inc, name="price", fill_alpha=0.5, line_width=0)
        p.vbar(x='index', width=1, top='ISA_9', bottom='ISB_26', fill_color=self.red, line_color=self.red,
               source=stock, view=view_dec, name="price", fill_alpha=0.5, line_width=0)

        p.line('index', 'ITS_9', color=self.orange, line_width=2, legend_label="Conversion Line", source=stock)
        p.line('index', 'IKS_26', color=self.black, line_width=3, legend_label="Base Line", source=stock)
        p.line('index', 'ICS_26', color=self.green, line_width=1, source=stock, alpha=0.5)


        # sig = tuple(df['SIG_ICHI_LONG_ALL'])
        # view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        # p.circle('index', 'ohlc4', color=self.green, size=5, source=stock, view=view_sig)

        # sig = tuple(df['SIG_ICHI_LONG_FIRST'])
        # view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        # p.triangle('index', 'ohlc4', color=self.green, size=15, source=stock, view=view_sig)

        df['SIG_QFY_ICHI_LONG'] = df['SIG_ICHIMOKU'] == 0
        sig = tuple(df['SIG_QFY_ICHI_LONG'])
        view_sig_qty = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.triangle('index', 'ohlc4', line_color=self.green, line_width=2, fill_color=self.green, size=15, source=stock, view=view_sig_qty)


        # sig = tuple(df['SIG_ICHI_SHORT_ALL'])
        # view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        # p.circle('index', 'ohlc4', color=self.red, size=5, source=stock, view=view_sig)

        # sig = tuple(df['SIG_ICHI_SHORT_FIRST'])
        # view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        # p.triangle('index', 'ohlc4', color=self.red, size=15, source=stock, view=view_sig)

        df['SIG_QFY_ICHI_SHORT'] = df['SIG_ICHIMOKU'] == 1
        sig = tuple(df['SIG_QFY_ICHI_SHORT'])
        view_sig_qty = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.inverted_triangle('index', 'ohlc4', line_color=self.red, line_width=2, fill_color=self.red, size=15, source=stock, view=view_sig_qty)

        if "y_ICHIMOKU" in df.columns:
            print("y")
            df['Y_LONG'] = df['y_ICHIMOKU'] == 0
            sig = tuple(df['Y_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4', line_color=self.orange, line_width=3, fill_color=self.green, size=16,
                       source=stock, view=view_sig)
    
            df['Y_SHORT'] = df['y_ICHIMOKU'] == 1
            sig = tuple(df['Y_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4', line_color=self.orange, line_width=3, fill_color=self.red, size=16,
                                source=stock, view=view_sig)

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_adx(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        # p.line('index', 'ADX_8', color=self.black, legend_label="ADX_8", source=stock, line_width=2)
        # p.line('index', 'DMP_8', color=self.green, legend_label="DI+", source=stock)
        # p.line('index', 'DMN_8', color=self.red, legend_label="DI-", source=stock)
        # # Vertical line
        vline1 = Span(location=20, dimension='width', line_color=self.black, line_width=1)
        vline2 = Span(location=0, dimension='width', line_color=self.black, line_width=2)
        vline3 = Span(location=-20, dimension='width', line_color=self.black, line_width=1)
        p.renderers.extend([vline1])
        p.renderers.extend([vline2])
        p.renderers.extend([vline3])

        inc = df['DMN_8'] < df['DMP_8']
        inc = tuple(inc)
        dec = df['DMN_8'] > df['DMP_8']
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])


        p.vbar(x='index', width=0.7, top='ADX_8_ONE', bottom=0, fill_color=self.red, line_color=self.red,
               source=stock, view=view_dec, name="ADX_8")
        p.vbar(x='index', width=0.7, top='ADX_8_ONE', bottom=0, fill_color=self.green, line_color=self.green,
               source=stock, view=view_inc, name="ADX_8", legend_label=name)

        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------

        i_max = df['ADX_8_ONE'].max()
        i_min = df['ADX_8_ONE'].min()
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p


    def chart_p10(self, df, name):
        df['ohlc4_up'] = -20
        df['ohlc4_down'] = 20
        stock = ColumnDataSource(df)

        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        # p.line('index', 'ADX_8', color=self.black, legend_label="ADX_8", source=stock, line_width=2)
        # p.line('index', 'DMP_8', color=self.green, legend_label="DI+", source=stock)
        # p.line('index', 'DMN_8', color=self.red, legend_label="DI-", source=stock)
        # # Vertical line
        # vline1 = Span(location=20, dimension='width', line_color=self.black, line_width=1)
        # vline2 = Span(location=0, dimension='width', line_color=self.black, line_width=2)
        # vline3 = Span(location=-20, dimension='width', line_color=self.black, line_width=1)
        # p.renderers.extend([vline1])
        # p.renderers.extend([vline2])
        # p.renderers.extend([vline3])

        inc = df['y_P10'] > 0
        inc = tuple(inc)
        dec = df['SIG_P10'] < 0
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        p.vbar(x='index', width=0.7, top='SIG_P10', bottom=0, fill_color=self.red, line_color=self.red,
               source=stock, view=view_dec, name="SIG_P10")
        p.vbar(x='index', width=0.7, top='SIG_P10', bottom=0, fill_color=self.green, line_color=self.green,
               source=stock, view=view_inc, name="SIG_P10", legend_label=name)

        if "y_P10" in df.columns:
            df['x1'] = df['y_P10'] == 0
            sig = tuple(df['x1'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_width=0, fill_color=self.green, size=15, source=stock, view=view_sig)
    
            df['x2'] = df['y_P10'] == 1
            sig = tuple(df['x2'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_width=0, fill_color=self.red, size=15, source=stock,
                                view=view_sig)
    
            df['x3'] = df['y_P10'] == 2
            sig = tuple(df['x3'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_width=0, fill_color=self.gray2, size=15, source=stock, view=view_sig)
            #
            # df['x4'] = df['y_P10'] == 3
            # sig = tuple(df['x4'])
            # view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            # p.inverted_triangle('index', 'ohlc4_down', line_width=0, fill_color=self.gray2, size=15, source=stock,
            #                     view=view_sig)

        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------

        i_max = 100
        i_min = -100
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p

    def chart_p10int(self, df, name):
        df['ohlc4_up'] = -20
        df['ohlc4_down'] = 20
        stock = ColumnDataSource(df)

        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=200,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        # p.line('index', 'ADX_8', color=self.black, legend_label="ADX_8", source=stock, line_width=2)
        # p.line('index', 'DMP_8', color=self.green, legend_label="DI+", source=stock)
        # p.line('index', 'DMN_8', color=self.red, legend_label="DI-", source=stock)
        # # Vertical line
        # vline1 = Span(location=20, dimension='width', line_color=self.black, line_width=1)
        # vline2 = Span(location=0, dimension='width', line_color=self.black, line_width=2)
        # vline3 = Span(location=-20, dimension='width', line_color=self.black, line_width=1)
        # p.renderers.extend([vline1])
        # p.renderers.extend([vline2])
        # p.renderers.extend([vline3])


        inc = df['Open'] >= df['Close']
        # inc = tuple(inc)
        dec = df['Open'] < df['Close']
        # dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        p.line('index', 'ohlc4', color=self.black, source=stock)

        # p.segment(x0='index', x1='index', y0='Low', y1='High', color=self.red, source=stock, view=view_inc)
        # p.segment(x0='index', x1='index', y0='Low', y1='High', color=self.green, source=stock, view=view_dec)
        #
        # p.vbar(x='index', width=0.7, top='Open', bottom='Close', fill_color=self.red, line_color=self.red,
        #        source=stock, view=view_inc, name="price", fill_alpha=.5)
        # p.vbar(x='index', width=0.7, top='Open', bottom='Close', fill_color=self.green, line_color=self.green,
        #        source=stock, view=view_dec, name="price", legend_label=name, fill_alpha=.5)

        if "y_P10INT" in df.columns:

            inc = df['y_P10INT'] == 1
            inc = tuple(inc)
            dec = df['y_P10INT'] == 2
            dec = tuple(dec)
            zer = df['y_P10INT'] == 0
            zer = tuple(zer)

            view_long = CDSView(source=stock, filters=[BooleanFilter(inc)])
            view_short = CDSView(source=stock, filters=[BooleanFilter(dec)])
            view_zer = CDSView(source=stock, filters=[BooleanFilter(zer)])

            p.triangle('index', 'ohlc4', line_width=0, fill_color=self.green,
                       size=15, source=stock, legend_label="long y", view=view_long)
            p.inverted_triangle('index', 'ohlc4', line_width=0, fill_color=self.red,
                       size=15, source=stock, legend_label="short y", view=view_short)
            p.circle('index', 'ohlc4', line_width=0, fill_color=self.black,
                     size=4, source=stock, legend_label="neutral sig", view=view_zer)

            # inc = df['SIG_P10INT'] == 1
            # inc = tuple(inc)
            # dec = df['SIG_P10INT'] == 2
            # dec = tuple(dec)
            # zer = df['SIG_P10INT'] == 0
            # zer = tuple(zer)

            # view_long_sig = CDSView(source=stock, filters=[BooleanFilter(inc)])
            # view_short_sig = CDSView(source=stock, filters=[BooleanFilter(dec)])
            # view_zer = CDSView(source=stock, filters=[BooleanFilter(zer)])
            #
            # p.circle('index', 'ohlc4', line_width=0, fill_color=self.green,
            #            size=8, source=stock, legend_label="long sig", view=view_long_sig)
            # p.circle('index', 'ohlc4', line_width=0, fill_color=self.red,
            #            size=8, source=stock, legend_label="short sig", view=view_short_sig)
            #
            # p.circle('index', 'ohlc4', line_width=0, fill_color=self.black,
            #            size=4, source=stock, legend_label="neutral sig", view=view_zer)


        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------

        i_max = 100
        i_min = -100
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p

    def chart_cci_21(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        # p.line('index', 'ADX_8', color=self.black, legend_label="ADX_8", source=stock, line_width=2)
        # p.line('index', 'DMP_8', color=self.green, legend_label="DI+", source=stock)
        # p.line('index', 'DMN_8', color=self.red, legend_label="DI-", source=stock)
        # # Vertical line
        vline0 = Span(location=200, dimension='width', line_color=self.black, line_width=1)
        vline1 = Span(location=100, dimension='width', line_color=self.black, line_width=1)
        vline2 = Span(location=0, dimension='width', line_color=self.black, line_width=2)
        vline3 = Span(location=-100, dimension='width', line_color=self.black, line_width=1)
        vline4 = Span(location=-200, dimension='width', line_color=self.black, line_width=1)
        p.renderers.extend([vline0])
        p.renderers.extend([vline1])
        p.renderers.extend([vline2])
        p.renderers.extend([vline3])
        p.renderers.extend([vline4])

        p.line('index', 'CCI_21_0.015', color=self.black, legend_label="cci21", source=stock)
        p.legend.visible = True

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        
        i_max = 220
        i_min = -220
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p

    def chart_macd(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        # p.line('index', 'ADX_8', color=self.black, legend_label="ADX_8", source=stock, line_width=2)
        # p.line('index', 'DMP_8', color=self.green, legend_label="DI+", source=stock)
        # p.line('index', 'DMN_8', color=self.red, legend_label="DI-", source=stock)
        # # Vertical line

        # vline1 = Span(location=20, dimension='width', line_color=self.black, line_width=1)
        # vline2 = Span(location=0, dimension='width', line_color=self.black, line_width=2)
        # vline3 = Span(location=-20, dimension='width', line_color=self.black, line_width=1)
        # p.renderers.extend([vline1])
        # p.renderers.extend([vline2])
        # p.renderers.extend([vline3])

        inc = df['MACDh_12_26_9'] > 0
        inc = tuple(inc)
        dec = df['MACDh_12_26_9'] < 0
        dec = tuple(dec)

        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])


        p.vbar(x='index', width=0.7, top='MACDh_12_26_9', bottom=0, fill_color=self.red, line_color=self.red,
               source=stock, view=view_dec, name="MACD")
        p.vbar(x='index', width=0.7, top='MACDh_12_26_9', bottom=0, fill_color=self.green, line_color=self.green,
               source=stock, view=view_inc, name="MACD", legend_label=name)

        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------

        i_max = df['MACDh_12_26_9'].max()
        i_min = df['MACDh_12_26_9'].min()
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p

    def chart_rsi(self, df, name):
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=150,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        vline1 = Span(location=20, dimension='width', line_color=self.black, line_width=1)
        vline2 = Span(location=80, dimension='width', line_color=self.black, line_width=1)
        p.renderers.extend([vline1])
        p.renderers.extend([vline2])

        p.line('index', 'RSI_14', color=self.blue, source=stock, legend_label=name)

        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------

        i_max = df['RSI_14'].max()
        i_min = df['RSI_14'].min()
        desired_range2 = (i_min, i_max)
        p.y_range = Range1d(*desired_range2)
        return p

    def chart_sma5813(self, df, name):
        df['ohlc4_up'] = df['ohlc4'] * 1.003
        df['ohlc4_down'] = df['ohlc4'] * 0.997
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=220,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        p.line('index', 'SMA_5', color=self.green, legend_label="SMA_5", line_width=1, source=stock)
        p.line('index', 'SMA_8', color=self.orange, legend_label="SMA_8", line_width=2, source=stock)
        p.line('index', 'SMA_13', color=self.red, legend_label="SMA_13", line_width=3, source=stock)

        df['SIG_SMA5813_LONG_ALL_FIRST'] = df['SIG_SMA5813'] == 0
        sig = tuple(df['SIG_SMA5813_LONG_ALL_FIRST'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.green, size=5, source=stock, view=view_sig)

        df['SIG_SMA5813_SHORT_ALL_FIRST'] = df['SIG_SMA5813'] == 1
        sig = tuple(df['SIG_SMA5813_SHORT_ALL_FIRST'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.red, size=5, source=stock, view=view_sig)

        if "y_SMA5813" in df.columns:
            df['SIG_QFY_BREAKOUT_GOOD_LONG'] = df['y_SMA5813'] == 0
            sig = tuple(df['SIG_QFY_BREAKOUT_GOOD_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_width=0, fill_color=self.green, size=15, source=stock, view=view_sig)
    
            df['SIG_QFY_SMA5813_GOOD_SHORT'] = df['y_SMA5813'] == 1
            sig = tuple(df['SIG_QFY_SMA5813_GOOD_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_width=0, fill_color=self.red, size=15, source=stock, view=view_sig)
    
            df['SIG_QFY_SMA5813_BAD_LONG'] = df['y_SMA5813'] == 2
            sig = tuple(df['SIG_QFY_SMA5813_BAD_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_width=0, fill_color=self.gray2, size=15, source=stock, view=view_sig)
    
            df['SIG_QFY_SMA5813_BAD_SHORT'] = df['y_SMA5813'] == 3
            sig = tuple(df['SIG_QFY_SMA5813_BAD_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_width=0, fill_color=self.gray2, size=15, source=stock, view=view_sig)

        p.legend.visible = False

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_gam(self, df, name):
        df['ohlc4_up'] = df['ohlc4'] * 1.003
        df['ohlc4_down'] = df['ohlc4'] * 0.997
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=220,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        if 'y_GAM' in df.columns:
            df['SIG_QFY_LONG'] = df['y_GAM'] == 0
            sig = tuple(df['SIG_QFY_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_color=self.orange, line_width=3, fill_color=self.green, size=15, source=stock, view=view_sig)

            df['SIG_QFY_SHORT'] = df['y_GAM'] == 1
            sig = tuple(df['SIG_QFY_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_color=self.orange, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)

        p.legend.visible = False
        p.add_tools(HoverTool(

            tooltips=[("Date", "@Date_str"),
                                ("ohlc4", "@ohlc4{$0,0.00}"),
                                ("Volume", "@Volume{($ 0.00 a)}")],

            mode='vline'
        ))

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

    def chart_gam2(self, df, name):
        df['ohlc4_up'] = df['ohlc4'] * 1.003
        df['ohlc4_down'] = df['ohlc4'] * 0.997
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=220,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        if 'y_GAM2' in df.columns:
            df['SIG_QFY_LONG'] = df['y_GAM2'] == 0
            sig = tuple(df['SIG_QFY_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_color=self.orange, line_width=3, fill_color=self.green, size=15, source=stock, view=view_sig)

            df['SIG_QFY_SHORT'] = df['y_GAM2'] == 1
            sig = tuple(df['SIG_QFY_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_color=self.orange, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)
            
            df['x3'] = df['y_GAM2'] == 2
            sig = tuple(df['x3'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_width=0, fill_color=self.gray2, size=15, source=stock, view=view_sig)


        p.legend.visible = False
        p.add_tools(HoverTool(

            tooltips=[("Date", "@Date_str"),
                                ("ohlc4", "@ohlc4{$0,0.00}"),
                                ("Volume", "@Volume{($ 0.00 a)}")],

            mode='vline'
        ))

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p


    def chart_breakout(self, df, name):
        df['ohlc4_up'] = df['ohlc4'] * 1.003
        df['ohlc4_down'] = df['ohlc4'] * 0.997
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=220,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        # print ohlc4 price
        p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        p.line('index', 'ohlc4', color=self.blue, source=stock)

        df['SIG_BREAKOUT_LONG_ALL'] = df['SIG_BREAKOUT'] == 0
        sig = tuple(df['SIG_BREAKOUT_LONG_ALL'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.green, size=5, source=stock, view=view_sig)

        df['SIG_BREAKOUT_SHORT_ALL'] = df['SIG_BREAKOUT'] == 1
        sig = tuple(df['SIG_BREAKOUT_SHORT_ALL'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.red, size=5, source=stock, view=view_sig)


        if 'y_BREAKOUT' in df.columns:
            df['SIG_QFY_BREAKOUT_GOOD_LONG'] = df['y_BREAKOUT'] == 0
            sig = tuple(df['SIG_QFY_BREAKOUT_GOOD_LONG'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_up', line_color=self.orange, line_width=3, fill_color=self.green, size=15, source=stock, view=view_sig)

            df['SIG_QFY_BREAKOUT_GOOD_SHORT'] = df['y_BREAKOUT'] == 1
            sig = tuple(df['SIG_QFY_BREAKOUT_GOOD_SHORT'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_color=self.orange, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)

            df['SIG_QFY_X1'] = df['y_BREAKOUT'] == 2
            sig = tuple(df['SIG_QFY_X1'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.triangle('index', 'ohlc4_down', line_color=self.gray2, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)

            df['SIG_QFY_X2'] = df['y_BREAKOUT'] == 3
            sig = tuple(df['SIG_QFY_X2'])
            view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'ohlc4_down', line_color=self.gray2, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)

        p.legend.visible = False
        p.add_tools(HoverTool(

            tooltips=[("Date", "@Date_str"),
                                ("ohlc4", "@ohlc4{$0,0.00}"),
                                ("Volume", "@Volume{($ 0.00 a)}")],

            mode='vline'
        ))

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p


    def chart_mt(self, df, name):
        df['ohlc4_up'] = df['ohlc4'] * 1.003
        df['ohlc4_down'] = df['ohlc4'] * 0.997
        df['ohlc4_down2'] = df['ohlc4'] * 0.996
        df['ohlc4_down3'] = df['ohlc4'] * 0.995
        stock = ColumnDataSource(df)
        p = figure(sizing_mode='fixed',
                   plot_width=self.width,
                   plot_height=220,
                   toolbar_location=self.toolbar_location,
                   y_axis_location=self.y_axis_location,
                   tools=self.tools,
                   title=name)

        p.vbar(x='index', width=0.7, bottom='Low', top='High',
               fill_color="#A7DBD8", fill_alpha=.5, line_color="#A7DBD8",
               source=stock)

        p.line('index', 'ohlc4', color=self.blue, source=stock)
        # p.line('index', 'bufferUp_S', color=self.orange, source=stock)
        #
        # p.line('index', 'bufferDn', color=self.gray2, source=stock, line_width=3)
        # p.line('index', 'bufferUp', color=self.orange, source=stock, line_width=3)
        #
        # p.line('index', 'MTx', color=self.blue, source=stock)


        # p.circle('index', 'ohlc4', color=self.blue, size=5, legend_label="ohlc", source=stock)
        # p.line('index', 'ohlc4', color=self.blue, source=stock)

        df['SIG_LONG'] = df['SIG_ALL_MT'] == 0
        sig = tuple(df['SIG_LONG'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.green, legend_label="MTx", size=3, source=stock, view=view_sig)

        df['SIG_SHORT'] = df['SIG_ALL_MT'] == 1
        sig = tuple(df['SIG_SHORT'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.circle('index', 'ohlc4', color=self.red, legend_label="MTx", size=3, source=stock, view=view_sig)
        
        df['SIG_BUY'] = df['SIG_MT'] == 0
        sig = tuple(df['SIG_BUY'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.triangle('index', 'ohlc4_up', line_color=self.orange, line_width=3, fill_color=self.green, size=15, source=stock, view=view_sig)

        df['SIG_SELL'] = df['SIG_MT'] == 1
        sig = tuple(df['SIG_SELL'])
        view_sig = CDSView(source=stock, filters=[BooleanFilter(sig)])
        p.inverted_triangle('index', 'ohlc4_down', line_color=self.orange, line_width=3, fill_color=self.red, size=15, source=stock, view=view_sig)

        # df['MTx_color'] = df['MTx_color'].astype(int)
        # df['MTx_color'] = df['MTx_color'].astype(str)
        #
        # p.text('index', 'ohlc4_down2', text="MTx_color", text_font_size="8pt", text_color="#000000",
        #        source=stock)
        #
        # df['MTx_color_sma'] = df['MTx_color_sma'].astype(int)
        # df['MTx_color_sma'] = df['MTx_color_sma'].astype(str)
        #
        # p.text('index', 'ohlc4_down3', text="MTx_color_sma", text_font_size="8pt", text_color="#000000",
        #        source=stock)


        p.legend.visible = False
        p.add_tools(HoverTool(

            tooltips=[("Date", "@Date_str"),
                                ("ohlc4", "@ohlc4{$0,0.00}"),
                                ("Volume", "@Volume{($ 0.00 a)}")],

            mode='vline'
        ))

        # start default settings  ----------------------------------------------------------------------------------
        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"
        p.min_border_left = self.min_border_left
        p.min_border_right = self.min_border_right
        p.min_border_top = self.min_border_top
        p.min_border_bottom = self.min_border_bottom
        p.outline_line_width = 1
        p.outline_line_alpha = 1
        p.outline_line_color = self.gray2
        # end default settings ------------------------------------------------------------------------------------
        return p

