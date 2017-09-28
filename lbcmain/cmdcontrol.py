class Command(object):
    """deal with user input"""
    
    def __init__(self, monitor):
        super(Command, self).__init__()
        self.monitor = monitor
        
    def activate(self):
        while True:
            cmdstr = raw_input()
            if cmdstr == "exit":
                self.monitor.stop()
                break
            else:
                print 'Unknown command'


