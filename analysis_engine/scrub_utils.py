"""

Scrubbing Utilities for Transforming Datasets
=============================================

Perform dataset scrubbing action
and return the scrubbed dataset as a ready-to-go
data feed. This is an approach for normalizing
an internal data feed.

Supported environment variables:

::

    # verbose logging in this module
    # note this can take longer to transform
    # DataFrames and is not recommended for
    # production:
    export DEBUG_FETCH=1

Supports Data feed outputs:

::

    DATAFEED_DAILY = 900
    DATAFEED_MINUTE = 901
    DATAFEED_TICK = 902
    DATAFEED_STATS = 903
    DATAFEED_PEERS = 904
    DATAFEED_NEWS = 905
    DATAFEED_FINANCIALS = 906
    DATAFEED_EARNINGS = 907
    DATAFEED_DIVIDENDS = 908
    DATAFEED_COMPANY = 909

"""

import datetime
import pandas as pd
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import ev
from analysis_engine.iex.consts import DATAFEED_DAILY
from analysis_engine.iex.consts import DATAFEED_MINUTE
from analysis_engine.iex.consts import DATAFEED_TICK
from analysis_engine.iex.consts import DATAFEED_STATS
from analysis_engine.iex.consts import DATAFEED_PEERS
from analysis_engine.iex.consts import DATAFEED_NEWS
from analysis_engine.iex.consts import DATAFEED_FINANCIALS
from analysis_engine.iex.consts import DATAFEED_EARNINGS
from analysis_engine.iex.consts import DATAFEED_DIVIDENDS
from analysis_engine.iex.consts import DATAFEED_COMPANY
from analysis_engine.iex.consts import get_datafeed_str

log = build_colorized_logger(
    name=__name__)


def debug_msg(
        label,
        datafeed_type,
        msg_format,
        date_str,
        df):
    """debug_msg

    :param label: log label
    :param datafeed_type: fetch type
    :param msg_format: message to include
    :param date_str: date string
    :param df: ``pandas DataFrame`` or ``None``
    """

    msg = msg_format.format('_', date_str)

    if ev('DEBUG_FETCH', '0') == '1':
        if 'START' in msg:
            log.info(
                '{} - {} -------------------------'
                '------------------------------------'.format(
                    label,
                    get_datafeed_str(
                        df_type=datafeed_type)))
        msg = msg_format.format(
            df,
            date_str),
        if hasattr(df, 'empty'):
            log.info(
                '{} - {} - {} found df={} '
                'columns={}'.format(
                    label,
                    get_datafeed_str(
                        df_type=datafeed_type),
                    msg,
                    df,
                    df.columns.values))
        else:
            log.info(
                '{} - {} - {} not df={}'.format(
                    label,
                    get_datafeed_str(
                        df_type=datafeed_type),
                    msg,
                    df))

        if 'END' in msg:
            log.info(
                '{} - {} -------------------------'
                '------------------------------------'.format(
                    label,
                    get_datafeed_str(
                        df_type=datafeed_type)))
    else:
        log.info(
            '{} - {} - {}'.format(
                label,
                get_datafeed_str(
                    df_type=datafeed_type),
                msg))
    # end of debug pre-scrub logging

# end of debug_msg


def scrub_dataset(
        label,
        datafeed_type,
        df,
        date_str=None,
        msg_format=None,
        scrub_mode='sort-by-date',
        ds_id='no-id'):
    """scrub_dataset

    Scrub a DataFrame and return the resulting DataFrame

    :param label: log label
    :param datafeed_type: ``analysis_engine.iex.consts.DATAFEED_*`` type
            ::

                DATAFEED_DAILY = 900
                DATAFEED_MINUTE = 901
                DATAFEED_TICK = 902
                DATAFEED_STATS = 903
                DATAFEED_PEERS = 904
                DATAFEED_NEWS = 905
                DATAFEED_FINANCIALS = 906
                DATAFEED_EARNINGS = 907
                DATAFEED_DIVIDENDS = 908
                DATAFEED_COMPANY = 909
    :param df: ``pandas DataFrame``
    :param date_str: date string for simulating historical dates
                     or ``datetime.datetime.now()`` if not
                     set
    :param msg_format: msg format for a ``string.format()``
    :param scrub_mode: mode to scrub this dataset
    :param ds_id: dataset identifier
    """

    if not hasattr(df, 'empty'):
        log.info(
            '{} - {} no dataset_id={}'.format(
                label,
                datafeed_type,
                ds_id))
        return None

    out_df = df

    daily_date_format = '%I:%M %p'
    minute_date_format = '%I:%M %p'
    tick_date_format = '%I:%M %p'

    use_msg_format = msg_format
    if not msg_format:
        use_msg_format = 'df={} date_str={}'

    use_date_str = date_str
    if not use_date_str:
        use_date_str = datetime.datetime.now().strftime(
            '%Y-%m-%d')
        daily_date_format = '%Y-%m-%d %I:%M %p'
        minute_date_format = '%Y-%m-%d %I:%M %p'
        tick_date_format = '%Y-%m-%d %I:%M %p'

    debug_msg(
        label=label,
        datafeed_type=datafeed_type,
        msg_format='START - {}'.format(
            use_msg_format),
        date_str=use_date_str,
        df=df)

    try:
        if scrub_mode == 'sort-by-date':
            if datafeed_type == DATAFEED_DAILY:
                return out_df
            elif datafeed_type == DATAFEED_MINUTE:
                if 'label' in df:
                    for idx, i in enumerate(out_df['label']):
                        if ':' not in i:
                            out_df['label'][idx] = '{} {}:00 {}'.format(
                                use_date_str,
                                i.split(' ')[0],
                                i.split(' ')[1])
                        else:
                            out_df['label'][idx] = '{} {} {}'.format(
                                use_date_str,
                                i.split(' ')[0],
                                i.split(' ')[1])
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=minute_date_format)
            elif datafeed_type == DATAFEED_TICK:
                if 'label' in df:
                    for idx, i in enumerate(out_df['label']):
                        if ':' not in i:
                            out_df['label'][idx] = '{} {}:00 {}'.format(
                                use_date_str,
                                i.split(' ')[0],
                                i.split(' ')[1])
                        else:
                            out_df['label'][idx] = '{} {} {}'.format(
                                use_date_str,
                                i.split(' ')[0],
                                i.split(' ')[1])
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=tick_date_format)
            elif datafeed_type == DATAFEED_STATS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_PEERS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_NEWS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_FINANCIALS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_EARNINGS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_DIVIDENDS:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            elif datafeed_type == DATAFEED_COMPANY:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
            else:
                log.info(
                    '{} - {} - no scrub_mode={} '
                    'support'.format(
                        label,
                        datafeed_type,
                        scrub_mode))
                if 'label' in df:
                    out_df['date'] = pd.to_datetime(
                        df['label'],
                        format=daily_date_format)
        else:
            log.info(
                '{} - {} - no scrub_mode'.format(
                    label,
                    datafeed_type))
    except Exception as e:
        log.critical(
            '{} - {} sort={} - '
            'failed with ex={} data={}'.format(
                label,
                datafeed_type,
                scrub_mode,
                e,
                df))
        out_df = None
    # end of try/ex

    debug_msg(
        label=label,
        datafeed_type=datafeed_type,
        msg_format='END - df={} date_str={}',
        date_str=use_date_str,
        df=out_df)

    return out_df
# end of scrub_dataset