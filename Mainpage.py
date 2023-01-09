
import pymysql as p
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from datetime import datetime
form_class = uic.loadUiType('./main.ui')[0]


class Main(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.Signal_login = False
        self.INFO_login = []
        self.conn = p.connect(host='localhost', port=3306, user='root', password='00000000',
                         db='beaconapp', charset='utf8')
        # 커서 획득
        self.c = self.conn.cursor()
        self.setupUi(self)
        self.login_id_lineEdit.setText("") # 아무것도입력안할시 오류나서 미리 설정해둠.
        self.Stack_W_login.setCurrentIndex(0)
        self.login_SW.setCurrentIndex(0)        # 스택위젯
        self.login_btn.clicked.connect(self.moveLoginPage)
        self.login_btn2.clicked.connect(self.login_Check)
        self.logout_btn.clicked.connect(self.logout)
        self.schedule_btn.clicked.connect(self.moveSchedulePage)
        self.chat_btn.clicked.connect(self.moveChattingPage)
        self.Mainpage_btn1.clicked.connect(self.moveMainpage)        # 로그인페이지-홈버튼
        self.Mainpage_btn2.clicked.connect(self.moveMainpage)        # 일정페이지 - 홈버튼
        self.Mainpage_btn3.clicked.connect(self.moveMainpage)        # 채팅페이지 - 홈버튼
        self.scheduleCalendar.clicked.connect(self.scheduleclick)
        self.Schedule_add.clicked.connect(self.moveScheduleAddPage)
        self.schedule_add_btn.clicked.connect(self.scheduleAdd)
        self.back_btn.clicked.connect(self.moveSchedulePage)
        self.back_btn2.clicked.connect(self.moveSchedulePage)
        self.Schedule_check.clicked.connect(self.moveScheduleViewPage)
        self.attend_btn.clicked.connect(self.moveAttendPage)
        self.training_btnSW.setCurrentIndex(0)
        self.training_btnSW2.setCurrentIndex(0)
        self.training_infoSW.setCurrentIndex(0)


    def moveAttendPage(self):
        self.login_SW.setCurrentIndex(6)
        self.traininginfocheck()
    def moveChattingPage(self):
        self.login_SW.setCurrentIndex(5)
    def moveSchedulePage(self):
        self.login_SW.setCurrentIndex(2)
    def moveScheduleViewPage(self):
        self.login_SW.setCurrentIndex(4)
        self.scheduleView()

    def moveMainpage(self):
        self.login_SW.setCurrentIndex(0)

    def moveLoginPage(self):
        self.login_SW.setCurrentIndex(1)


    def traininginfocheck(self):
        self.c.execute(f"select * from person_info where id_num = {self.id_num} and date = '2023-01-02'")
        traininginfo = self.c.fetchall()
        print(traininginfo)
        if traininginfo[0][2] == None:
            self.training_infoSW.setCurrentIndex(0)
            self.training_btnSW.setCurrentIndex(0)
            self.training_btnSW2.setCurrentIndex(0)
        elif traininginfo[0][2] !=None and traininginfo[0][3] == None :
            self.training_infoSW.setCurrentIndex(1)
            self.training_btnSW.setCurrentIndex(2)
            self.training_btnSW2.setCurrentIndex(1)
        elif traininginfo[0][2] !=None and traininginfo[0][3] != None :
            self.training_infoSW.setCurrentIndex(1)
            self.training_btnSW.setCurrentIndex(1)
            self.training_btnSW2.setCurrentIndex(0)
        elif traininginfo[0][2] !=None and traininginfo[0][4] != None :
            self.training_infoSW.setCurrentIndex(2)
            self.training_btnSW.setCurrentIndex(3)
            self.training_btnSW2.setCurrentIndex(0)

    def scheduleView(self):
        self.schedule_listView.clear()
        self.c.execute(f"SELECT * From Schedule Inner Join  person on person.id_num = schedule.id_num \
                        Where date = '{self.datestring}'")
        schedulelist = self.c.fetchall()
        print(schedulelist)
        for i in range(len(schedulelist)):
            self.schedule_listView.addItem(f'{schedulelist[i][8]}\n {schedulelist[i][2]}')

    #일정 선택
    def scheduleclick(self):
        self.date = self.scheduleCalendar.selectedDate()
        self.datestring = self.date.toString("yyyy-MM-dd")
        print(self.datestring)
        self.selectedDate_lbl1.setText(self.date.toString("yyyy-MM-dd"))
        self.selectedDate_lbl2.setText(self.date.toString("yyyy-MM-dd"))
    def moveScheduleAddPage(self):
        self.login_SW.setCurrentIndex(3)
    def scheduleAdd(self):
        schedule_contents = self.schedule_textEdit.toPlainText()
        self.c.execute(f"INSERT INTO Schedule VALUES ('{self.INFO_login[0][0]}','{self.datestring}','{schedule_contents}')")
        self.conn.commit()
        self.schedule_textEdit.clear()
        print("성공")
    # 로그인
    def login_Check (self):

        if self.login_id_lineEdit.text() == "":
            QMessageBox.critical(self, "로그인 오류", "정보를 입력하세요")
            return
        self.id = self.login_id_lineEdit.text()
        pw = self.login_pw_lineEdit.text()

        self.c.execute(f"SELECT * FROM person WHERE ID = '{self.id}' AND Password = '{pw}'")
        self. INFO_login = self.c.fetchall()
        print(self.INFO_login)
        self.id_num=self.INFO_login[0][0]
        self.student_name=self.INFO_login[0][5]
        now = datetime.now()
        date = now.date()
        if self.id not in self. INFO_login[0]:
            QMessageBox.critical(self, "로그인 오류", "ID 정보가 없습니다. 회원가입 해주세요")
        elif pw not in self. INFO_login[0]:
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 다시 입력하세요")
        elif pw == '' :
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 입력하세요")
        else :
            self.Signal_login = True
            self.login_SW.setCurrentIndex(0)
            self.login_id_lineEdit.clear()
            self.login_pw_lineEdit.clear()
            self.Stack_W_login.setCurrentIndex(1)
            self.logon_label.setText(f"{self.student_name}님 안녕하세요")
            print('성공')

            self.c.execute(f"Insert into person_info (id_Num,Name,Date,NameDate) values \
                            ({self.id_num},'{self.student_name}','{date}','{self.student_name}{date}')\
                            on duplicate key update Name = '{self.student_name}', Date = '{date}'")

    #로그아웃
    def logout(self):
        self.Signal_login = False
        self.Stack_W_login.setCurrentIndex(0)
        self.logon_label.setText("")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = Main()
    mainWindow.setFixedHeight(600)
    mainWindow.setFixedWidth(600)
    mainWindow.show()
    app.exec_()