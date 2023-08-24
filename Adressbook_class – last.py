# #АДРЕСНА КНИГА

from collections import UserDict
from datetime import datetime, timedelta
import calendar
import re
import json

class AddressBook(UserDict):
    def add_record(self, record):
        if self.validate_record(record):
            key = record.name.value
            self.data[key] = record
            return True
        else:
            return False

    def remove_record(self, name):
        if name in self.data:
            del self.data[name]
            return True
        else:
            return False

    def find_records(self, **search_criteria):
        result = []
        found = False
        for record in self.data.values():
            if 'name' in search_criteria and len(search_criteria['name']) >= 2 and search_criteria[
                'name'] in record.name.value:
                result.append(record)
                found = True
            if 'phones' in search_criteria and len(search_criteria['phones']) >= 5:
                for phone in record.phones:
                    if search_criteria['phones'] in phone.value:
                        result.append(record)
                        found = True
                        break
        if not found:
            print("Немає контакту, що відповідає заданим критеріям пошуку")
        return result


    def validate_record(self, record):
        valid_phones = all(isinstance(phone, Phone) and phone.validate(phone.value) for phone in record.phones)
        valid_name = isinstance(record.name, Name)

        if record.birthday:
            valid_birthday = isinstance(record.birthday, Birthday) and record.birthday.validate(record.birthday.value)
        else:
            valid_birthday = True

        if not valid_phones:
            print("Номери телефонів не валідні.")
        if not valid_name:
            print("Ім'я не валідне.")
        if not valid_birthday:
            print("Дата народження не валідна.")

        return valid_phones and valid_name and valid_birthday

    def get_record_by_name(self, name):
        for record in self.data.values():
            if record.name.value == name:
                return record
        return None

    def get_all_records(self):

        all_contacts = []
        header = '{:<20} {:<15} {:<15}'.format('Ім\'я', 'Телефон', 'День народження')
        separator = '-' * len(header)
        all_contacts.append(header)
        all_contacts.append(separator)

        if self.data:
            for record in self.data.values():
                record_str = '{:<20} {:<15} {:<15}'.format(
                    record.name.value,
                    ', '.join(phone.value for phone in record.phones),
                    record.birthday.value if record.birthday else '-'
                )
                all_contacts.append(record_str)
        else:
            all_contacts.append("Адресна книга порожня")

        return '\n'.join(all_contacts)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.data):
            record = list(self.data.values())[self.index]
            self.index += 1
            return record
        else:
            raise StopIteration

    def iterator(self, n):
        return (list(self.data.values())[i:i + n] for i in range(0, len(self.data), n))


    def __str__(self):
        book_str = "\n".join(f"{name}: {record}" for name, record in self.data.items())
        return book_str


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.birthday = Birthday(birthday) if birthday is not None else None
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone is not None else []

    def add_phone_number(self, number):
        phone = Phone(number)
        if phone.validate(number):
            self.phones.append(phone)
            return True
        else:
            return False


    def remove_phone_number(self, number):
        if any(phone.value == number for phone in self.phones):
            new_phones = [phone for phone in self.phones if phone.value != number]
            self.phones = new_phones
            return True
        return False

    def change_phone_number(self, number, new_number):
        for index, phone in enumerate(self.phones):
            if phone.value == number:
                self.phones[index] = Phone(new_number)
                return True
        return False

    def days_to_birthday(self):
        if self.birthday and self.birthday.validate(self.birthday.value):
            parsed_date = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
            date_now = datetime.now().date()
            date_now_year = date_now.year
            next_year = date_now.year + 1
            parsed_date = parsed_date.replace(year=date_now_year)

            if parsed_date <= date_now:
                if calendar.isleap(next_year):
                    time_delta = (parsed_date - date_now + timedelta(days=366)).days
                else:
                    time_delta = (parsed_date - date_now + timedelta(days=365)).days
            else:
                time_delta = (parsed_date - date_now).days
            return time_delta
        else:
            return None

    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        if not phones_str:
            phones_str = "None"
        if not self.birthday:
            birthday_str = "None"
        else:
            birthday_str = self.birthday.value
        return f"Name: {self.name.value}, Phones: {phones_str}, Birthday: {birthday_str}"

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def validate(self, new_value):
        return True
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


    def __str__(self):
        return str(self.value)


