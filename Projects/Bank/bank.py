import json
from abc import ABC, abstractmethod


class Account(ABC):
    bank_name = "MyBank"
    total_accounts = 0

    def __init__(self, acc_number, owner, balance=0):
        self._acc_number = acc_number
        self._owner = owner
        self._balance = balance
        self._transactions = []
        Account.total_accounts += 1

    @property
    def balance(self):
        return self._balance

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, name):
        if name.strip() == "":
            print("Name can't be empty")
        else:
            self._owner = name

    def deposit(self, amount):
        if amount <= 0:
            print("Amount must be positive")
            return False
        self._balance += amount
        self._transactions.append(Transaction("Deposit", amount))
        print(f"Deposited {amount}. Balance = {self._balance}")
        return True

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def show_info(self):
        pass

    def show_transactions(self):
        if not self._transactions:
            print("No transactions yet.")
            return
        print(f"\nTransactions for {self._acc_number}:")
        for t in self._transactions:
            t.show()

    @classmethod
    def show_total(cls):
        print(f"Total accounts: {cls.total_accounts} in {cls.bank_name}")

    @staticmethod
    def valid_number(num):
        return num.startswith("ACC-")


class SavingsAccount(Account):
    def withdraw(self, amount):
        if amount <= 0:
            print("Amount must be positive")
            return False
        if amount > self._balance:
            print("Not enough money")
            return False
        self._balance -= amount
        self._transactions.append(Transaction("Withdraw", amount))
        print(f"Withdrew {amount}. Balance = {self._balance}")
        return True

    def show_info(self):
        print(f"Savings | {self._acc_number} | {self._owner} | {self._balance}")


class CurrentAccount(Account):
    def withdraw(self, amount):
        if amount <= 0:
            print("Amount must be positive")
            return False
        if amount > self._balance + 500:
            print("Over limit")
            return False
        self._balance -= amount
        self._transactions.append(Transaction("Withdraw", amount))
        print(f"Withdrew {amount}. Balance = {self._balance}")
        return True

    def show_info(self):
        print(f"Current | {self._acc_number} | {self._owner} | {self._balance}")


class Transaction:
    def __init__(self, t_type, amount):
        self.t_type = t_type
        self.amount = amount

    def show(self):
        print(f"  {self.t_type} | {self.amount}")


class Customer:
    def __init__(self, cid, name):
        self.cid = cid
        self.name = name
        self.phones = set()
        self.accounts = []

    def add_phone(self, phone):
        self.phones.add(phone)

    def add_account(self, acc):
        self.accounts.append(acc)

    def rename(self, new_name):
        if new_name.strip() == "":
            print("Name can't be empty")
            return
        self.name = new_name
        for acc in self.accounts:
            acc.owner = new_name
        print(f"Customer and all accounts renamed to {new_name}")

    def show(self):
        print(f"\nCustomer: {self.name} (ID: {self.cid})")
        print(f"Phones: {self.phones}")
        for a in self.accounts:
            a.show_info()


class Loan:
    def __init__(self, loan_id, account, amount, rate=0.05):
        self.loan_id = loan_id
        self.account = account
        self.amount = amount
        self.rate = rate

    def total_due(self):
        return self.amount * (1 + self.rate)

    def show(self):
        print(f"Loan {self.loan_id} | {self.account.owner} | "
              f"Amount: {self.amount} | Total due: {self.total_due()}")


class Bank:
    def __init__(self, name):
        self.name = name
        self.customers = {}
        self.accounts = {}
        self.loans = []

    def add_customer(self, c):
        self.customers[c.cid] = c

    def open_account(self, cid, acc):
        self.accounts[acc._acc_number] = acc
        self.customers[cid].add_account(acc)

    def add_loan(self, loan):
        self.loans.append(loan)

    def find(self, acc_num):
        return self.accounts.get(acc_num)


def save_all(bank):
    data = {
        "customers": [
            {"cid": c.cid, "name": c.name, "phones": list(c.phones)}
            for c in bank.customers.values()
        ],
        "accounts": [
            {
                "number": acc._acc_number,
                "owner": next((c.cid for c in bank.customers.values() if acc in c.accounts), ""),
                "kind": "Savings" if isinstance(acc, SavingsAccount) else "Current",
                "balance": acc.balance,
                "transactions": [
                    {"type": t.t_type, "amount": t.amount}
                    for t in acc._transactions
                ],
            }
            for acc in bank.accounts.values()
        ],
        "loans": [
            {"id": l.loan_id, "account": l.account._acc_number,
             "amount": l.amount, "rate": l.rate}
            for l in bank.loans
        ],
    }
    with open("bank.json", "w") as f:
        json.dump(data, f, indent=2)


