
def get_total_seconds(timedelta):
    """
    Backported for Python < 2.7

    See http://docs.python.org/library/datetime.html.
    """
    return ((timedelta.microseconds + (
            timedelta.seconds +
            timedelta.days * 24 * 60 * 60
        ) * 10**6) / float(10**6))

