import re
from typing import Optional, Dict, List

from enums import SqlFunctions


def get_int_or_zero(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return 0


def get_list_or_zero(x):
    return x if isinstance(x, list) and len(x) > 0 else 0


def str_val(*args):
    if len(args) == 1:
        return args[0] if args[0].isalpha() else f'"{args[0]}"'
    else:
        return tuple(x if x.isalpha() else f'"{x}"' for x in args)


def and_or_operator(x):
    if x.startswith('&'):
        return 'AND'
    elif x.startswith('|'):
        return 'OR'
    else:
        raise ValueError(f'Issue with {x}, and {x[0]}')


# apply aggregation and alias to column name. eg: "count=UnitPrice:UP" translated to: COUNT(UnitPrice) AS UP
def format_cols_query(cols):
    form_cols = []
    for col in cols:
        if '=' in col and ':' in col:
            agg, col_name, col_alias = re.split(r'[:=]', col)
            col_name, col_alias = str_val(col_name, col_alias)
            agg_func = SqlFunctions[agg.upper()].value.format(col_name)
            form_cols.append(f'{agg_func} AS {col_alias}')
        elif '=' in col:
            agg, col_name = col.split('=')
            col_name = str_val(col_name)
            agg_func = SqlFunctions[agg.upper()].value.format(col_name)
            form_cols.append(f'{agg_func}')
        elif ':' in col:
            split = col.split(':')
            col_name, col_alias = split[0], str_val(split[1].strip())
            form_cols.append(f'{col_name} AS {col_alias}')
        else:
            col = str_val(col)
            form_cols.append(f'{col}')

    return form_cols


# parse tables in dictionaries, in a list. parse all displayed columns in a single list
def process_multi_table_join(tables):
    tables_data = []
    formatted_cols = []

    for i, t in enumerate(tables):
        t_data = {}
        name, shared_col = t['name'], str_val(t['shared'])
        t_alias = None

        #  split table name into name and alias, if ':' is present
        if ':' in name:
            t_title = name.replace(':', ' ')
            elements = name.split(':')
            t_name, t_alias = str_val(elements[0]), elements[1]
            if len(elements[0].split(' ')) > 1:
                t_title = f'{t_name} {t_alias}'
        else:
            t_name = str_val(name)
            t_title = t_name

        # format the target columns (these are the ones between SELECT and FROM)
        #  use table alias where necessary
        if 'cols' in t:
            cols = format_cols_query(t['cols'])
            for col in cols:
                displayed_val = t_alias if t_alias else str_val(name)
                agg_notations = [enum_item.name for enum_item in list(SqlFunctions)[:4]]

                # if any aggregation is done on the column
                if any(col.startswith(agg) for agg in agg_notations):
                    # include table name or alias inside the agg function. ex sum(TableName.Quantity)
                    data = col.replace('(', f'({displayed_val}.')
                    string = f'\n\t{data}'
                else:
                    string = f'\n\t{displayed_val}.{col}'

                formatted_cols.append(string)
        else:
            formatted_cols.append(f'\n\t{t_alias if t_alias else str_val(name)}.*')

        t_data.update({'name': t_name, 'title': t_title, 'shared': shared_col})
        if t_alias:
            t_data.update({'alias': t_alias})
        if 'join' in t:
            t_data.update({'join': t.get('join')})

        tables_data.append(t_data)

    return tables_data, formatted_cols


def process_two_table_join(table):
    t_title = table.get('name')

    formatted_cols = []
    t_alias = None

    # perform naming operations and set table alias
    if ':' in t_title:
        t_name, t_alias = t_title.split(':')
        t_title = t_title.replace(':', ' ')

    t_name = t_alias if t_alias else t_title
    cols = format_cols_query(table.get('cols'))
    for item in cols:
        formatted_cols.append(f'\n\t{t_alias if t_alias else t_name}.{item if "cols" in table else "*"}')

    tables_data = {'name': t_name, 'title': t_title}

    return tables_data, formatted_cols


def format_join_type(join_type):
    joins = {
        'i': 'INNER',
        'l': 'LEFT',
        'r': 'RIGHT',
        'f': 'FULL',
        'c': 'CROSS'
    }

    return joins.get(join_type.lower(), 'INNER')


# check if string is BETWEEN aggregation. eg: "10<UnitPrice<20" translated to: UnitPrice BETWEEN 10 AND 20
def get_between_agg(expression):
    is_valid = False
    res = None

    number_pattern = r'\b\d+(?:\.\d+)?\b'
    letter_pattern = r'[A-Za-z_]+'

    numbers = re.findall(number_pattern, expression)
    letters = re.findall(letter_pattern, expression)

    if len(numbers) > 0 and len(letters) == 1:
        numbers_with_letters = numbers.copy()
        numbers_with_letters.insert(1, letters[0])

        if len(numbers_with_letters) > 2:
            is_valid = True
            res = numbers_with_letters

    return is_valid, res


# format a table for multi_join readability
def get_table(
        name: str,
        shared: str,
        cols: Optional[List[str]] = None,
        join: Optional[str] = None
) -> Dict[str, str]:
    res = {'name': name, 'shared': shared, 'cols': cols}
    if join:
        res.update({'join': join})
    return res
