# -*- coding:utf-8 -*-
#!/usr/bin/env python
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GObject,Notify
import time

import info_sys
import shareschild

class MainProgram(Gtk.Window):

    def __init__(self):
        #define variable
        self.button_onoff=0
        self.timedelay=5000
        self.timer=None
        self.notify=None
        self.alert_list=[]

        self.builder=Gtk.Builder()
        self.builder.add_from_file("shares_info.glade")
        #signals and handler function to define a dict
        handlers={
                "on_mainwindow_destroy":Gtk.main_quit,
                "on_imagemenuitem5_activate":Gtk.main_quit,
                "on_statusicon1_activate":self.on_status_activate,
                #cell add row and cell edit
                "on_imagemenuitem1_activate":self.on_Add_row,
                "on_imagemenuitem9_activate":self.on_Del_row,
                #menu
                "on_imagemenuitem2_activate":self.on_Open_file,
                "on_imagemenuitem3_activate":self.on_Save_file,
                "on_menuitem5_activate":self.on_dealrecord_activate,
                #button function
                "on_button1_clicked":self.on_monitor_button,
                }
        self.builder.connect_signals(handlers)
        #define window and elements
        self.mainwindow=self.builder.get_object("mainwindow")
        #状态栏
        self.statusicon=self.builder.get_object("statusicon1")
        self.statusicon.set_from_stock(Gtk.STOCK_GOTO_TOP)
        self.statusicon.set_tooltip_markup("markup")
        self.statusicon.set_tooltip_text("shares_info")
        self.sharetView=self.builder.get_object("treeview1")
        self.textview=self.builder.get_object("textview1")
        self.monitor_button=self.builder.get_object("button1")
        self.close_button=self.builder.get_object("button2")
        self.k_button=self.builder.get_object("button3")
        self.chan_button=self.builder.get_object("button4")

        #create treeview list
        self.cell_code=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("股票代码",self.cell_code,text=0)
        self.sharetView.append_column(column)
        self.cell_code.set_property("editable",True)
        self.cell_code.connect("edited",self.text_edited,0)

        self.cell_name=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("股票名称",self.cell_name,text=1)
        self.sharetView.append_column(column)
        self.cell_name.set_property("editable",True)
        self.cell_name.connect("edited",self.text_edited,1)

        self.cell_price=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("现价",self.cell_price,text=2)
        self.sharetView.append_column(column)

        self.cell_high=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("D_High",self.cell_high,text=3)
        self.sharetView.append_column(column)
        self.cell_high.set_property("editable",True)
        self.cell_high.connect("edited",self.text_edited,3)

        self.cell_low=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("D_Low",self.cell_low,text=4)
        self.sharetView.append_column(column)
        self.cell_low.set_property("editable",True)
        self.cell_low.connect("edited",self.text_edited,4)

        self.sharestore=Gtk.ListStore(str,str,str,str,str)
        self.sharetView.set_model(self.sharestore)
        #show window
        self.mainwindow.show_all()

    #status act define
    def on_status_activate(self,widget):
        if self.mainwindow.get_property('visible'):
            self.mainwindow.hide()
        else:
            self.mainwindow.present()

    #cell insert and delete and edit
    def on_Add_row(self,widget):
        self.cell_code.set_visible(True)
        self.sharestore.append(["new_row","","","",""])
        return
    def on_Del_row(self,widget):
        selection=self.sharetView.get_selection()
        treeiter=selection.get_selected()
        self.sharestore.remove(treeiter)
        return

    def text_edited(self,widget,path,text,column):
        self.sharestore[path][column]=text

    #menu response
    def on_Open_file(self,widget):
        self.sharestore.clear()
        pdate=info_sys.read_xml("stockinfo")
        for pd in pdate:
            self.sharestore.append([pd[0],pd[1],"",pd[2],pd[3]])
        return

    def on_Save_file(self,widget):
        iter=self.sharestore.get_iter_first()
        gp_info=[]
        while iter!=None:
            code=self.sharestore.get_value(iter,0)
            name=self.sharestore.get_value(iter,1)
            high=self.sharestore.get_value(iter,3)
            low=self.sharestore.get_value(iter,4)
            gp_info.append([code,name,high,low])
            iter=self.sharestore.iter_next(iter)
        info_sys.write_xml(gp_info,"stockinfo")
        return

    def on_dealrecord_activate(self,widget):
        deal=shareschild.DealWindow()

    def on_monitor_button(self,widget):
        if self.button_onoff==0:
            self.button_onoff=1
            self.monitor_button.set_label('停止监控')
            self.timer=GObject.timeout_add(self.timedelay,
                    self.time_progress)
        else:
            self.button_onoff=0
            self.monitor_button.set_label('开始监控')
            GObject.source_remove(self.timer)
            self.timer=None

    def time_progress(self):
        iter=self.sharestore.get_iter_first()
        self.code=[]
        while iter!=None:
            self.code.append([self.sharestore.get_value(iter,0)])
            iter=self.sharestore.iter_next(iter)

        #get gp_date
        code_list=[]
        for dp in self.code:
            gpcode=dp[0]
            code_list.append(info_sys.get_gpinfo(gpcode))

        #set liststore data
        iter=self.sharestore.get_iter_first()
        for item in code_list:
            self.sharestore.set_value(iter,2,item[2])
            iter=self.sharestore.iter_next(iter)

        #alert and price monitor
        iter=self.sharestore.get_iter_first()
        text=''
        alert_onoff=0
        while iter!=None:
            current=float(self.sharestore.get_value(iter,2))
            D_High=self.sharestore.get_value(iter,3)
            D_low=self.sharestore.get_value(iter,4)
            code=self.sharestore.get_value(iter,0)
            if D_High!="":
                D_High=float(D_High)
                if current>=D_High and (code in self.alert_list)==False:
                    text+=code+' '+str(current)+' price up to Decide_high '
                    alert_onoff=1
                    self.alert_list.append(code)
                if D_low!="":
                    D_low=float(D_low)
                    if current<=D_low and (code in self.alert_list)==False:
                        text+=code+' '+str(current)+' price down to Decide_low'
                        alert_onoff=1
                        self.alert_list.append(code)
            iter=self.sharestore.iter_next(iter)

        if text!='' and alert_onoff==1:
            textbuffer=self.textview.get_buffer()
            enditer=textbuffer.get_end_iter()
            logtext=time.strftime("%Y %m %d %H:%M:%S",time.localtime())+" "+text+'\n\t'
            textbuffer.insert(enditer,logtext,len(logtext))

            self.show_notify(text)
        return True

    #notify
    def show_notify(self,text):
        if self.notify==None:
            Notify.init("Share alert")
            self.notify=Notify.Notification.new('Alert!',text,'information')
            self.notify.set_urgency(2)
            self.notify.show()
        return


if __name__=='__main__':
    main=MainProgram()
    Gtk.main()
