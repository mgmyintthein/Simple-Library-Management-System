import sys
import os
import random
sys.path.append('resources')
from sendingemail import MailSender
import time
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUi 
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication,QWidget,QStackedWidget,QFileDialog,QSplashScreen,QScrollArea,QVBoxLayout,QFormLayout,QGroupBox,QLabel,QTableView,QMessageBox
from PyQt5.QtSql import QSqlDatabase,QSqlTableModel
from PyQt5.QtGui import QFont

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "mycompany.myproduct.subproduct.version"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

db=QSqlDatabase("QSQLITE")
db.setDatabaseName(os.path.join(basedir,"resources/LibraryMS.db"))
db.open()

class SplashScreen(QSplashScreen):
    def __init__(self):
        super(QSplashScreen,self).__init__()
        loadUi(os.path.join(basedir,"resources/splashscreen.ui"),self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(600,400)
        self.setGeometry(QtCore.QRect(300, 170, 541, 421))
        #pixmap=QPixmap("lib1.jpg")
        #self.setPixmap(pixmap)
        
    def progress(self):
        for i in range(100):
            time.sleep(0.1)
            self.progressBar.setValue(i+1)

class BookList(QtWidgets.QMainWindow):
    def __init__(self):
        super(BookList,self).__init__()
        loadUi(os.path.join(basedir,'resources/booklist.ui'),self)
        self.searchline.textChanged.connect(self.update_filter)        
        self.model=QSqlTableModel(db=db)
        self.tableView.setModel(self.model)
        self.header = self.tableView.horizontalHeader()
        self.font = QFont()  # Create a QFont object
        self.font.setPointSize(14)  # Set the desired font size
        self.font.setBold(True)
        self.header.setFont(self.font)  # Apply the font to the header
        self.model.setTable("bookList")
        self.model.select()
        self.model.setSort(0, Qt.AscendingOrder)
        self.model.setEditStrategy(QSqlTableModel.OnRowChange)
        self.tableView.setColumnWidth(1,300)
        self.tableView.setColumnWidth(2,170)
        self.tableView.setColumnWidth(3,150)
        self.dashbutton.clicked.connect(self.gotoDashBoard)
        self.addBbut.clicked.connect(self.gotoAddBook)
        self.deleteBbut.clicked.connect(self.deleteSelectedRow)
        self.userlistbut.clicked.connect(self.gotoUserList)

    def gotoUserList(self):
        userlist=UserList()
        widget.addWidget(userlist)
        widget.setWindowTitle("LibraryMS User List")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)

    def deleteSelectedRow(self):
        # Get the selected row(s) indexes
        selected_indexes = self.tableView.selectedIndexes()

        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No row selected!")
            return

        # Get the unique rows to delete
        rows_to_delete = list(set(index.row() for index in selected_indexes))

        # Sort rows in descending order to delete from bottom to top without invalidating indices
        rows_to_delete.sort(reverse=True)

        # Delete rows from the database and the model
        for row in rows_to_delete:
            # Get the primary key or unique identifier from the database for deletion
            identifier = self.model.index(row, 0).data()  # Replace '0' with the index of the primary key column
            connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cursor = connection.cursor()
            # Execute a delete operation on the database
            cursor.execute(f"DELETE FROM bookList WHERE BookNo = ?;", (identifier,))
            connection.commit()

            # Remove the row from the model
            self.model.removeRow(row)
            connection.close()
        QMessageBox.warning(self,"Warning", "Deleted Successfully!")

    def gotoAddBook(self):
        addbook=Addbook()
        widget.addWidget(addbook)
        widget.setWindowTitle("LibraryMS Add Book")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)

    def update_filter(self, s):
        filter_str = 'Name LIKE "%{}%"'.format(s)
        self.model.setFilter(filter_str)

    def gotoDashBoard(self):
        dashboard=Dashboard()
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.setWindowTitle("LibraryMS Dashboard")
        widget.move(10,13)

