import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox

from addEditCoffeeForm import Ui_Dialog
from mainForm import Ui_MainWindow


class AddCoffeeForm(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.p = parent
        self.setupUi(self)
        self.roast.addItems(['Слабая', 'Средняя', 'Сильная', 'Высшая'])
        self.grind.addItems(['В зернах', 'Молотый'])
        self.pushButton.clicked.connect(self.add)

    def add(self):
        title, taste = self.sort.text(), self.taste.toPlainText()
        if title and taste:
            if self.grind.currentIndex():
                grind = 'TRUE'
            else:
                grind = 'FALSE'

            self.p.add_coffee(title, str(self.roast.currentIndex() + 1), grind, taste,
                              str(self.price.value()), str(self.price.value()))
        else:
            QMessageBox.warning(self, 'Ошибка',
                                'Заполните все формы.')


class UpdateCoffeeForm(QDialog, Ui_Dialog):
    def __init__(self, parent, id, title, roasting, grind, taste, price, volume):
        super().__init__(parent)
        self.p = parent
        self.id = id
        self.setupUi(self)

        self.roast.addItems(['Слабая', 'Средняя', 'Сильная', 'Высшая'])
        self.grind.addItems(['В зернах', 'Молотый'])

        self.sort.setText(title)
        self.roast.setCurrentIndex(roasting)
        self.grind.setCurrentIndex(grind)
        self.taste.setPlainText(taste)
        self.price.setValue(price)
        self.volume.setValue(volume)

        self.pushButton.clicked.connect(self.update)

    def update(self):
        title, taste = self.sort.text(), self.taste.toPlainText()
        if title and taste:
            if self.grind.currentIndex():
                grind = 'TRUE'
            else:
                grind = 'FALSE'

            self.p.update_coffee(self.id, title, str(self.roast.currentIndex() + 1), grind, taste,
                                 str(self.price.value()), str(self.price.value()))
        else:
            QMessageBox.warning(self, 'Ошибка',
                                'Заполните все формы.')


class DBSample(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addButton.clicked.connect(self.create_add_form)
        self.updateButton.clicked.connect(self.create_update_form)

        self.connection = sqlite3.connect("data/coffee.db")
        self.id = len(self.connection.cursor().execute('SELECT * FROM coffee').fetchall())
        self.show_data()

    def show_data(self):
        res = self.connection.cursor().execute('SELECT coffee.id, coffee.title, roastings.title, grind, '
                                               'taste, price, volume FROM coffee INNER JOIN roastings '
                                               'ON coffee.roasting = roastings.id').fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ИД', 'Название сорта', 'Степень обжарки',
                                                    'Помол', 'Вкус', 'Цена', 'Объём упаковки'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 3:
                    if elem == 'TRUE':
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem('Молотый'))
                    else:
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem('В зернах'))
                else:
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))

    def create_add_form(self):
        self.inst = AddCoffeeForm(self)
        self.inst.exec()

    def create_update_form(self):
        coffee = self.tableWidget.selectedItems()
        if coffee:
            row = coffee[0].row()
            id = self.tableWidget.item(row, 0).text()
            _, title, roasting, grind, taste, price, volume = self.connection.cursor().execute(
                'SELECT * FROM coffee WHERE id = ?', id).fetchall()[0]
            roasting = roasting - 1
            title, taste = str(title), str(taste)
            if grind == 'TRUE':
                grind = 1
            else:
                grind = 0

            self.inst = UpdateCoffeeForm(self, id, title, roasting,
                                         grind, taste, price, volume)
            self.inst.exec()
        else:
            # Если сеанс не выбран, выводим сообщение об ошибке
            QMessageBox.warning(self, 'Ошибка',
                                'Выберете товар.')

    def add_coffee(self, title, roasting, grind, taste, price, volume):
        con = self.connection.cursor()
        self.id += 1
        con.execute("INSERT OR REPLACE INTO coffee(id, title, roasting, grind, taste, price, volume)"
                    " VALUES(" + ', '.join('?' * 7) + ")",
                    (self.id, title, roasting, grind, taste, price, volume))
        self.connection.commit()
        self.show_data()

    def update_coffee(self, id, title, roasting, grind, taste, price, volume):
        con = self.connection.cursor()
        con.execute("UPDATE coffee SET"
                    " title = ?, roasting = ?, grind = ?, taste = ?, price = ?, volume = ? WHERE id = ?",
                    (title, roasting, grind, taste, price, volume, id))
        self.connection.commit()
        self.show_data()

    def closeEvent(self, event):
        self.connection.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = DBSample()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
