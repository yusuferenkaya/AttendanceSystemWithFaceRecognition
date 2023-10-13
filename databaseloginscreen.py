import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QMainWindow, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def login(self):
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user=self.username_edit.text(),
                password=self.password_edit.text(),
                database="facerecognition"
            )
            print("Login successful")
            self.accept()
        except mysql.connector.Error as e:
            print("Could not connect to database:", e)
            QMessageBox.warning(self, "Login Failed", "Could not log in to database. Please check your credentials.")


class MainWindow(QMainWindow):
    def __init__(self, mydb):
        super().__init__()
        self.setWindowTitle("Attendance Stats")
        self.mydb = mydb
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.user_combo_box = QComboBox()
        self.user_combo_box.currentTextChanged.connect(self.update_table)
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.count_label = QLabel()
        self.layout.addWidget(self.count_label)
        self.table_widget.setColumnCount(3)
        self.table_widget.setColumnWidth(2, 200)  # replace 200 with the desired width in pixels

        self.table_widget.setHorizontalHeaderLabels(['ID', 'Name', 'Date'])
        self.layout.addWidget(self.user_combo_box)
        self.layout.addWidget(self.table_widget)
        self.central_widget.setLayout(self.layout)
        self.update_combo_box()

    def update_combo_box(self):
        self.user_combo_box.clear()
        cursor = self.mydb.cursor()
        cursor.execute("SELECT DISTINCT name FROM log")
        result = cursor.fetchall()
        for row in result:
            self.user_combo_box.addItem(row[0])

    def update_table(self):
        current_text = self.user_combo_box.currentText()
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM log WHERE name=%s", (current_text,))
        result = cursor.fetchall()
        self.table_widget.setRowCount(len(result))
        for i, row in enumerate(result):
            for j, col in enumerate(row):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(col)))
        count = len(result)
        self.count_label.setText(f"Count of total attendances: {count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print("Logged in successfully")
        mydb = mysql.connector.connect(
            host="localhost",
            user=login_dialog.username_edit.text(),
            password=login_dialog.password_edit.text(),
            database="facerecognition"
        )
        main_window = MainWindow(mydb)
        main_window.show()
        sys.exit(app.exec_())