class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            Field.value.fset(self, new_value)
        else:
            print(f'Номер телефону {new_value} не можна призначити, оскільки він не валідний')

    def validate(self, number):
        if number is None:
            return False
        try:
            phone_format = r'\+380\d{9}'
            if not re.match(phone_format, number):
                return False
            return True
        except ValueError:
            return False


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            Field.value.fset(self, new_value)
        else:
            print(f'Дату дня народження {new_value} не можна призначити, оскільки вона не валідна')

    def validate(self, new_value):
        try:
            datetime.strptime(new_value, '%d.%m.%Y').date()
            return True
        except ValueError:
            return False
        except TypeError:
            return False


class AddressBookFileHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def save_to_file(self, address_book):
        with open(self.file_name, 'w') as file:
            json.dump(address_book.data, file, default=self._serialize_record, indent=4)

    def _deserialize_record(self, contact_data):
        print(f"Спроба десеріалізації: {contact_data}")

        if isinstance(contact_data, str):
            return None

        name = contact_data.get('name')
        phones = contact_data.get('phones', [])
        birthday = contact_data.get('birthday')


        return Record(name, phones[0] if phones else None, birthday)

    def load_from_file(self):
        try:
            with open(self.file_name, 'r') as file:
                file_contents = file.read()
                print(f"Зчитані дані з файлу: {file_contents}")

                if not file_contents.strip():
                    print("Файл порожній. Повертаємо порожню адресну книгу.")
                    return AddressBook()

                try:
                    data = json.loads(file_contents)
                    if data is not None:
                        address_book = AddressBook()
                        address_book.data = data
                        print(f"Deserialized data: {data}")
                        return address_book
                    else:
                        print("Помилка: Не вдалося розпізнати дані з файлу.")
                        return None
                except json.JSONDecodeError as e:
                    print(f"Помилка: Не вдалося розпізнати дані з файлу. Помилка JSON: {e}")
                    return None

        except FileNotFoundError:
            with open(self.file_name, 'w') as file:
                file.write("{}")
            return AddressBook()

    def _serialize_record(self, record):
        return {
            'name': record.name.value,
            'phones': [phone.value for phone in record.phones],
            'birthday': record.birthday.value if record.birthday else None
        }




def handler_parse(rawstr):
    command = rawstr.split()[0].lower()
    if command in COMMANDS:
        return command
    for key, value in COMMANDS.items():
        if any(arg.startswith(command) for arg in value):
            return key
    return None

COMMANDS = {
    'get_all_records': ['all'],
    'add_record': ['add'],
    'remove_record': ['remove'],
    'find_records': ['find'],
    'add_phone_number': ['add_phone'],
    'remove_phone_number': ['remove_phone'],
    'change_phone_number': ['change_phone'],
    'days_to_birthday': ['when_birthday'],
    'save_to_file': ['save'],
    'load_from_file': ['load'],
    'exit': ['exit'],
}
COMMAND_DESCRIPTIONS = {
    'Вивести всі контакти': ['all'],
    'Додати контакт': ['add'],
    'Видалити контакт': ['remove'],
    'Знайти контакт': ['find'],
    'Додати номер телефону': ['add_phone'],
    'Видалити номер телефону': ['remove_phone'],
    'Змінити номер телефону': ['change_phone'],
    'Дні до дня народження': ['when_birthday'],
    'Зберегти до файлу': ['save'],
    'Завантажити з файлу': ['load'],
    'Вийти': ['exit'],
}


def print_command_list():
    commands_output = "Список доступних команд:\n"
    commands_list = list(COMMAND_DESCRIPTIONS.keys())
    num_columns = 3
    column_width = 25

    for i in range(0, len(commands_list), num_columns):
        chunk = commands_list[i:i + num_columns]
        for command in chunk:
            aliases = ", ".join(COMMAND_DESCRIPTIONS[command])
            commands_output += f"{aliases:<{column_width}}\t{command:<{column_width}}"
        commands_output += "\n"
    return commands_output


