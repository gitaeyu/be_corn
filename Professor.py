import pymysql as p
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui
from datetime import datetime
import time

form_class = uic.loadUiType('./main.ui')[0]


# 채팅 갱신 스레드
class Thread1(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while self.parent.MessageSignal:
            conn = p.connect(host='localhost', port=3306, user='root', password='00000000',
                             db='beaconapp', charset='utf8')
            c = conn.cursor()
            number = c.execute(f"select message.*,person.Name from message join person on message.id_number = person.id_num \
                            where (person.Name = '{self.parent.receiver}' and message.Receiver = '{self.parent.user_name}') or \
                            (message.Receiver = '{self.parent.receiver}'  and person.Name = '{self.parent.user_name}') order by time")
            chatlist = c.fetchall()
            conn.commit()
            conn.close()
            row = self.parent.chat_textBrowser.count()
            time.sleep(0.5)
            if number == row:
                continue
            else:
                self.parent.chat_textBrowser.clear()
                for i in chatlist:
                    self.parent.chat_textBrowser.addItem(f'{i[2]}\n \n {i[4]} : {i[1]}\n')
                self.parent.chat_textBrowser.scrollToBottom()
                time.sleep(0.3)
                self.parent.chat_textBrowser.scrollToBottom()

    def stop(self):
        self.quit()
        self.wait(100)  # 5000ms = 5s


# 채팅방 리스트 갱신 스레드
class Thread2(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while self.parent.chatroomSignal:
            conn = p.connect(host='localhost', port=3306, user='root', password='00000000',
                             db='beaconapp', charset='utf8')
            c = conn.cursor()
            number = c.execute(f"select a.* from (select message.*,person.name from message \
                            join person on message.id_number = person.id_num where (id_number, Time) \
                            in (select id_number, max(Time) as Time from message group by id_number)\
                            order by Time)  as a where receiver ='{self.parent.user_name}'")
            message_room_list = c.fetchall()
            conn.commit()
            conn.close()
            row = self.parent.message_list.count()
            time.sleep(0.5)
            if number == row:
                continue
            else:
                self.parent.message_list.clear()
                for i in message_room_list:
                    self.parent.message_list.addItem(f'{i[4]}\n {i[1]}')
                self.parent.message_list.scrollToBottom()

    def stop(self):
        self.quit()
        self.wait(100)  # 5000ms = 5s


# 채팅 알림 스레드
class Thread3(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while self.parent.signal:
            conn = p.connect(host='localhost', port=3306, user='root', password='00000000',
                             db='beaconapp', charset='utf8')
            c = conn.cursor()
            numofmessage = c.execute(f"select a.* from (select message.*,person.name from message \
                            join person on message.id_number = person.id_num \
                            where message.Receiver = '{self.parent.user_name}') as a")
            conn.commit()
            conn.close()
            prevnumofmessage = self.parent.numofmessage
            time.sleep(0.2)
            if numofmessage == prevnumofmessage:
                continue

            else:
                self.parent.numofmessage = numofmessage

                if self.parent.login_SW.currentIndex() == 5:
                    continue
                else:
                    self.parent.Notification_SW.setCurrentIndex(1)
                    time.sleep(5)
                    self.parent.Notification_SW.setCurrentIndex(0)

    def stop(self):
        self.quit()
        self.wait(100)


class Main(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.Signal_login = False
        self.INFO_login = []

        self.conn = p.connect(host='127.0.0.1', port=3306, user='root', password='00000000',
                              db='beaconapp', charset='utf8')
        # 커서 획득
        self.c = self.conn.cursor()
        self.setupUi(self)
        self.login_id_lineEdit.setText("")  # 아무것도입력안할시 오류나서 미리 설정해둠.
        self.Stack_W_login.setCurrentIndex(0)  # 스택위젯
        self.login_SW.setCurrentIndex(0)  # 스택위젯 - 초기화면
        self.training_btnSW.setCurrentIndex(0)
        self.training_btnSW2.setCurrentIndex(0)
        self.training_infoSW.setCurrentIndex(0)
        self.Notification_SW.setCurrentIndex(0)
        self.login_btn.clicked.connect(self.moveLoginPage)
        self.login_btn2.clicked.connect(self.login_Check)
        self.logout_btn.clicked.connect(self.logout)
        self.Mainpage_btn1.clicked.connect(self.moveMainpage)  # 로그인페이지-홈버튼
        self.Mainpage_btn2.clicked.connect(self.moveMainpage)  # 일정페이지 - 홈버튼
        self.Mainpage_btn3.clicked.connect(self.moveMainpage)  # 채팅페이지 - 홈버튼
        self.Mainpage_btn4.clicked.connect(self.moveMainpage)  # 출석페이지 - 홈버튼

        self.schedule_btn.clicked.connect(self.moveSchedulePage)
        self.scheduleCalendar.clicked.connect(self.scheduleclick)
        self.Schedule_add.clicked.connect(self.moveScheduleAddPage)
        self.schedule_add_btn.clicked.connect(self.scheduleAdd)
        self.back_btn.clicked.connect(self.moveSchedulePage)
        self.back_btn2.clicked.connect(self.moveSchedulePage)
        self.Schedule_check.clicked.connect(self.moveScheduleViewPage)

        self.attend_btn.clicked.connect(self.moveAttendPage)
        self.join_room_btn.clicked.connect(self.recordJointime)
        self.comeback_btn.clicked.connect(self.recordComebacktime)
        self.leave_btn.clicked.connect(self.recordLeavetime)
        self.out_btn.clicked.connect(self.recordExcursiontime)
        self.attendance_present_btn.clicked.connect(self.moveAtt_presentPage)
        self.back_btn3.clicked.connect(self.moveAttendPage)

        self.chat_btn.clicked.connect(self.moveChattingPage)
        self.chat_send.clicked.connect(self.sendMessage)
        self.chat_start_btn.clicked.connect(self.chat_start)
        self.see_chat_list_btn.clicked.connect(self.see_chatlist)
        self.message_list.clicked.connect(self.clickchatlist)
        self.Notification_lw.clicked.connect(self.gotochatting)
        self.consult_cb.hide()
        # 스레드 실행
        self.chat1 = Thread1(self)  # 채팅 메세지 갱신 스레드
        self.chat2 = Thread2(self)  # 채팅방 목록 갱신 스레드
        self.notification = Thread3(self)  # 채팅 알림 갱신 스레드

    # 새로운 메세지 알림이 왔을때 클릭시 새로운 메세지를 보낸 채팅방에 바로 들어가도록 해줌.
    def gotochatting(self):
        conn = p.connect(host='127.0.0.1', port=3306, user='root', password='00000000',
                         db='beaconapp', charset='utf8')
        c = conn.cursor()
        c.execute(f"select b.* from (select message.*,person.Name from message \
                        join person on message.id_number = person.id_num\
                        where message.Receiver = '{self.user_name}') as b \
                        order by time desc limit 1;")
        conn.commit()
        conn.close()
        tempinfo = c.fetchall()

        self.receiver = f'{tempinfo[0][4]}'  # chat_start() 에 필요한 정보 갱신
        self.login_SW.setCurrentIndex(5)  # 채팅 페이지로 이동
        self.chat_start()
        self.Notification_SW.setCurrentIndex(0)

    def clickchatlist(self):
        a = self.message_list.currentItem()  # 채팅방 리스트에서 고른 항목을 a라는 변수에 담고
        b = a.text()  # a의 텍스트를 받아
        self.receiver = b[0:3]  # b[0:3] 은 이름이다. 다만 이름이 2자거나 4자면 문제가 생김.. 수정이 필요한 부분.

    # 채팅페이지의 채팅방보기를 클릭하면 실행되는 기능으로 마지막 메세지를 기준으로 하여 리스트 생성하게 하려고 함.
    def see_chatlist(self):
        self.messageSW.setCurrentIndex(0)  # 채팅방 목록 보이게 함.
        self.refresh_message_list()  # 채팅방 리스트 갱신
        self.MessageSignal = False  # 스레드의 Run메서드의 While문을 멈추게하기 위하여 Signal을 False로 바꿈
        self.chat1.stop()  # 채팅 갱신 스레드 멈춤
        self.chatroomSignal = True  # 채팅방  갱신 스레드의 신호를 True로 바꿈
        self.chat2.start()  # 채팅방 갱신 스레드 시작

    # 채팅페이지의 상담 시작 버튼을 클릭하면 실행되는 기능으로 채팅창으로 이동하며 콤보박스의 이름에 따라 각 채팅방이 다른것처럼 보이게 함.
    def chat_start(self):
        # self.receiver 가 설정되지 않은 상태면 나타나는 메세지
        if self.receiver == '':
            QMessageBox.critical(self, "교수 정보 없음", "콤보박스를 선택하거나 채팅방을 더블클릭 해주세요")
            return
        self.messageSW.setCurrentIndex(1)  # 채팅페이지에서 채팅을 보여주는 페이지로 이동
        self.MessageSignal = True  # 채팅 갱신 스레드 시작을 위하여 조건줌
        self.chat1.start()  # 채팅 갱신 스레드 시작
        self.chatroomSignal = False  # 채팅방 갱신 스레드 종료를 위하여 조건을 줌
        self.chat2.stop()  # 채팅방 갱신 스레드 멈춤

    # 메세지를 보내는 기능으로 DB에 저장한다.
    def sendMessage(self):
        a = self.chat_lineEdit.text()
        if a == '':
            return
        now = datetime.now()
        chat_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.c.execute(f"Insert into message values ({self.id_num},'{a}','{chat_time}','{self.receiver}')")
        self.conn.commit()
        self.chat_lineEdit.clear()

    # 메세지를 불러오는 기능으로 접속한 ID와 Combobox 또는 채팅방 메세지 리스트의 Receiver가 누구냐에 따라 채팅방 불러옴.
    def refresh_chat_textBrowser(self):
        self.chat_textBrowser.clear()
        self.c.execute(f"select message.*,person.Name from message join person on message.id_number = person.id_num \
                            where (person.Name = '{self.receiver}' and message.Receiver = '{self.user_name}') or \
                            (message.Receiver = '{self.receiver}'  and person.Name = '{self.user_name}') order by time")
        chatlist = self.c.fetchall()
        for i in chatlist:
            self.chat_textBrowser.append(f'{i[2]}\n \n {i[4]} : {i[1]}\n')

    # 채팅방을 불러오는 기능
    def refresh_message_list(self):
        self.message_list.clear()
        self.c.execute(f"select a.* from (select message.*,person.name from message \
                        join person on message.id_number = person.id_num where (id_number, Time) \
                        in (select id_number, max(Time) as Time from message group by id_number)\
                        order by Time)  as a where receiver ='{self.user_name}'")
        message_room_list = self.c.fetchall()
        for i in message_room_list:
            self.message_list.addItem(f'{i[4]}\n {i[1]}')  # i[4]는 보낸사람의 이름 i[1]은 보낸사람의 마지막 메세지

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
        self.chatroomSignal = True
        self.chat2.start()

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
        # 스레드 중지를 위하여 설정
        self.MessageSignal = False
        self.chat1.stop()
        self.chatroomSignal = False
        self.chat2.stop()

    # 로그인 페이지로 이동
    def moveLoginPage(self):
        self.login_SW.setCurrentIndex(1)

    # 출결현황 페이지 - 쿼리문을 사용했어야 했는데 익숙치못해서 리스트 사용함. 조건문의 수정이 필요하다.
    def make_Att_present(self):

        progress_info = self.c.execute(f"select a.*,b.수업시간,b.시작시간 from person_info as a \
                        join class_schedule as b on a.Date = b.훈련일자 where a.id_num = {self.id_num} and a.Date != curdate()")

        attendance = self.c.execute(f"SELECT * from person_info \
                    where (((Excursion is not null and timediff(Leave_time,Entrance)-timediff(comeback,excursion) >040000) \
                    or (Excursion is null and timediff(Leave_time,Entrance) >040000) )and Entrance is not null and \
                    Leave_time is not null) and id_num = {self.id_num} and Date != curdate()")

        late = self.c.execute(f"SELECT * from person_info where (DATE_FORMAT(entrance, '%H:%i:%s')  > '09:20:59') \
                                and id_num = {self.id_num} and Date != curdate() and ((timediff(Leave_time,Entrance)>040000)\
                                or (timediff(Leave_time,Entrance)-timediff(Excursion,Comeback) >040000))")

        earlyleave = self.c.execute(f"SELECT * from person_info where DATE_FORMAT(Leave_time,'%H:%i:%s')  < '17:00:00' \
                                    and id_num = {self.id_num} and Date != curdate() \
                                    and (timediff(Leave_time,Entrance) > 040000 \
                                    or timediff(timediff(Leave_time,Entrance),timediff(Comeback,excursion)) > 040000)")

        out = self.c.execute(f"SELECT * from person_info where Excursion is not null and id_num = {self.id_num} \
                                and Date != curdate() and timediff(Leave_time,Entrance)-timediff(comeback,excursion) >040000")

        absence = self.c.execute(f"SELECT * from person_info where ((Excursion is not null \
                                and timediff(Leave_time,Entrance)-timediff(comeback,excursion) <040000) \
                                or timediff(Leave_time,Entrance) < 040000 or Entrance is null or Leave_time is null) \
                                and id_num = {self.id_num} and Date != curdate()")

        # for문에서 정해진 출결현황에 따라 라벨 및 프로그레스바 등을 바꿔줌.
        self.attendance_lbl.setText(f'{attendance}')
        self.late_lbl.setText(f'{late}')
        self.earlyleave_lbl.setText(f'{earlyleave}')
        self.out_lbl.setText(f'{out}')
        self.absence_lbl.setText(f'{absence}')
        attendance_ratio = attendance / 140
        self.my_attendance_ratio_lbl.setText(f'({round(attendance_ratio * 100, 2)}% \t {attendance}/140일)')
        self.my_attendance_ratio_pB.setValue(int(attendance_ratio * 100))
        progress_ratio = progress_info / 140
        self.process_progress_ratio_lbl.setText(f'({round(progress_ratio * 100, 2)}% \t {progress_info}/140일)')
        self.process_progress_ratio_pB.setValue(int(progress_ratio * 100))

    # 입실 시간 기록
    def recordJointime(self):
        now = datetime.now()

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
        if todaytraining == () :
            todaytraining_start = ''
            todaytraining_end = ''
        else :
            todaytraining_start = todaytraining[0][2]
            todaytraining_end = todaytraining[0][3]
        self.today_training_lbl.setText(f'{todaytraining_start} ~{todaytraining_end}')
        self.c.execute(f"select * from person_info where id_num = {self.id_num} and date = '{date}'")
        traininginfo = self.c.fetchall()

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

        for i in range(len(schedulelist)):
            self.schedule_listView.addItem(f'{schedulelist[i][8]}\n {schedulelist[i][2]}')

    # 일정 선택
    def scheduleclick(self):
        self.date = self.scheduleCalendar.selectedDate()
        self.datestring = self.date.toString("yyyy-MM-dd")

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

    # 로그인
    def login_Check(self):
        if self.login_id_lineEdit.text() == "":
            QMessageBox.critical(self, "로그인 오류", "정보를 입력하세요")
            return
        self.id = self.login_id_lineEdit.text()
        pw = self.login_pw_lineEdit.text()
        self.c.execute(f"SELECT * FROM person WHERE ID = '{self.id}'")
        self.INFO_login = self.c.fetchall()
        if self.INFO_login == ():
            QMessageBox.critical(self, "로그인 오류", "ID 정보가 없습니다. 회원가입 해주세요")
            return
        self.id_num = self.INFO_login[0][0]
        self.user_name = self.INFO_login[0][5]
        now = datetime.now()
        date = now.date()
        if pw == '':
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 입력하세요")
        elif pw not in self.INFO_login[0]:
            QMessageBox.critical(self, "로그인 오류", "비밀번호를 다시 입력하세요")
        else:
            self.Signal_login = True
            self.login_SW.setCurrentIndex(0)
            self.login_id_lineEdit.clear()
            self.login_pw_lineEdit.clear()
            self.Stack_W_login.setCurrentIndex(1)
            self.logon_label.setText(f"{self.user_name}님 안녕하세요")
            self.numofmessage = self.c.execute(f"select a.* from (select message.*,person.name from message \
                            join person on message.id_number = person.id_num \
                            where message.Receiver = '{self.user_name}') as a")

            self.c.execute(f"Insert into person_info (id_Num,Name,Date,NameDate) values \
                            ({self.id_num},'{self.user_name}','{date}','{self.user_name}{date}')\
                            on duplicate key update Name = '{self.user_name}', Date = '{date}'")
            self.conn.commit()
            self.signal = True
            self.notification.start()

    # 로그아웃
    def logout(self):
        self.Signal_login = False
        self.Stack_W_login.setCurrentIndex(0)
        self.logon_label.setText("")
        self.signal = False
        self.notification.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = Main()
    mainWindow.setFixedHeight(600)
    mainWindow.setFixedWidth(600)
    mainWindow.show()
    app.exec_()
