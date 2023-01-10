
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
        self.Mainpage_btn4.clicked.connect(self.moveMainpage)        # 출석페이지 - 홈버튼
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
        self.join_room_btn.clicked.connect(self.recordJointime)
        self.comeback_btn.clicked.connect(self.recordComebacktime)
        self.leave_btn.clicked.connect(self.recordLeavetime)
        self.out_btn.clicked.connect(self.recordExcursiontime)
        self.attendance_present_btn.clicked.connect(self.moveAtt_presentPage)
        self.back_btn3.clicked.connect(self.moveAttendPage)
    def moveAtt_presentPage(self):
        self.login_SW.setCurrentIndex(7)
        self.make_Att_present()
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
    # 출결현황 페이지
    def make_Att_present(self):
        self.c.execute(f"select a.*,b.수업시간,b.시작시간 from person_info as a join class_schedule as b on a.Date = b.훈련일자 where a.id_num = {self.id_num}")
        progress_info = self.c.fetchall()
        print(progress_info)

        attendance = 0
        late = 0
        earlyleave = 0
        out = 0
        absence = 0

        for i in progress_info:
            if i[3] == None or i[2] == None: # 퇴실 or 입실이 하나라도 안찍혔을때
                absence+=1 #결석
                continue
            seconds = (i[3] - i[2]).total_seconds()
            latetime = datetime.strptime('09:21:00', '%H:%M:%S') #지각시간
            temptime = i[2].strftime('%H:%M:%S')
            jointime = datetime.strptime(f'{temptime}','%H:%M:%S') #입실시간
            temptime = i[3].strftime('%H:%M:%S')
            leavetime = datetime.strptime(f'{temptime}','%H:%M:%S')
            earlyleavetime = datetime.strptime('17:00:00', '%H:%M:%S')
            if latetime < jointime : #지각시간 < 입실시간 하지만 퇴실시간은 있음.
                if seconds < 14400:
                    absence+=1
                    continue
                else :
                    late +=1
                    attendance +=1

            elif leavetime < earlyleavetime :
                if seconds < 14400:
                    absence+=1
                    continue
                else :
                    earlyleave += 1
                    attendance+=1
            else :
                if seconds < 14400:
                    absence+=1
                    continue
                else :
                    attendance +=1
            if i[5] != None :
                out +=1
        print(len(progress_info))
        print(attendance,late,earlyleave,out,absence)
        self.attendance_lbl.setText(f'{attendance}')
        self.late_lbl.setText(f'{late}')
        self.earlyleave_lbl.setText(f'{earlyleave}')
        self.out_lbl.setText(f'{out}')
        self.absence_lbl.setText(f'{absence}')
        attendance_ratio = attendance/140
        self.my_attendance_ratio_lbl.setText(f'({round(attendance_ratio*100,2)}% \t {attendance}/140일)')
        self.my_attendance_ratio_pB.setValue(int(attendance_ratio*100))
        progress_ratio = len(progress_info)/140
        self.process_progress_ratio_lbl.setText(f'({round(progress_ratio*100,2)}% \t {len(progress_info)}/140일)')
        self.process_progress_ratio_pB.setValue(int(progress_ratio*100))





    def recordJointime(self):
        now = datetime.now()
        print(now)
        date = now.date()
        jointime = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set entrance  = '{jointime}' where namedate = '{self.student_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()
    def recordLeavetime(self):
        now = datetime.now()
        date = now.date()
        leavetime = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set Leave_time  = '{leavetime}' where namedate = '{self.student_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()
    def recordExcursiontime(self):
        now = datetime.now()
        date = now.date()
        excursion = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set excursion  = '{excursion}'where namedate = '{self.student_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()
    def recordComebacktime(self):
        now = datetime.now()
        date = now.date()
        comeback = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set Comeback  = '{comeback}'where namedate = '{self.student_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()
    def traininginfocheck(self):

        now = datetime.now()
        date = now.date()
        self.c.execute(f"select * from class_schedule where 훈련일자 = '{date}'")
        todaytraining = self.c.fetchall()
        todaytraining_start = todaytraining[0][2].strftime("%H:%M:%S")
        todaytraining_end = todaytraining[0][3].strftime("%H:%M:%S")
        self.today_training_lbl.setText(f'{todaytraining_start} ~{todaytraining_end}')
        self.c.execute(f"select * from person_info where id_num = {self.id_num} and date = '{date}'")
        traininginfo = self.c.fetchall()
        print(traininginfo)

        if traininginfo[0][2] == None:
            self.training_infoSW.setCurrentIndex(0)
            self.training_btnSW.setCurrentIndex(0)
            self.training_btnSW2.setCurrentIndex(0)
            self.Join_lbl.setText('')
            self.Leave_lbl.setText('')
            self.Comeback_lbl.setText('')
            self.Out_lbl.setText('')

        elif traininginfo[0][2] !=None and traininginfo[0][3] == None:
            self.training_infoSW.setCurrentIndex(1)
            self.training_btnSW.setCurrentIndex(2)
            self.training_btnSW2.setCurrentIndex(1)
            self.Join_lbl.setText(f'{traininginfo[0][2].strftime("%H:%M:%S")}')
            self.Leave_lbl.setText('')
            if traininginfo[0][5] == None:
                self.Out_lbl.setText('')
                self.Comeback_lbl.setText('')
            else :
                self.Out_lbl.setText(f'{traininginfo[0][5].strftime("%H:%M:%S")}')
                self.training_btnSW.setCurrentIndex(1)
                self.training_btnSW2.setCurrentIndex(0)
                if traininginfo[0][4] == None :
                    self.Comeback_lbl.setText('')
                else :
                    self.Comeback_lbl.setText(f'{traininginfo[0][4].strftime("%H:%M:%S")}')
                    self.training_btnSW.setCurrentIndex(2)
                    self.training_btnSW2.setCurrentIndex(0)

        elif traininginfo[0][2] !=None and traininginfo[0][3] != None :
            self.training_infoSW.setCurrentIndex(2)
            self.training_btnSW.setCurrentIndex(3)
            self.training_btnSW2.setCurrentIndex(0)
            self.Join_lbl.setText(f'{traininginfo[0][2].strftime("%H:%M:%S")}')
            self.Leave_lbl.setText(f'{traininginfo[0][3].strftime("%H:%M:%S")}')
            if traininginfo[0][5] == None:
                self.Out_lbl.setText('')
                self.Comeback_lbl.setText('')
            else :
                self.Out_lbl.setText(f'{traininginfo[0][5].strftime("%H:%M:%S")}')
                if traininginfo[0][4] == None :
                    self.Comeback_lbl.setText('')
                else :
                    self.Comeback_lbl.setText(f'{traininginfo[0][4].strftime("%H:%M:%S")}')



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