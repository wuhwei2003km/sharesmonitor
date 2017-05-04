# -*- coding:utf-8 -*-
#!/usr/bin/env python
import os.path as osp
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

import dealrecord

class DealWindow:
    def __init__(self):
        self.builder=Gtk.Builder()
        self.builder.add_from_file("shareschild.glade")
        #signals and handler function to define a dict
        handlers={
                "on_childwindow_destroy":self.on_destroy,
                "on_imagemenuitem5_activate":self.on_menuitem5_activate,
                "on_imagemenuitem1_activate":self.on_Add_item,
                "on_imagemenuitem2_activate":self.on_Open_item,
                "on_imagemenuitem3_activate":self.on_Save_item,
                "on_imagemenuitem9_activate":self.on_Del_item,
                }
        self.builder.connect_signals(handlers)

        #define window and element
        self.window=self.builder.get_object("childwindow")
        self.sw=self.builder.get_object("scrolledwindow1")
        self.treeview=self.builder.get_object("treeview1")
        self.filedialog=self.builder.get_object("filechooserdialog1")
        self.filedialog.set_transient_for(self.window)
        self.filedialog.add_button(Gtk.STOCK_OK,Gtk.ResponseType.OK)
        self.filedialog.add_button(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)
        self.filesavedialog=self.builder.get_object("filechooserdialog2")
        self.filesavedialog.set_transient_for(self.window)
        self.filesavedialog.add_button(Gtk.STOCK_OK,Gtk.ResponseType.OK)
        self.filesavedialog.add_button(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)

        ffilter=Gtk.FileFilter()
        ffilter.set_name("xml")
        ffilter.add_mime_type("xml/xml")
        ffilter.add_pattern("*.xml")
        self.filedialog.add_filter(ffilter)
        self.filesavedialog.add_filter(ffilter)

        for i,column_title in enumerate(["股票代码","股票名称","买入日期",
            "买入价格","买入数量","卖出日期","卖出价格","卖出数量"]):
            self.cell=Gtk.CellRendererText()
            column=Gtk.TreeViewColumn(column_title,self.cell,text=i)
            self.treeview.append_column(column)
            self.cell.set_property("editable",True)
            self.cell.connect("edited",self.text_edited,i)
        self.cell_gain=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("净收益额",self.cell_gain,text=8)
        self.treeview.append_column(column)

        self.liststore=Gtk.ListStore(str,str,str,str,str,str,str,str,str)
        self.treeview.set_model(self.liststore)
        self.window.show_all()

    def on_destroy(self,widget):
        self.window.hide()
        return

    def on_menuitem5_activate(self,widget):
        self.window.hide()
        return

    def text_edited(self,widget,path,text,column):
        self.liststore[path][column]=text

    def on_Add_item(self,widget):
        self.cell.set_visible(True)
        self.liststore.append(["new row","","","","","","","",""])
        return

    def on_Del_item(self,widget):
        selection=self.treeview.get_selection()
        model,treeiter=selection.get_selected()
        self.liststore.remove(treeiter)

    #菜单操作
    def on_Open_item(self,widget):
        self.filedialog.set_title('Open xml file')
        self.filedialog.action=Gtk.FileChooserAction.OPEN
        response=self.filedialog.run()
        if response==Gtk.ResponseType.OK:
            fname=self.filedialog.get_filename()

            if fname!=None:
                pdate=dealrecord.read_xml(fname)
                self.liststore.clear()
                for pd in pdate:
                    self.liststore.append([pd[0],pd[1],pd[2],pd[3],pd[4],pd[5],pd[6],pd[7],pd[8]])
        elif response==Gtk.ResponseType.CANCEL:
            pass

        self.filedialog.hide()
        return

    def on_Save_item(self,widget):
        self.filesavedialog.set_title('Save xml file')
        response=self.filesavedialog.run()
        if response==Gtk.ResponseType.OK:
            filename=self.filesavedialog.get_filename()

            iter=self.liststore.get_iter_first()
            gp_info=[]
            while iter!=None:
                gp_info.append([self.liststore.get_value(iter,0),
                    self.liststore.get_value(iter,1),
                    self.liststore.get_value(iter,2),
                    self.liststore.get_value(iter,3),
                    self.liststore.get_value(iter,4),
                    self.liststore.get_value(iter,5),
                    self.liststore.get_value(iter,6),
                    self.liststore.get_value(iter,7),
                    self.liststore.get_value(iter,8)])
                iter=self.liststore.iter_next(iter)
            dealrecord.write_xml(gp_info,filename)

        elif response==Gtk.ResponseType.CANCEL:
            pass

        self.filesavedialog.hide()
        return


if __name__=="__main__":
    deal=DealWindow()
    Gtk.main()
