from scripts.sql_parser.enums import FilterCondition
from scripts.sql_parser.utils import *


# covers LIMIT and OFFSET clauses
def get_limit_sql(limit_param, offset_param, order_by_param):
    sql = ''
    if limit_param:
        lim = get_int_or_zero(limit_param)
        if lim != 0:
            if not order_by_param and lim < 0:
                sql += 'ORDER BY 1 DESC\n'
            sql += f'LIMIT {abs(lim)}'

            if offset_param:
                off_val = get_int_or_zero(offset_param)
                if off_val > 0:
                    sql += f' OFFSET {off_val}'

    return sql


# covers ORDER BY clause
# TODO Update to handle table aliasing
def get_order_by_sql(order_by_param):
    sql = ''
    if order_by_param:
        col, direction = order_by_param
        sql = f'ORDER BY {col} {"ASC" if int(direction) >= 0 else "DESC"}\n'
    return sql


# covers WHERE clause
# TODO Update to handle table aliasing
def get_where_sql(query, where_param):
    sql = ''
    if where_param:
        if get_list_or_zero(where_param):
            checked = False
            for i, cond in enumerate(where_param):
                or_and_choice = and_or_operator(cond)
                if "WHERE" not in query and not checked:
                    checked = True
                    start = "WHERE"
                else:
                    start = f'\t{or_and_choice}' if i > 0 else f'\t{or_and_choice}'
                is_between_agg, agg_vals = get_between_agg(cond[1:])
                if is_between_agg:
                    low, col, high = agg_vals
                    sql += f'{start} {AggregateFunctions.BETWEEN.value.format(col, low, high)}\n'
                else:
                    sql += f'{start} {cond[1:]}\n'
    return sql


# covers LIKE clause
def get_like_sql(c, sw, ew):
    sql = ''
    if c or sw or ew:
        cond = 'contains' if c else 'starts_with' if sw else 'ends_with'
        col, col_val = c if c else sw if sw else ew
        formatted_like = FilterCondition[cond.upper()].value.format(col_val)
        sql = f'WHERE {col} {formatted_like}\n'
    return sql


def get_join_sql(table_left, table_right, distinct, j_type, shared_col):
    l_name, l_title, l_cols = format_join_table_data(table_left)
    r_name, r_title, r_cols = format_join_table_data(table_right)
    cols = l_cols + r_cols
    sql = f'SELECT {distinct}'
    sql += ','.join(cols)

    sql += f'\nFROM {l_title}\n'
    sql += f'{format_join_type(j_type)} JOIN {r_title}\n'
    sql += f'ON {l_name}.{shared_col} = {r_name}.{shared_col}\n'
    return sql


# covers
def get_distinct_sql(distinct_param):
    return 'DISTINCT ' if distinct_param is True else ''
