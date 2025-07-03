def parse_time(time_str):
    """
    Parses a time string in the format 'HH:MM' and returns a tuple of integers (hour, minute).
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour, minute
    except ValueError:
        raise ValueError("Time must be in 'HH:MM' format") from None