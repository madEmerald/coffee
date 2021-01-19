import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect("coffee.db")
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

    def closeEvent(self, event):
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())