class Addbook(QtWidgets.QMainWindow):
    def __init__(self):
        super(Addbook,self).__init__()
        loadUi(os.path.join(basedir,'resources/addbook.ui'),self)
        self.dashB.clicked.connect(self.gotoDashBoard)
        self.clearbut.clicked.connect(self.gotoClear)
        self.addBbut.clicked.connect(self.AddBook)

    def AddBook(self):
        if self.bookid.text()=="":
            return self.showtext.setText("Error! Please fill in all!")
        bookid=int(self.bookid.text())
        bname=self.bname.text()
        authname=self.authname.text()
        booked=self.booked.text()
        cover=None
        conn = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM bookList WHERE BookNo = ?", (bookid,))
        result = cursor.fetchone()
        conn.close()
        # Check the result to determine if the user ID exists
        if result[0] > 0:
            return self.showtext.setText(f"Error! This BookNo {bookid} is Exit.")
        else:
            pass
        if bookid=="" or bname=="" or authname=="" or booked=="":
            return self.showtext.setText("Error! Please fill in all!")
        else:
            connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bookList (BookNo, Name, Author, Edition,Cover) VALUES (?, ?, ?, ?,?)",
                   (bookid, bname, authname, booked,cover))
            connection.commit()
            connection.close()
            return self.showtext.setText("Successfully Finish!")
            

    def gotoClear(self):
        self.bookid.clear()
        self.bname.clear()
        self.authname.clear()
        self.booked.clear()
    def gotoDashBoard(self):
        dashboard=Dashboard()
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.setWindowTitle("LibraryMS Dashboard")
        widget.move(10,13)

class AddUser(QtWidgets.QMainWindow):
    def __init__(self):
        super(AddUser,self).__init__()
        loadUi(os.path.join(basedir,'resources/adduser.ui'),self)
        self.dashB.clicked.connect(self.gotoDashBoard)
        self.clearbut.clicked.connect(self.gotoClear)
        self.addUbut.clicked.connect(self.Addusr)

    def Addusr(self):
        if self.bookid.text()=="":
            return self.showtext.setText("Error! Please fill in all!")
        userid=int(self.bookid.text())
        usrname=self.bname.text()
        bookname=self.authname.text()
        date=self.booked.text()
        
        conn = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM userlist WHERE UserID = ?", (userid,))
        result = cursor.fetchone()
        conn.close()
        # Check the result to determine if the user ID exists
        if result[0] > 0:
            return self.showtext.setText(f"Error! This UserID {userid} is Exit.")
        else:
            pass
        if self.bookid.text()=="" or usrname=="" or bookname=="" or date=="":
            return self.showtext.setText("Error! Please fill in all!")
        else:           
            
            connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cursor = connection.cursor()
            cursor.execute("INSERT INTO userlist (UserID, Username, Bookname, Date) VALUES (?, ?, ?, ?)",
                   (userid, usrname, bookname, date))
            connection.commit()
            connection.close()
            return self.showtext.setText("Successfully Finish!")
            

    def gotoClear(self):
        self.bookid.clear()
        self.bname.clear()
        self.authname.clear()
        self.booked.clear()
    def gotoDashBoard(self):
        dashboard=Dashboard()
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.setWindowTitle("LibraryMS Dashboard")
        widget.move(10,13)

class UserList(QtWidgets.QMainWindow):
    def __init__(self):
        super(UserList,self).__init__()
        loadUi(os.path.join(basedir,'resources/userlist.ui'),self)
        self.searchline.textChanged.connect(self.update_filter)
        self.searchline2.textChanged.connect(self.update_filter2)  
        self.searchline3.textChanged.connect(self.update_filter3)      
        self.model=QSqlTableModel(db=db)
        self.tableView.setModel(self.model)
        self.header = self.tableView.horizontalHeader()
        self.font = QFont()  # Create a QFont object
        self.font.setPointSize(14)  # Set the desired font size
        self.font.setBold(True)
        self.header.setFont(self.font)  # Apply the font to the header
        self.model.setTable("userlist")
        self.model.select()
        self.model.setSort(0, Qt.AscendingOrder)
        self.model.setEditStrategy(QSqlTableModel.OnRowChange)
        self.tableView.setColumnWidth(1,300)
        self.tableView.setColumnWidth(2,300)
        self.tableView.setColumnWidth(3,170)
        self.dashbutton.clicked.connect(self.gotoDashBoard)
        self.addUbut.clicked.connect(self.gotoUser)
        self.deleteUbut.clicked.connect(self.deleteSelectedRow)
    def gotoUser(self):
        adduser=AddUser()
        widget.addWidget(adduser)
        widget.setWindowTitle("LibraryMS Add User")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)

    def deleteSelectedRow(self):
        # Get the selected row(s) indexes
        selected_indexes = self.tableView.selectedIndexes()

        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No row selected!")
            return

        # Get the unique rows to delete
        rows_to_delete = list(set(index.row() for index in selected_indexes))

        # Sort rows in descending order to delete from bottom to top without invalidating indices
        rows_to_delete.sort(reverse=True)

        # Delete rows from the database and the model
        for row in rows_to_delete:
            # Get the primary key or unique identifier from the database for deletion
            identifier = self.model.index(row, 0).data()  # Replace '0' with the index of the primary key column
            connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cursor = connection.cursor()
            # Execute a delete operation on the database
            cursor.execute(f"DELETE FROM userlist WHERE userid = ?;", (identifier,))
            connection.commit()
            # Remove the row from the model
            self.model.removeRow(row)
            connection.close()
        QMessageBox.warning(self,"Warning", "Deleted Successfully!")

    def update_filter(self, s):
        filter_str = 'Username LIKE "%{}%"'.format(s)
        self.model.setFilter(filter_str)
    def update_filter2(self, s):
        filter_str = 'Bookname LIKE "%{}%"'.format(s)
        self.model.setFilter(filter_str)
    def update_filter3(self, s):
        filter_str = 'Date LIKE "%{}%"'.format(s)
        self.model.setFilter(filter_str)
    
    def gotoDashBoard(self):
        dashboard=Dashboard()
        widget.addWidget(dashboard)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.setWindowTitle("LibraryMS Dashboard")
        widget.move(10,13)
        