def main():
    address_book = AddressBook()
    print(print_command_list())

    while True:

        user_input = input('Waiting for command...').strip().lower()
        command = handler_parse(user_input)

        if command == 'get_all_records':
            all_contacts = address_book.get_all_records()
            print(all_contacts)


        elif command == 'add_record':
            name = input("Введіть ім'я контакту: ").strip().lower()
            phone = input("Введіть номер телефону контакту (+380________): ").strip()
            birthday = input("Введіть день народження контакту (дд.мм.рррр): ").strip()
            new_record = Record(name, phone, birthday)

            if address_book.add_record(new_record):
                print(f"Контакт успішно додано до адресної книги. \n{address_book.get_all_records()}")
            else:
                print("Не вдалося додати контакт. Дані не валідні.")

        elif command == 'remove_record':
            name = input("Введіть ім'я контакту для видалення: ").strip().lower()
            if address_book.remove_record(name):
                print(f"Контакт {name} успішно видалено з адресної книги. \n{address_book.get_all_records()}")
            else:
                print(f"Контакт {name} не знайдено в адресній книзі або ще не додано жодного контакту")

        elif command == 'find_records':
            search_criteria = {}

            print("За якими критеріями ви хочете здійснити пошук? \n 1. Шукати за ім'ям \n 2. Шукати за номером телефону")
            search_option = input("Виберіть опцію (1 або 2): ")

            if search_option == "1":
                search_name = input("Введіть ім'я для пошуку (мінімум 2 символи): ").strip().lower()
                if len(search_name) >= 2:
                    search_criteria['name'] = search_name
                else:
                    print("Ви ввели замало символів для імені. Пошук за іменем скасовано.")
            elif search_option == "2":
                search_phones = input("Введіть частину номеру телефону для пошуку (мінімум 5 символів): ").strip()
                if len(search_phones) >= 5:
                    search_criteria['phones'] = search_phones
                else:
                    print("Ви ввели замало символів для телефону. Пошук за номером телефону скасовано.")
            else:
                print("Невірний вибір опції. Введіть 1 або 2.")

            if 'name' in search_criteria or 'phones' in search_criteria:
                found_contacts = address_book.find_records(**search_criteria)
                if found_contacts:
                    if len(found_contacts) == 1:
                        print(f"Знайдений контакт: {found_contacts[0]}")
                    else:
                        print("Контакти знайдені:")
                        for contact in found_contacts:
                            print(contact)
                else:
                    print("Контакти не знайдені за заданими критеріями пошуку.")


        elif command == 'add_phone_number':
            name = input("Введіть ім'я контакту: ").strip().lower()
            contact = address_book.get_record_by_name(name)

            if contact is not None:
                new_phone = input("Введіть новий номер телефону: ").strip()
                if contact.add_phone_number(new_phone):
                    print(f"Номер телефону успішно додано. \n{address_book.get_all_records()}")
                else:
                    print("Не вдалося додати номер телефону. Номер не валідний.")
            else:
                print(f"Контакт з ім'ям {name} не знайдений в адресній книзі.")

        elif command == 'remove_phone_number':
            name = input("Введіть ім'я контакту: ").strip().lower()
            contact = address_book.get_record_by_name(name)

            if contact is not None:
                phone_to_remove = input("Введіть номер телефону для видалення: ").strip()
                if contact.remove_phone_number(phone_to_remove):
                    print(f"Номер телефону успішно видалено. \n{address_book.get_all_records()}")
                else:
                    print("Не вдалося видалити номер телефону. Номер не знайдений.")
            else:
                print(f"Контакт з ім'ям {name} не знайдений в адресній книзі.")

        elif command == 'change_phone_number':
            name = input("Введіть ім'я контакту: ").strip().lower()
            contact = address_book.get_record_by_name(name)

            if contact is not None:
                old_phone = input("Введіть старий номер телефону: ").strip()
                new_phone = input("Введіть новий номер телефону: ").strip()
                if contact.change_phone_number(old_phone, new_phone):
                    print(f"Номер телефону успішно змінено. \n{address_book.get_all_records()}")
                else:
                    print("Не вдалося змінити номер телефону. Старий номер не знайдений або новий номер не валідний.")
            else:
                print(f"Контакт з ім'ям {name} не знайдений в адресній книзі.")

        elif command == 'days_to_birthday':
            name = input("Введіть ім'я контакту: ").strip().lower()
            contact = address_book.get_record_by_name(name)

            if contact is not None:
                days = contact.days_to_birthday()
                print(f"До дня народження залишилося {days} днів.")
            else:
                print(f"Контакт з ім'ям {name} не знайдений в адресній книзі.")

        elif command == 'save_to_file':
            file_handler = AddressBookFileHandler("address_book.json")
            file_handler.save_to_file(address_book)
            print("Адресну книгу збережено у файл.")

        elif command == 'load_from_file':
            file_handler = AddressBookFileHandler("address_book.json")
            loaded_address_book = file_handler.load_from_file()
            if loaded_address_book:
                print("Адресну книгу завантажено з файлу.")
                address_book = loaded_address_book
            else:
                print("Не вдалося завантажити адресну книгу з файлу.")

        elif command == 'exit':
            print('Goodbye!')
            break

        else:
            print(f'ТАКОЇ КОМАНДИ НЕ МАЄ. СПРОБУЙ ЩЕ РАЗ! \n{print_command_list()}')


if __name__ == "__main__":
    main()





