from multiprocessing import Value

class NotPositiveAmountError(Exception):
    pass

class Account:
    def __init__(self, account_id: int, balance: int = 0):
        self.account_id = account_id
        self.balance = Value('q', balance)

    def get_balance(self) -> Value:
        return self.balance.value

    def compare_and_swap(self, expected, new_value) -> bool:
        with self.balance.get_lock():
            if self.balance.value == expected:
                self.balance.value = new_value
                return True
            return False


# TransferService Compare-And-Swap
class TransferService:
    @staticmethod
    def transfer_money(from_account: Account, to_account: Account, amount: int) -> bool:
        if amount <= 0:
            raise NotPositiveAmountError()
        while True: # todo: add timeout to avoid infinite loop
            old_from = from_account.get_balance()
            if old_from < amount:
                return False
            if from_account.compare_and_swap(old_from, old_from - amount):
                break

        while True: # todo: add timeout to avoid infinite loop
            old_to = to_account.get_balance()
            if to_account.compare_and_swap(old_to, old_to + amount):
                return True
