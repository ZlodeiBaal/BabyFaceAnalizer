from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import os,io
import cv2, time




class BOT:
    ChatArray = []
    RequestForPhoto = []
    RequestForState = []
    THISBOT = ''
    Warm_up = True
    def __init__(self):
        file1 = open('tg_creedential.txt', 'r')
        if (os.path.isfile('SpamAdress.txt')):
            with open('SpamAdress.txt') as f:
                for line in f:
                    line_s = line.strip().split(':')
                    self.ChatArray.append([int(line_s[0]),int(line_s[1])])
        models_list = file1.readlines()
        REQUEST_KWARGS = {
            'proxy_url': models_list[1].strip(),
            'urllib3_proxy_kwargs': {
                    'username': models_list[2].strip(),
                    'password': models_list[3].strip(),
                 }
        }
        updater = Updater(models_list[0].strip(), request_kwargs=REQUEST_KWARGS)
        dp = updater.dispatcher
        self.THISBOT = updater.bot
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("CurrentState", self.Status))
        dp.add_handler(CommandHandler("CurrentPhoto", self.Photo))
        dp.add_handler(CommandHandler("NO_FACE_start", self.reg_face_visibility))
        dp.add_handler(CommandHandler("NO_FACE_stop", self.del_face_visibility))
        dp.add_handler(CommandHandler("MOD_start", self.reg_face_mood_change))
        dp.add_handler(CommandHandler("MOD_stop", self.del_face_mood_change))
        dp.add_handler(CommandHandler("Wake_up_start", self.reg_sleep_change))
        dp.add_handler(CommandHandler("Wake_up_stop", self.del_sleep_change))
        dp.add_handler(CommandHandler("Eyes_opened_start", self.reg_eye_opened))
        dp.add_handler(CommandHandler("Eyes_opened_stop", self.del_eye_opened))
        updater.start_polling()

    def RewriteChat(self):
        if (os.path.isfile('SpamAdress.txt')):
            os.remove('SpamAdress.txt')
        fw = open('SpamAdress.txt', 'a')
        for (chat_id, mod) in self.ChatArray:
            fw.write(str(chat_id) +':'+ str(mod)+ '\n')
        fw.close()

    def ReleaseRequests(self, SM, img):
        self.Warm_up = False
        if len(self.RequestForState)!=0:
            if SM.IsFaceStableSeen:
                state = "Face stable seen"
            else:
                state = "Face unseen"
            if len(SM.FrameList)>0:
                state+=' '+SM.FrameList[-1].Emotion
                if SM.EyesOpened==1:
                    state+=' Opened'
                else:
                    state += ' Not Opened'
            state += ' '+str(len(SM.FrameList))
            state += ' ' + str(SM.disp_main)
            while len(self.RequestForState)!=0:
                chat_id = self.RequestForState[0]
                self.RequestForState.pop(0)
                self.THISBOT.sendMessage(chat_id,state)
        if len(self.RequestForPhoto)!=0:
            is_success, buffer = cv2.imencode(".jpg", img)
            if is_success:
                try:
                    io_buf = io.BytesIO(buffer)
                    while len(self.RequestForPhoto) != 0:
                        chat_id = self.RequestForPhoto[0]
                        self.RequestForPhoto.pop(0)
                        self.THISBOT.sendPhoto(chat_id, io_buf)
                except:
                    print('Fail to send image')
        if SM.Pending_for_alarm:
            SM.Last_Time_sent=time.time()
            SM.Pending_for_alarm = False
            while len(SM.alarm_type)!=0:
                for (chat_id,mod) in self.ChatArray:
                    if SM.alarm_type[0]==mod:
                        if mod==0:
                            self.THISBOT.sendMessage(chat_id, 'FaceLost')
                        if mod == 1:
                            self.THISBOT.sendMessage(chat_id, SM.Emo_alarm)
                        if mod == 2:
                            self.THISBOT.sendMessage(chat_id, "Машет головой!")
                        if mod == 3:
                            self.THISBOT.sendMessage(chat_id, "ГЛАЗА ОТКРЫТЫ!")
                SM.alarm_type.pop(0)



    def start(self, bot, update):

        update.message.reply_text('Current commands: \n /CurrentPhoto \n /CurrentState \n /NO_FACE_start \n'
                                  ' /NO_FACE_stop \n /MOD_start \n'
                                  ' /MOD_stop \n /Wake_up_start \n /Wake_up_stop \n /Eyes_opened_start \n /Eyes_opened_stop')

    def Status(self,bot,update):
        if not self.Warm_up:
            self.RequestForState.append(update.message.chat_id)

    def Photo(self,bot,update):
        if not self.Warm_up:
            self.RequestForPhoto.append(update.message.chat_id)

    def reg_face_visibility(self, bot, update):
        mod = 0
        update.message.reply_text("Для отмены: /NO_FACE_stop")
        self.register_user(bot,update,mod)

    def reg_face_mood_change(self, bot, update):
        mod = 1
        update.message.reply_text("Для отмены: /MOD_stop")
        self.register_user(bot,update,mod)

    def reg_sleep_change(self, bot, update):
        mod = 2
        update.message.reply_text("Для отмены: /Wake_up_stop")
        self.register_user(bot,update,mod)

    def reg_eye_opened(self, bot, update):
        mod = 3
        update.message.reply_text("Для отмены: /Eyes_opened_stop")
        self.register_user(bot,update,mod)

    def del_eye_opened(self, bot, update):
        mod = 3
        self.delete_user(bot,update,mod)

    def del_sleep_change(self, bot, update):
        mod = 2
        self.delete_user(bot,update,mod)

    def del_face_visibility(self, bot, update):
        mod = 0
        self.delete_user(bot,update,mod)

    def del_face_mood_change(self, bot, update):
        mod = 1
        self.delete_user(bot,update,mod)

    def register_user(self, bot, update, mod):
        chat_id = update.message.chat_id
        if ([chat_id,mod] not in self.ChatArray):
            self.ChatArray.append([chat_id,mod])
            self.RewriteChat()


    def delete_user(self,bot, update, mod):
        chat_id = update.message.chat_id
        try:
            self.ChatArray.remove([chat_id,mod])
            update.message.reply_text("Отключено!")
            self.RewriteChat()
        except ValueError:
            update.message.reply_text("Функция уже была отключена!")




