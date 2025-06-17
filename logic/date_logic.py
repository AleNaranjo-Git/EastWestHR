from datetime import date, timedelta
from typing import List
import holidays
import logging

def get_holidays(start_date: date, end_date: date, country: str = "CR") -> List[date]:
    holiday_dates: List[date] = []
    cr_holidays = holidays.country_holidays(country, years=range(start_date.year, end_date.year + 1))
    for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
        if single_date in cr_holidays:
            holiday_dates.append(single_date)
    logging.debug(f"Holidays between {start_date} and {end_date}: {holiday_dates}")
    return holiday_dates

def is_business_day(check_date: date, holidays_list: List[date]) -> bool:
    return check_date.weekday() < 5 and check_date not in holidays_list