import os
import sqlite3

from gladAnalysis.errors import Error

app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(app_dir)
data_dir = os.path.join(root_dir, 'data')


def insert_intersect_table(cursor, tile_dict):
    create_aoi_tiles_table(cursor)

    row_list = []

    # tile_dict is a dict of {tile_obj: proportion_covered}
    # `tile` objects are from the mercantile library
    for tile, proportion_covered in tile_dict.items():
        row = [tile.x, tile.y, tile.z, proportion_covered]

        # append to row list for batch insert later
        row_list.append(row)

    cursor.executemany('INSERT INTO tiles_aoi values (?, ?, ?, ?)', row_list)


def create_aoi_tiles_table(cursor):
    """After we've identified our intersecting / within
       tiles, insert this table into the db so we can
       join to it.
    """

    # create temporary AOI table
    create_table_sql = ('CREATE TEMPORARY TABLE tiles_aoi ( '
                        'x INTEGER, '
                        'y INTEGER, '
                        'z INTEGER, '
                        'proportion_covered REAL) ')
    cursor.execute(create_table_sql)

    # add index on x - trying to increase cardinality for easy searching
    # previously had (x,y,z) as primary key - while true, it was very slow
    cursor.execute('CREATE INDEX tiles_aoi_idx_x ON tiles_aoi(x)')


def select_within_tiles(cursor, request):
    """Execute the join of our AOI to the all-stats table"""

    agg_by = request.args.get('aggregate_by')
    period = request.args.get('period')
    gladConfirmOnly = request.args.get('gladConfirmOnly')

    if agg_by:
        first_col = 'alert_date'
    else:
        first_col = 1

    sql = ('SELECT {}, CAST(SUM(proportion_covered * alert_count) as integer) '
           'FROM tile_alert_stats '
           'INNER JOIN tiles_aoi '
           'WHERE tile_alert_stats.x = tiles_aoi.x '
           'AND tile_alert_stats.y = tiles_aoi.y '
           'AND tile_alert_stats.z = tiles_aoi.z '.format(first_col)
           )

    if period:
        sql += "AND alert_date BETWEEN '{}' AND '{}' ".format(*period.split(','))

    if gladConfirmOnly:
        sql += 'AND confidence = 3 '

    if agg_by:
        sql += 'GROUP BY alert_date '

    # run the query against the database
    cursor.execute(sql)

    # return rows - [(alert_date, alert_count), (alert_date, alert_count)]
    return cursor.fetchall()


def connect(dbname=None):
    # useful for testing with our demo db
    sqlite_db = dbname if dbname else os.path.join(data_dir, 'stats.db')

    if not os.path.exists(sqlite_db):
        raise Error('{} does not exist. Dockerfile has download code'.format(sqlite_db))

    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    return conn, cursor


def get_latest():
    conn, cursor = connect()
    cursor.execute('SELECT alert_date FROM latest')

    return cursor.fetchone()[0]
