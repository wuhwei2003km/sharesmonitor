#-*- coding:utf-8 -*-
#!/usr/bin/env python
from xml.dom.minidom import Document
from xml.dom import minidom
import base64

#write deal_recond file
def write_xml(pdata,filename):
    doc=Document()
    dealinfo=doc.createElement("RecordInfo")
    doc.appendChild(dealinfo)

    for pd in pdata:
        record=doc.createElement("Record")
        dealinfo.appendChild(record)

        stock=doc.createElement("Stock")
        stock.setAttribute("Code",base64.b64encode(pd[0]))
        stock.setAttribute("Name",base64.b64encode(pd[1]))
        record.appendChild(stock)

        buylist=doc.createElement("BuyInfo")
        buylist.setAttribute("price",base64.b64encode(pd[2]))
        buylist.setAttribute("Number",base64.b64encode(pd[3]))
        buylist.setAttribute("date",base64.b64encode(pd[4]))
        record.appendChild(buylist)

        selllist=doc.createElement("SellInfo")
        selllist.setAttribute("price",base64.b64encode(pd[5]))
        selllist.setAttribute("Number",base64.b64encode(pd[6]))
        selllist.setAttribute("time",base64.b64encode(pd[7]))
        record.appendChild(selllist)

        netgain=doc.createElement("NetGain")
        netgain.appendChild(doc.createTextNode(base64.b64encode(pd[8])))
        record.appendChild(netgain)

    f=file(filename,"w")
    doc.writexml(f)
    f.close
    return

#read deal_recond file
def read_xml(filename):
    pdate=[]
    doc=minidom.parse(filename)
    root=doc.documentElement

    ldata=root.getElementsByTagName("Record")
    for da in ldata:
        stocknode=da.getElementsByTagName("Stock")[0]
        buyinfonode=da.getElementsByTagName("BuyInfo")[0]
        sellinfonode=da.getElementsByTagName("SellInfo")[0]
        netgain=da.getElementsByTagName("NetGain")[0]

        if netgain.hasChildNodes():
            netgain_value=base64.b64decode(netgain.childNodes[0].nodeValue)
        else:
            netgain_value=""

        pdate.append([base64.b64decode(stocknode.getAttribute('Code')),
            base64.b64decode(stocknode.getAttribute('Name')),
            base64.b64decode(buyinfonode.getAttribute('price')),
            base64.b64decode(buyinfonode.getAttribute('Number')),
            base64.b64decode(buyinfonode.getAttribute('date')),
            base64.b64decode(sellinfonode.getAttribute('price')),
            base64.b64decode(sellinfonode.getAttribute('Number')),
            base64.b64decode(sellinfonode.getAttribute('time')),netgain_value])
    return pdate
if __name__=="__main__":
    #write_xml([["601628","中国人寿","23.45","500","2017-01-03","","","",""],
    #   ["601155","新城控股","","","","15.89","200","2017-03-06",""],
    #   ],"dealxml.xml")
    data=read_xml("dealxml.xml")
    print data