def load_all(bank):
    try:
        with open("bank.json") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 1, 1, 1

    for c in data.get("customers", []):
        cust = Customer(c["cid"], c["name"])
        for p in c["phones"]:
            cust.add_phone(p)
        bank.add_customer(cust)

    for a in data.get("accounts", []):
        owner = bank.customers[a["owner"]].name if a["owner"] in bank.customers else "Unknown"
        if a["kind"] == "Savings":
            acc = SavingsAccount(a["number"], owner, a["balance"])
        else:
            acc = CurrentAccount(a["number"], owner, a["balance"])
        for t in a.get("transactions", []):
            acc._transactions.append(Transaction(t["type"], t["amount"]))
        if a["owner"] in bank.customers:
            bank.open_account(a["owner"], acc)
        else:
            bank.accounts[a["number"]] = acc

    for l in data.get("loans", []):
        acc = bank.find(l["account"])
        if acc:
            bank.add_loan(Loan(l["id"], acc, l["amount"], l["rate"]))

    cc = max((int(c["cid"][1:]) for c in data.get("customers", [])), default=0) + 1
    ac = max((int(a["number"][4:]) for a in data.get("accounts", [])), default=0) + 1
    lc = max((int(l["id"][1:]) for l in data.get("loans", [])), default=0) + 1
    return cc, ac, lc


def clean_customer_id(text):
    text = text.strip().upper()
    if text and not text.startswith("C"):
        text = "C" + text
    return text


def clean_account_number(text):
    text = text.strip().upper()
    if text.startswith("ACC"):
        text = text.replace("ACC", "ACC-", 1).replace("--", "-")
    elif text.isdigit():
        text = "ACC-" + text
    return text


def menu():
    print("""
Customers
1.  Add customer
2.  Rename customer
3.  Show all

Accounts
4.  Open savings account
5.  Open current account
6.  Show total accounts

Money
7.  Deposit
8.  Withdraw
9.  Show account transactions

Loans 
10. Request loan
11. Show all loans

Other 
0.  Exit
""")


def ask_amount():
    try:
        return float(input("Amount: "))
    except:
        print("Invalid number")
        return 0


def goodbye():
    print("Bye!")


bank = Bank("MyBank")
customer_counter, account_counter, loan_counter = load_all(bank)

while True:
    menu()
    choice = input("Choice: ").strip()

    if choice == "1":
        name = input("Name: ")
        while name.strip() == "":
            print("Name can't be empty. Try again.")
            name = input("Name: ")

        cid = f"C{customer_counter:03d}"
        customer_counter += 1

        c = Customer(cid, name)
        phone = input("Phone: ")
        if phone:
            c.add_phone(phone)
        bank.add_customer(c)
        print(f"Customer added with ID {cid}")
        save_all(bank)

    elif choice == "2":
        cid = clean_customer_id(input("Customer ID: "))
        if cid not in bank.customers:
            print("Not found")
            continue
        new_name = input("New name: ")
        bank.customers[cid].rename(new_name)
        save_all(bank)

    elif choice == "3":
        for c in bank.customers.values():
            c.show()

    elif choice == "4" or choice == "5":
        cid = clean_customer_id(input("Customer ID: "))
        if cid not in bank.customers:
            print("Not found")
            continue

        customer = bank.customers[cid]

        if choice == "4":
            new_type = SavingsAccount
            type_name = "Savings"
        else:
            new_type = CurrentAccount
            type_name = "Current"

        already_has = False
        for acc in customer.accounts:
            if isinstance(acc, new_type):
                already_has = True
                break

        if already_has:
            print(f"{customer.name} already has a {type_name} account.")
            continue

        num = f"ACC-{account_counter:04d}"
        if not Account.valid_number(num):
            print("Invalid account number")
            continue
        account_counter += 1

        acc = new_type(num, customer.name)
        bank.open_account(cid, acc)
        print(f"Account {num} created")
        save_all(bank)

    elif choice == "6":
        Account.show_total()

    elif choice == "7":
        num = clean_account_number(input("Account number: "))
        acc = bank.find(num)
        if acc:
            if acc.deposit(ask_amount()):
                save_all(bank)
        else:
            print("Not found")

    elif choice == "8":
        num = clean_account_number(input("Account number: "))
        acc = bank.find(num)
        if acc:
            if acc.withdraw(ask_amount()):
                save_all(bank)
        else:
            print("Not found")

    elif choice == "9":
        num = clean_account_number(input("Account number: "))
        acc = bank.find(num)
        if acc:
            acc.show_transactions()
        else:
            print("Not found")

    elif choice == "10":
        num = clean_account_number(input("Account number: "))
        acc = bank.find(num)
        if not acc:
            print("Not found")
            continue
        amount = ask_amount()
        if amount <= 0:
            print("Invalid amount")
            continue
        loan = Loan(f"L{loan_counter:03d}", acc, amount, 0.07)
        loan_counter += 1
        bank.add_loan(loan)
        loan.show()
        save_all(bank)

    elif choice == "11":
        if not bank.loans:
            print("No loans yet.")
        else:
            for loan in bank.loans:
                loan.show()

    elif choice == "0":
        save_all(bank)
        goodbye()
        break

    else:
        print("Wrong choice")
