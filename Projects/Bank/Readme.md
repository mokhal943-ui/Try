MyBank

MyBank is a simple banking management program I made using Python.
I made this project to practice object-oriented programming and to build something more practical than small programming exercises.

What it can do

Add customers
Rename customers
Add phone numbers
Open savings and current accounts
Deposit money
Withdraw money
View account transactions
Request loans
View loans
Save and load the data using JSON

What I used
Python 3
Classes and objects
Inheritance
Abstract classes
Properties
Class and static methods
JSON files
Main classes

The project has several classes:
Account is the base class for bank accounts.
SavingsAccount and CurrentAccount are the two account types.
Customer stores customer information and their accounts.
Transaction stores deposits and withdrawals.
Loan handles loan information.
Bank keeps track of customers, accounts, and loans.
SavingsAccount and CurrentAccount inherit from Account, but they have different withdrawal rules.

Saving data
The program saves the customers, accounts, transactions, and loans in a JSON file called bank.json.
When the program starts again, it loads the saved information so the data does not disappear when the program is closed.

Running the project
You only need Python 3.
Run:
python bank.py

The program will show a menu where you can choose what you want to do.