class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super(Dashboard,self).__init__()
        loadUi(os.path.join(basedir,'resources/dashboard.ui'),self)
        self.setWindowTitle("LibraryMS Dashboard")
        self.booklistB.clicked.connect(self.bookList)
        self.addbookB.clicked.connect(self.addbook)
        self.addusrB.clicked.connect(self.gotoUser)
        self.bookbowB.clicked.connect(self.gotoUserList)
        self.aboutB.clicked.connect(self.About)
        self.bookloB.clicked.connect(self.Location)
    def Location(self):
        self.l1.setText("No Services for this function!")
        self.l2.clear()
        self.l3.clear()
    def About(self):
        self.l1.setText("=> LibraryMS V1.0.0 intend to manage library easily and simply.")
        self.l2.setText("=> LibraryMS V1.0.0 is developed by GenZ Tech & Edu.")
        self.l3.setText("=> Read user manual and discuss with developer to use this.")

    def gotoUser(self):
        adduser=AddUser()
        widget.addWidget(adduser)
        widget.setWindowTitle("LibraryMS Add User")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)
    def gotoUserList(self):
        userlist=UserList()
        widget.addWidget(userlist)
        widget.setWindowTitle("LibraryMS User List")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)

    def addbook(self):
        addbook=Addbook()
        widget.addWidget(addbook)
        widget.setWindowTitle("LibraryMS Add Book")
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        widget.move(10,13)


    def bookList(self):
        booklist=BookList()
        widget.addWidget(booklist)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(1350,650)
        #self.setGeometry(100,60,1000,800)
        widget.setWindowTitle("LibraryMS Book List")   
        widget.move(10,13)

        
class ForgetPg(QtWidgets.QDialog):
    def __init__(self):
        super(ForgetPg,self).__init__()   
        loadUi(os.path.join(basedir,'resources/forgetpwd.ui'),self)
        self.otptemp=0
        self.setWindowTitle("Forget Pawwsord")
        self.reqbut.clicked.connect(self.otprequestFun)
        self.tologintbut.clicked.connect(self.gotoLogIn)
        self.vefbut.clicked.connect(self.otpverifyFunction)

    def otpverifyFunction(self):
        otpcode=self.otpline.text()
        email=self.emailline.text()
        if otpcode=="":
            return self.showtext.setText("Please fill OTP code.")
        if otpcode== str(self.otptemp):
            connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cursor = connection.cursor()
            query = "SELECT username, password FROM signuptable WHERE email = ?"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            connection.close()
            if result is not None:
                name, password = result
                return self.showtext.setText(f"Username:{name} Password:{password}")
            else:
                return self.showtext.setText("Error")
        else:
            return self.showtext.setText("Invalid OTP code!")

    
    def gotoLogIn(self):
        loginpg=LoginScreen()
        widget.addWidget(loginpg)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(loginpg.size())
        widget.setWindowTitle("Login")

    def otprequestFun(self):
        email=self.emailline.text()
        if email=="":
            return self.showtext.setText("Please fill email.")

        connection = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM signuptable WHERE email = ?"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        connection.close()
        if result[0] > 0:
            
            otp = str(random.randint(100000, 999999))
            self.otptemp=otp
            plaintext = "Hello LyBMS Admin, \n" \
                        f"This is your OTP code {otp}.\n"
            ourmailsender = MailSender('yourSender@gmail.com', 'xxx xxx xxx xxx', ('smtp.gmail.com', 587))

            html = f"""Hello LyBMS Admin, <br>
                        This is your OTP code : {otp}.<br>
                        <b>LibraryMS</b>"""
            ourmailsender.set_message(plaintext, "OTP sending", "LibraryMS Creator", html)
            # Next, we set the recipient for our email. The recipients are always entered as a list (or tuple) even when
            # there is only one recipient
            ourmailsender.set_recipients([email])        # We're almost there! Now we just have to connect to the SMTP server using the account and address we specified when
            # we created our MailSender, and send the email.

            ourmailsender.connect()
            ourmailsender.send_all()
            return self.showtext.setText("The OTP is sent to email.")

        else:
            return self.showtext.setText("The email is not signuped.")
        
