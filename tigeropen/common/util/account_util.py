import re

PAPER_ACCOUNT_DIGIT_LEN = 17


class AccountUtil:

    @staticmethod
    def is_paper_account(account):
        try:
            if account:
                account = str(account)
                return account.isdigit() and len(account) >= PAPER_ACCOUNT_DIGIT_LEN
        except:
            pass
        return False

