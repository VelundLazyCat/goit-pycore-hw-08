from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


class MyCustomError(Exception):
    pass


class Field:
    def __init__(self, value):
        if self.is_valid(value):
            self.value = value
        else:
            raise ValueError

    def is_valid(self, value):
        return True

    def __repr__(self):
        return self.value


class Name(Field):
    pass


class Phone(Field):

    def is_valid(self, phone_number: str):
        if (phone_number.isdigit() and len(phone_number) == 10):
            return True
        else:
            raise MyCustomError('Phone number is invalid')


class Birthday(Field):

    def __init__(self, value):
        try:
            # value = self.string_to_date(value)
            self.string_to_date(value)
            super().__init__(value)
        except ValueError:
            raise MyCustomError("Invalid date format. Use DD.MM.YYYY")

    def string_to_date(self, date_string):
        return datetime.strptime(date_string, '%d.%m.%Y').date()

    def date_to_string(self):
        if self.value:
            return self.value.strftime('%d.%m.%Y')

    def __str__(self):
        return str(self.value)


class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone_number == phone.value:
                self.phones.remove(phone)
                return phone

    def edit_phone(self, phone_number, phone_number_new):
        for phone in self.phones:
            if phone.value == phone_number:
                self.add_phone(phone_number_new)
                self.remove_phone(phone_number)
                return phone_number, phone_number_new
        raise ValueError

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone_number == phone.value:
                print(self.name, ': ', phone_number)
                return phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return birthday

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name}, birthday: {self.birthday}, phones: {phones}"


class AddressBook(UserDict):
    # реалізація класу

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        return self.data.pop(name, None)

    # def iterator(self, n=5):
    #    records = list(self.data.values())
    #    for i in range(0, len(records), n):
    #        yield records[i:i+n]

    def get_upcoming_birthdays(self, days=7):

        def prepare_user_list():
            prepared_list = []
            for user, value in self.data.items():
                prepared_list.append(
                    {"name": user, "birthday": value.birthday})

            return prepared_list

        def find_next_weekday(start_date, weekday):
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        def adjust_for_weekend(birthday):
            if birthday.weekday() >= 5:
                birthday = find_next_weekday(birthday, 0)
            return birthday

        upcoming_birthdays = []
        today = date.today()

        for user in prepare_user_list():
            if not user["birthday"]:
                continue
            date_birthday = datetime.strptime(
                user["birthday"].value, '%d.%m.%Y').date()
            birthday_this_year = date_birthday.replace(
                year=today.year)

            if (birthday_this_year - today).days < 0:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year+1)

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date = adjust_for_weekend(birthday_this_year)
                upcoming_birthdays.append(
                    {"name": user["name"], "birthday": congratulation_date})
        return upcoming_birthdays

    def __str__(self) -> str:
        records = 'Book records:\n'
        for name, value in self.data.items():
            phones = '; '.join(p.value for p in value.phones)
            records += f"Contact name: {name}, birthday: {
                value.birthday} phones: {phones}\n"
        return records


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter the argument for the command"
        except MyCustomError as f:
            return f
        except KeyError as k:
            print(k)
        except IndexError:
            return "Must be one phone number"

    return inner


@input_error
def say_hello(args, book: AddressBook):
    return "How can I help you?"


@input_error
def good_bye(args, book: AddressBook):
    return "Good bye!\nPress Enter please..."


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if not record:
        record = Record(name)
        book.add_record(record)
        message = f"Contact {name} added."

    if phone:
        record.add_phone(phone)
    return message


@input_error
def do_change(args, book: AddressBook):
    name, phone_old, phone_new = args
    record = book.find(name)
    message = "Somthing strange."
    if record:
        record.edit_phone(phone_old, phone_new)
        message = f'Contact {name} has been changed'
    else:
        raise MyCustomError('We have a problem. This contact not exist')
    return message


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    message = "Somthing strange."
    if record:
        message = str(record)
    else:
        raise MyCustomError('We have a problem. This contact not exist')
    return message


@input_error
def show_all(args, book: AddressBook):
    result = str(book)
    return result


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def unknown_comand():
    raise KeyError('Command unknown! Maybe try else?')


@input_error
def add_birthday(args, book):
    name, bday, *_ = args
    record = book.find(name)
    if not record:
        raise MyCustomError('We have a problem. This contact not exist')

    record.add_birthday(bday)
    message = f"Birthday information for {name} updated."
    return message


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise MyCustomError('We have a problem. This contact not exist')

    bday = str(record.birthday)
    message = f"{name} birthday: {bday}"
    return message


@input_error
def birthdays(args, book):

    congrats = book.get_upcoming_birthdays()
    if congrats:
        message = '\ncongratulation list for next week\n\n'.upper()
        for con in congrats:
            message += f'{con['name']} birthday:{con['birthday']}\n'
    else:
        message = '\nno birthdays for next week.\n\n'.upper()

    return message


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


@input_error
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


def get_handler(command):
    return COMMANDS[command]


COMMANDS = {'hello': say_hello,  'add': add_contact,
            'change': do_change, 'phone': show_phone,
            'all': show_all,     'close': good_bye,
            'exit': good_bye,    'add-birthday': add_birthday,
            'show-birthday': show_birthday, 'birthdays': birthdays,
            }


def main():
    book = load_data()

    # блок команд для спрощення автотесту днів народжень
    '''john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday('29.09.2022')
    book.add_record(john_record)
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday('10.10.2022')
    book.add_record(jane_record)
    cat_record = Record("Cat")
    cat_record.add_phone("3334445556")
    cat_record.add_birthday('02.10.2022')
    book.add_record(cat_record)'''

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        command, *args = parse_input(user_input)
        command = command.lower()
        if not args:
            args = None,

        if COMMANDS.get(command):
            result = get_handler(command)(args, book=book)
            print(result)
            if 'bye' in str(result):
                input()
                break
        else:
            unknown_comand()
    save_data(book)


if __name__ == '__main__':
    main()