class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen,self).__init__()
        #self.setFixedSize(425,503)
        loadUi(os.path.join(basedir,'resources/loginqd.ui'),self)
        self.passline.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signbut.clicked.connect(self.gotoSignUp)
        self.logbut.clicked.connect(self.loginFunction)
        self.forgetbut.clicked.connect(self.forgpwFunction)

    def forgpwFunction(self):
        fog=ForgetPg()
        widget.addWidget(fog)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(fog.size())
        widget.setWindowTitle('Forget Password')

    def loginFunction(self):
        user=self.usrline.text()
        passw=self.passline.text()       
        
        if len(user)==0 or len(passw)==0 :
            self.showtext.setText("Input All Fields")
            self.usrline.clear()
            self.passline.clear()
            
        elif user==passw:
            self.showtext.setText("Username,Password should not be same!")
            self.usrline.clear()
            self.passline.clear()
        else :
            
            db = sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            c = db.cursor()
            login = c.execute("SELECT * from signuptable WHERE username = ? AND password = ?", (user, passw))

            if (len(login.fetchall()) > 0):
                mag =Dashboard()
                widget.addWidget(mag)
                widget.setCurrentIndex(widget.currentIndex()+1)
                widget.setFixedSize(1350,650)
                #self.setGeometry(100,60,1000,800)
                widget.setWindowTitle("LibraryMS Dashboard")   
                widget.move(10,13) 
            
            else:
                self.showtext.setText("Login Failed.")
                self.usrline.clear()
                self.passline.clear()

    def gotoSignUp(self):
        singuppg=SignUpPg()
        widget.addWidget(singuppg)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(singuppg.size())
        widget.setWindowTitle("Sign Up")

class SignUpPg(QDialog):
    def __init__(self):
        super(SignUpPg,self).__init__()
        loadUi(os.path.join(basedir,"resources/signupqd.ui"),self)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.logbut.clicked.connect(self.gotoLogIn)
        self.signbut.clicked.connect(self.signIn)

    def signIn(self):
        usrname=self.usrline1.text()
        email= self.emailline.text()
        passd=self.paswline.text()
        
        if len(usrname)==0 or len(email)==0 or len(passd)==0:
            self.usrline1.clear()
            self.emailline.clear()
            self.paswline.clear()
            self.showtext.setText("Please Fill in all input")
        elif len(passd) < 6 :
            self.usrline1.clear()
            self.emailline.clear()
            self.paswline.clear()
            self.showtext.setText("Password should be 6 character")
        elif usrname==passd or usrname==email or passd==email:
            self.showtext.setText("Username,Password should not be same!")
            self.usrline1.clear()
            self.emailline.clear()
            self.paswline.clear()
        else:
            conn=sqlite3.connect(os.path.join(basedir,'resources/LibraryMS.db'))
            cur=conn.cursor()
            user_info =[usrname,email,passd]
            cur.execute('INSERT INTO signuptable (username,email,password) VALUES(?,?,?)',user_info)
            conn.commit()
            conn.close()
            self.showtext.setText("Signup is successful")

    def gotoLogIn(self):
        loginpg=LoginScreen()
        widget.addWidget(loginpg)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedSize(loginpg.size())
        widget.setWindowTitle("Login") 
        

     
#main
app =QApplication(sys.argv)
app.setWindowIcon(QIcon(os.path.join(basedir, "resources", "lib.png")))
#print(os.path.join(basedir, "loginqd.ui"))

loginpg=LoginScreen()
widget=QStackedWidget()
splash=SplashScreen()
singuppg=SignUpPg()  
splash.show()
splash.progress()
    
splash.finish(widget)

widget.addWidget(loginpg)
widget.setWindowTitle("Login")
widget.setFixedSize(loginpg.size())

widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exit")