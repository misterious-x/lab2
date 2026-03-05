from dataclasses import dataclass
from datetime import date
from tkinter import Tk, ttk, Button, Entry, Label, END, StringVar
import tkinter.messagebox as msgbox


@dataclass
class TemperatureMeasurement:
    date: date
    type_measure: str
    location: str
    value: float

def extract_strings(line: str) -> tuple[list[str], str]:
    strings = []

    while '"' in line:
        start = line.find('"')
        end = line.find('"', start + 1)

        strings.append(line[start + 1:end])
        line = line[:start] + line[end + 1:]

    return strings, line

def parse_date(date_str: str) -> date:
    year, month, day = map(int, date_str.split('.'))
    return date(year, month, day)

def parse_value(value_str: str) -> float:
    return float(value_str)

def parse_line(line: str) -> TemperatureMeasurement:
    strings, remaining_line = extract_strings(line)

    type_measure, location = strings

    parts = remaining_line.split()
    date_ = parse_date(parts[0])
    value = parse_value(parts[1])

    return TemperatureMeasurement(date_, type_measure, location, value)


def read_measurements_from_file(filename: str) -> list:
    with open(filename, 'r', encoding='utf-8') as f:
        return [parse_line(line.strip()) for line in f if line.strip()]


class TemperatureApp:
    def __init__(self, root, measurements):
        self.root = root
        self.root.title("Temperature Measurements")

        self.measurements = measurements

        self.tree = ttk.Treeview(root, columns=("date", "type", "location", "value"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor='center')
        self.tree.pack(fill='both', expand=True)

        self._add_controls()
        self._populate_tree()

    def _add_controls(self):
        Label(self.root, text="Дата (гггг.мм.дд):").pack()
        self.date_var = StringVar()
        Entry(self.root, textvariable=self.date_var).pack()

        Label(self.root, text="Режим работы:").pack()
        self.type_var = StringVar()
        Entry(self.root, textvariable=self.type_var).pack()

        Label(self.root, text="Место измерения:").pack()
        self.location_var = StringVar()
        Entry(self.root, textvariable=self.location_var).pack()

        Label(self.root, text="Значение:").pack()
        self.value_var = StringVar()
        Entry(self.root, textvariable=self.value_var).pack()

        Button(self.root, text="Добавить", command=self.add_measurement).pack(pady=5)
        Button(self.root, text="Удалить", command=self.delete_selected).pack(pady=5)

        Label(self.root, text="Путь файла:").pack()
        self.file_var = StringVar()
        Entry(self.root, textvariable=self.file_var).pack()

        Button(self.root, text="Открыть файл", command=self.open_file).pack(pady=5)

    def _populate_tree(self):
        for m in self.measurements:
            self.tree.insert('', END, values=self._measurement_to_tuple(m))
    
    def _delete_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _measurement_to_tuple(self, m: TemperatureMeasurement):
        return (m.date.strftime("%Y.%m.%d"), m.type_measure, m.location, f"{m.value:.2f}")

    def add_measurement(self):
        try:
            year, month, day = map(int, self.date_var.get().split('.'))
            date_ = date(year, month, day)
            type_ = self.type_var.get()
            location = self.location_var.get()
            value = float(self.value_var.get())

            m = TemperatureMeasurement(date_, type_, location, value)
            self.measurements.append(m)
            self.tree.insert('', END, values=self._measurement_to_tuple(m))
        except Exception as e:
            msgbox.showerror("Ошибка", f"Неверный ввод: {e}")

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        for item in selected_item:
            index = self.tree.index(item)
            self.tree.delete(item)
            del self.measurements[index]

    def open_file(self):
        try:
            FILE_NAME = self.file_var.get()
            self.measurements = read_measurements_from_file(FILE_NAME)
            self._delete_tree()
            self._populate_tree()
        except:
            msgbox.showerror("Неверный путь файла!")


if __name__ == "__main__":
    FILE_NAME = "measurements.txt"
    measurements = read_measurements_from_file(FILE_NAME)

    root = Tk()
    app = TemperatureApp(root, measurements)
    root.mainloop()