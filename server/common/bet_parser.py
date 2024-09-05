from .utils import Bet
from typing import List, Tuple
from common.constants import BET_SEPARATOR, FIELD_SEPARATOR, EXPECTED_BET_FIELDS

def parse_bets(data: str) -> Tuple[List[Bet], bool]:
    """
    Parses a string containing Bet records separated by semicolons.
    Each record should have exactly EXPECTED_BET_FIELDS fields separated by FIELD_SEPARATOR.
    Returns a list of Bet objects and a boolean indicating if there were any errors.
    """
    bet_records = data.split(BET_SEPARATOR)
    bets = []
    hasError = False

    for record in bet_records:
        fields = record.split(FIELD_SEPARATOR)

        if len(fields) != EXPECTED_BET_FIELDS:
            hasError = True
            continue  # Skip this record and proceed with the next

        try:
            # Create a Bet object
            bet = Bet(*fields)
            bets.append(bet)
        except (TypeError, Exception):
            hasError = True

    return bets, hasError
