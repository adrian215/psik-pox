import pox.openflow.libopenflow_01 as of
from pox.core import core

log = core.getLogger()

class Component (object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        print "Utworzono nowy komponent dla polaczenia: %s" % connection

#     def _handle_PacketIn (self, event):
#         print "Odebrano %s" % event.ofp
#         packet = event.parsed
#         # packet = event.parsed.find("tcp")
#         # if packet != None:
#         #     self.handleTcpPacket(packet)
# # msg.actions.append(of.ofp_action_output(port = 3))
#         # msg = of.ofp_packet_out()
#         # msg.buffer_id = event.ofp.buffer_id# msg.actions.append(of.ofp_action_output(port = 3))
#         # msg.data = event
#         # # action = of.ofp_action_output(port = of.OFPP_FLOOD)# msg.actions.append(of.ofp_action_output(port = 3))
#         # # msg.actions.append(action)
#         print "Adres docelowy: %s" % event.nw_dst
#         msg = of.ofp_flow_mod()
#         msg.match = of.ofp_match.from_packet(packet)
#         msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
#         print "dodano przeplyw"
#
#         self.connection.send(msg)

    def _handle_ConnectionUp (self, event):
        print "Component odebral nowe polaczenie"

        # eth0      - 0
        # eth1      - 1
        # eth2      - 2
        # eth3 (h1) - 3
        # eth4 (h2) - 4

        #Wymiana informacji pomiedzy kontrolerem a snifferem
        self.flowFromPortToPort(3, [1])

        #Domyslnie wszystkie polaczenia ida bez zmian
        self.flowFromPortToPort(1, [3])
        self.flowFromPortToPort(3, [1])

        #Dla hosta h2
        self.flowFromPortToPort(2, [4])
        self.flowFromPortToPort(4, [2])

        #Dla zapytan http ruch jest przekierowany do sniffera
        self.flowFromPortToPort(1, [3, 4], priority=2, tpSrc=80)
        self.flowFromPortToPort(3, [1, 4], priority=2, tpDst=80)

        #Ruch pomiedzy hostem a controllerem


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

    def setTcpMatch(self, msg):
        msg.match.dl_type = 0x800
        msg.match.nw_proto = 6


def launch():

    def start_c(event):
        print "Nowe polaczenie!"
        component = Component(event.connection)

        # flowFromPortToPort(event, 2, 3)
        # flowFromPortToPort(event, 3, 2)
        #
        # fr = 2
        # to = 3
        # cp = 4
        #
        # msg = of.ofp_flow_mod()
        # # msg.match.in_port = fr
        # msg.match.tp_dst = 8088
        # msg.priority = 2
        # msg.actions.append(of.ofp_action_output(port=to))
        # msg.actions.append(of.ofp_action_output(port=cp))
        # event.connection.send(msg)

        # msg.actions.append(of.ofp_action_output(port = 2))
        # msg.actions.append(of.ofp_action_output(port = 3))
        # msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))

    core.openflow.addListenerByName("ConnectionUp", start_c)

