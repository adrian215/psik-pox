from threading import Thread

import pox.openflow.libopenflow_01 as of
from pox.core import core
from flask import Flask, jsonify

log = core.getLogger()

class Component (object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        print "Utworzono nowy komponent dla polaczenia: %s" % connection


    def _handle_ConnectionUp (self, event):
        print "Component odebral nowe polaczenie"

        # eth0  -   0 (controller)
        # eth1  -   1 (NAT)
        # eth2  -   2 (NAT)
        # eth3  -   3 (h1)
        # eth4  -   4 (h2)

        #Domyslnie wszystkie polaczenia ida bez zmian
        self.flowFromPortToPort(1, [3])
        self.flowFromPortToPort(3, [1])

        #Ruch pomiedzy snifferem2 a controllerem
        self.flowFromPortToPort(2, [4])
        self.flowFromPortToPort(4, [2])

        #Dla zapytan http ruch jest przekierowany do sniffera
        self.flowFromPortToPort(1, [3, 4], priority=2, tpSrc=80)
        self.flowFromPortToPort(3, [1, 4], priority=2, tpDst=80)



    def flowFromPortToPort(self, fromPort, toPorts, priority = 1,
                           tpSrc = None, tpDst = None):
        msg = of.ofp_flow_mod()
        msg.match.in_port = fromPort

        if tpSrc is not None:
            self.setTcpMatch(msg)
            msg.match.tp_src = tpSrc
        if tpDst is not None:
            self.setTcpMatch(msg)
            msg.match.tp_dst = tpDst

        msg.priority = priority
        for toPort in toPorts:
            msg.actions.append(of.ofp_action_output(port=toPort))
        self.connection.send(msg)
        print "Przeplyw: {0}:{1} \t -> \t {2}:{3} \t priorytet: {4}"\
            .format(fromPort, tpSrc, toPorts, tpDst, priority)

    def blockIp(self, ip):
        msg = of.ofp_flow_mod()
        msg.priority = 4
        msg.match.dl_type = 0x800
        msg.match.nw_src = of.IPAddr(ip)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 4
        msg.match.dl_type = 0x800
        msg.match.nw_dst = of.IPAddr(ip)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
        self.connection.send(msg)

        print "Ip %s blocked" % ip

    def setTcpMatch(self, msg):
        msg.match.dl_type = 0x800
        msg.match.nw_proto = 6


def launch():
    components = []

    print "Stworzono serwer"
    app = Flask("app")

    def start_c(event):
        print "Nowe polaczenie!"
        component = Component(event.connection)
        # component.blockIp("213.180.141.140")
        components.append(component)


    def startServer():
        print "Uruchamianie serwera"
        app.run(host='0.0.0.0')

    @app.route("/<block>")
    def request(block):
        for component in components:
            component.blockIp(block)
        print "Zablokowano ip %s" % block
        return "OK"

    core.openflow.addListenerByName("ConnectionUp", start_c)

    thread = Thread(target=startServer)
    thread.daemon = True
    thread.start()
