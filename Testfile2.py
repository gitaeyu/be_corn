import pymysql as p
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui
from datetime import datetime
import time

form_class = uic.loadUiType('./main.ui')[0]


class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        while True:
            conn = p.connect(host='localhost', port=3306, user='root', password='00000000',
                                  db='beaconapp', charset='utf8')
            c = conn.cursor()
            number = c.execute(f"select message.*,person.Name from message join person on message.id_number = person.id_num \
                            where (person.Name = '{self.parent.receiver}' and message.Receiver = '{self.parent.user_name}') or \
                            (message.Receiver = '{self.parent.receiver}'  and person.Name = '{self.parent.user_name}')order by time")
            chatlist = c.fetchall()
            conn.commit()
            conn.close()
            row = self.parent.chat_textBrowser.count()
            if number == row :
                continue
            else :
                self.parent.chat_textBrowser.clear()
                for i in chatlist:
                    self.parent.chat_textBrowser.addItem(f'{i[2]}\n \n {i[4]} : {i[1]}\n')
                self.parent.chat_textBrowser.scrollToBottom()
                time.sleep(0.3)
                self.parent.chat_textBrowser.scrollToBottom()



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
        self.login_id_lineEdit.setText("")  # 아무것도입력안할시 오류나서 미리 설정해둠.
        self.Stack_W_login.setCurrentIndex(0)  # 스택위젯
        self.login_SW.setCurrentIndex(0)  # 스택위젯 - 초기화면
        self.login_btn.clicked.connect(self.moveLoginPage)
        self.login_btn2.clicked.connect(self.login_Check)
        self.logout_btn.clicked.connect(self.logout)
        self.schedule_btn.clicked.connect(self.moveSchedulePage)
        self.chat_btn.clicked.connect(self.moveChattingPage)
        self.Mainpage_btn1.clicked.connect(self.moveMainpage)  # 로그인페이지-홈버튼
        self.Mainpage_btn2.clicked.connect(self.moveMainpage)  # 일정페이지 - 홈버튼
        self.Mainpage_btn3.clicked.connect(self.moveMainpage)  # 채팅페이지 - 홈버튼
        self.Mainpage_btn4.clicked.connect(self.moveMainpage)  # 출석페이지 - 홈버튼
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
        self.chat_send.clicked.connect(self.sendMessage)
        self.chat_start_btn.clicked.connect(self.chat_start)
        self.see_chat_list_btn.clicked.connect(self.see_chatlist)
        self.message_list.clicked.connect(self.clickchatlist)
        self.Notification_SW.setCurrentIndex(0)
        # self.consult_cb.hide()
        self.chat1 = Thread1(self)
        self.consult_cb.currentIndexChanged.connect(self.consult_changed)

    def consult_changed(self):
        self.receiver = self.consult_cb.currentText()
    def clickchatlist(self):
        a = self.message_list.currentItem()
        b = a.text()
        self.receiver = b[0:3]

    # 채팅페이지의 채팅방보기를 클릭하면 실행되는 기능으로 마지막 메세지를 기준으로 하여 리스트 생성하게 하려고 함.
    def see_chatlist(self):
        self.messageSW.setCurrentIndex(0)
        self.refresh_message_list()

    # 채팅페이지의 상담 시작 버튼을 클릭하면 실행되는 기능으로 채팅창으로 이동하며 콤보박스의 이름에 따라 각 채팅방이 다른것처럼 보이게 함.
    def chat_start(self):
        if self.receiver == '':
            QMessageBox.critical(self, "교수 정보 없음", "콤보박스를 선택하거나 채팅방을 더블클릭 해주세요")
            return
        self.messageSW.setCurrentIndex(1)
        self.chat1.start()


    # 메세지를 보내는 기능으로 DB에 저장한다.
    def sendMessage(self):
        a = self.chat_lineEdit.text()
        if a == '':
            return
        now = datetime.now()
        chat_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"Insert into message values ({self.id_num},'{a}','{chat_time}','{self.receiver}')")
        self.conn.commit()

    # 메세지를 불러오는 기능으로 접속한 ID와 Combobox 또는 채팅방 메세지 리스트의 Receiver가 누구냐에 따라 채팅방 불러옴.
    def refresh_chat_textBrowser(self):
        self.chat_textBrowser.clear()
        self.c.execute(f"select message.*,person.Name from message join person on message.id_number = person.id_num \
                            where (person.Name = '{self.receiver}' and message.Receiver = '{self.user_name}') or \
                            (message.Receiver = '{self.receiver}'  and person.Name = '{self.user_name}') order by time")
        chatlist = self.c.fetchall()
        for i in chatlist:
            self.chat_textBrowser.append(f'{i[2]}\n \n {i[4]} : {i[1]}\n')

    # 채팅방을 불러오는 기능으로 아직 미완성
    def refresh_message_list(self):
        self.message_list.clear()
        self.c.execute(f"select a.* from (select message.*,person.name from message \
                        join person on message.id_number = person.id_num where (id_number, Time) \
                        in (select id_number, max(Time) as Time from message group by id_number)\
                        order by Time)  as a where receiver ='{self.user_name}'")
        message_room_list = self.c.fetchall()
        print(message_room_list)
        for i in message_room_list:
            self.message_list.addItem(f'{i[4]}\n {i[1]}')

    # 출결현황 페이지로 이동하며 출석 / 지각 등의 정보를 표시해준다.
    def moveAtt_presentPage(self):
        self.login_SW.setCurrentIndex(7)
        self.make_Att_present()

    # 비콘 출석페이지로 이동
    def moveAttendPage(self):
        if self.Signal_login == False:
            QMessageBox.critical(self, "로그인 정보 없음", "로그인해주세요")
            return
        if self.id_num > 90:
            QMessageBox.critical(self, "출석대상이 아님", "출석대상이 아닙니다")
            return
        self.login_SW.setCurrentIndex(6)
        self.traininginfocheck()

    # 채팅페이지로 이동
    def moveChattingPage(self):
        if self.Signal_login == False:
            QMessageBox.critical(self, "로그인 정보 없음", "로그인해주세요")
            return
        self.login_SW.setCurrentIndex(5)
        self.messageSW.setCurrentIndex(0)
        self.refresh_message_list()

    # 일정 페이지로 이동
    def moveSchedulePage(self):
        if self.Signal_login == False:
            QMessageBox.critical(self, "로그인 정보 없음", "로그인해주세요")
            return
        self.login_SW.setCurrentIndex(2)

    # 일정페이지 내에서 일정 보기로 이동
    def moveScheduleViewPage(self):
        self.login_SW.setCurrentIndex(4)
        self.scheduleView()

    # 메인페이지로 이동
    def moveMainpage(self):
        self.login_SW.setCurrentIndex(0)

    # 로그인 페이지로 이동
    def moveLoginPage(self):
        self.login_SW.setCurrentIndex(1)

    # 출결현황 페이지 - 쿼리문을 사용했어야 했는데 익숙치못해서 리스트 사용함. 조건문의 수정이 필요하다.
    def make_Att_present(self):
        self.c.execute(
            f"select a.*,b.수업시간,b.시작시간 from person_info as a join class_schedule as b on a.Date = b.훈련일자 where a.id_num = {self.id_num}")
        progress_info = self.c.fetchall()

        attendance = 0
        late = 0
        earlyleave = 0
        out = 0
        absence = 0

        for i in progress_info:
            if i[3] == None or i[2] == None:  # 퇴실 or 입실이 하나라도 안찍혔을때
                absence += 1  # 결석
                continue  # 그리고 다음날으로 넘어감
            seconds = (i[3] - i[2]).total_seconds()  # 퇴실시간에서 입실시간을 밴 시간
            latetime = datetime.strptime('09:21:00', '%H:%M:%S')  # 지각시간
            temptime = i[2].strftime('%H:%M:%S')
            jointime = datetime.strptime(f'{temptime}', '%H:%M:%S')  # 입실시간
            temptime = i[3].strftime('%H:%M:%S')
            leavetime = datetime.strptime(f'{temptime}', '%H:%M:%S')
            earlyleavetime = datetime.strptime('17:00:00', '%H:%M:%S')
            if latetime < jointime:  # 지각시간 < 입실시간 하지만 퇴실시간은 있음.
                if seconds < 14400:  # 있던 시간이 4시간보다 적으면 결석으로 처리해버림
                    absence += 1
                    continue  # 다음으로 넘어감
                else:
                    late += 1
                    attendance += 1

            elif leavetime < earlyleavetime:  # 퇴실시간이 정해진 시간보다 빠를때 조퇴로 체크
                if seconds < 14400:
                    absence += 1
                    continue
                else:
                    earlyleave += 1
                    attendance += 1
            else:
                if seconds < 14400:
                    absence += 1
                    continue
                else:
                    attendance += 1
            if i[5] != None:
                out += 1

        # for문에서 정해진 출결현황에 따라 라벨 및 프로그레스바 등을 바꿔줌.
        self.attendance_lbl.setText(f'{attendance}')
        self.late_lbl.setText(f'{late}')
        self.earlyleave_lbl.setText(f'{earlyleave}')
        self.out_lbl.setText(f'{out}')
        self.absence_lbl.setText(f'{absence}')
        attendance_ratio = attendance / 140
        self.my_attendance_ratio_lbl.setText(f'({round(attendance_ratio * 100, 2)}% \t {attendance}/140일)')
        self.my_attendance_ratio_pB.setValue(int(attendance_ratio * 100))
        progress_ratio = len(progress_info) / 140
        self.process_progress_ratio_lbl.setText(f'({round(progress_ratio * 100, 2)}% \t {len(progress_info)}/140일)')
        self.process_progress_ratio_pB.setValue(int(progress_ratio * 100))

    # 입실 시간 기록
    def recordJointime(self):
        now = datetime.now()
        print(now)
        date = now.date()
        jointime = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set entrance  = '{jointime}' where namedate = '{self.user_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()

    # 퇴실 시간 기록
    def recordLeavetime(self):
        now = datetime.now()
        date = now.date()
        leavetime = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set Leave_time  = '{leavetime}' where namedate = '{self.user_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()

    # 외출 시간 기록
    def recordExcursiontime(self):
        now = datetime.now()
        date = now.date()
        excursion = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set excursion  = '{excursion}'where namedate = '{self.user_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()

    # 복귀 시간 기록
    def recordComebacktime(self):
        now = datetime.now()
        date = now.date()
        comeback = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"update person_info set Comeback  = '{comeback}'where namedate = '{self.user_name}{date}'")
        self.conn.commit()
        self.traininginfocheck()

    # 당일 시간 기록에 따라 출결페이지의 버튼들의 stackwidget을 바꿔주고 라벨의 텍스트를 바꿔준다.
    def traininginfocheck(self):

        now = datetime.now()
        date = now.date()
        self.c.execute(f"select * from class_schedule where 훈련일자 = '{date}'")
        todaytraining = self.c.fetchall()
        todaytraining_start = todaytraining[0][2]
        todaytraining_end = todaytraining[0][3]
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

        elif traininginfo[0][2] != None and traininginfo[0][3] == None:
            self.training_infoSW.setCurrentIndex(1)
            self.training_btnSW.setCurrentIndex(2)
            self.training_btnSW2.setCurrentIndex(1)
            self.Join_lbl.setText(f'{traininginfo[0][2].strftime("%H:%M:%S")}')
            self.Leave_lbl.setText('')
            if traininginfo[0][5] == None:
                self.Out_lbl.setText('')
                self.Comeback_lbl.setText('')
            else:
                self.Out_lbl.setText(f'{traininginfo[0][5].strftime("%H:%M:%S")}')
                self.training_btnSW.setCurrentIndex(1)
                self.training_btnSW2.setCurrentIndex(0)
                if traininginfo[0][4] == None:
                    self.Comeback_lbl.setText('')
                else:
                    self.Comeback_lbl.setText(f'{traininginfo[0][4].strftime("%H:%M:%S")}')
                    self.training_btnSW.setCurrentIndex(2)
                    self.training_btnSW2.setCurrentIndex(0)

        elif traininginfo[0][2] != None and traininginfo[0][3] != None:
            self.training_infoSW.setCurrentIndex(2)
            self.training_btnSW.setCurrentIndex(3)
            self.training_btnSW2.setCurrentIndex(0)
            self.Join_lbl.setText(f'{traininginfo[0][2].strftime("%H:%M:%S")}')
            self.Leave_lbl.setText(f'{traininginfo[0][3].strftime("%H:%M:%S")}')
            if traininginfo[0][5] == None:
                self.Out_lbl.setText('')
                self.Comeback_lbl.setText('')
            else:
                self.Out_lbl.setText(f'{traininginfo[0][5].strftime("%H:%M:%S")}')
                if traininginfo[0][4] == None:
                    self.Comeback_lbl.setText('')
                else:
                    self.Comeback_lbl.setText(f'{traininginfo[0][4].strftime("%H:%M:%S")}')

    # 일정 보기 기능
    def scheduleView(self):
        self.schedule_listView.clear()
        self.c.execute(f"SELECT * From Schedule Inner Join  person on person.id_num = schedule.id_num \
                        Where date = '{self.datestring}'")
        schedulelist = self.c.fetchall()
        print(schedulelist)
        for i in range(len(schedulelist)):
            self.schedule_listView.addItem(f'{schedulelist[i][8]}\n {schedulelist[i][2]}')

    # 일정 선택
    def scheduleclick(self):
        self.date = self.scheduleCalendar.selectedDate()
        self.datestring = self.date.toString("yyyy-MM-dd")
        print(self.datestring)
        self.selectedDate_lbl1.setText(self.date.toString("yyyy-MM-dd"))
        self.selectedDate_lbl2.setText(self.date.toString("yyyy-MM-dd"))

    # 일정 추가 페이지로 이동
    def moveScheduleAddPage(self):
        self.login_SW.setCurrentIndex(3)

    # 일정 추가 기능
    def scheduleAdd(self):
        schedule_contents = self.schedule_textEdit.toPlainText()
        self.c.execute(
            f"INSERT INTO Schedule VALUES ('{self.INFO_login[0][0]}','{self.datestring}','{schedule_contents}')")
        self.conn.commit()
        self.schedule_textEdit.clear()
        print("성공")

    # 로그인
    def login_Check(self):

        if self.login_id_lineEdit.text() == "":
            QMessageBox.critical(self, "로그인 오류", "정보를 입력하세요")
            return
        self.id = self.login_id_lineEdit.text()
        pw = self.login_pw_lineEdit.text()

        self.c.execute(f"SELECT * FROM person WHERE ID = '{self.id}' AND Password = '{pw}'")
        self.INFO_login = self.c.fetchall()
        print(self.INFO_login)
        self.id_num = self.INFO_login[0][0]
        self.user_name = self.INFO_login[0][5]
        now = datetime.now()
        date = now.date()
        if self.id not in self.INFO_login[0]:
            QMessageBox.critical(self, "로그인 오류", "ID 정보가 없습니다. 회원가입 해주세요")
        elif pw not in self.INFO_login[0]:
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 다시 입력하세요")
        elif pw == '':
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 입력하세요")
        else:
            self.Signal_login = True
            self.login_SW.setCurrentIndex(0)
            self.login_id_lineEdit.clear()
            self.login_pw_lineEdit.clear()
            self.Stack_W_login.setCurrentIndex(1)
            self.logon_label.setText(f"{self.user_name}님 안녕하세요")
            print('성공')

            self.c.execute(f"Insert into person_info (id_Num,Name,Date,NameDate) values \
                            ({self.id_num},'{self.user_name}','{date}','{self.user_name}{date}')\
                            on duplicate key update Name = '{self.user_name}', Date = '{date}'")
            self.conn.commit()

    # 로그아웃
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
