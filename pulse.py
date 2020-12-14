#!/bin/python
import subprocess
import sys
import getopt

def run(cmd):
    process = subprocess.run(
        cmd.split(" "), 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    out = process.stdout.decode("utf-8")
    err = process.stderr.decode("utf-8")
    
    return out, err


class Sink():
    """
    """
    default = False
    # [left, right]
    volume = None
    name = None
    index = -1
    
    def __init__(self, index):
        self.index = int(index)
        
    def __str__(self):
        txt = "%d - %s" % (self.index, self.name)
        txt +=  " (default)" if self.isDefault() else ""
        return txt
    
    def isDefault(self):
        return self.default
        
        
        
        
def readSinks():
    out, err = run("pacmd list-sinks")
    
    sink_list = []
    cur_sink = None
    cur_isprop = False
    
    for l in iter(out.splitlines()):
        
        current_level = len(l) - len(l.lstrip())
        
        if( "index: " in l ):
            index = l[l.find(":")+1:]
            cur_sink = Sink(index)
            
            cur_sink.default = "*" in l
            
            sink_list.append(cur_sink)
            continue
        
        if( "properties: " in l):
            cur_isprop = True
            continue 
        
        
        if( "volume:" in l and not "base" in l):
            vol = l.replace("volume:", "")
            vol = vol.rsplit(",")
            
            for i in range(0, len(vol)):
                vol[i] = int((vol[i][:vol[i].find("%")])[-3:])
                
            cur_sink.volume = vol
            
            continue
        
        if( "device.product.name" in l and current_level == 2):
            name = l.lstrip()
            name = name[name.find("=")+1:]
            name = name.replace('"', '')
            
            cur_sink.name = name.lstrip()
            
            continue
        
    return sink_list
    
    
class Application:
    """
    """
    name = None
    index = -1
    
    def __init__(self, index):
        self.index = index
        
    def __str__(self):
        return "%d - %s" % (self.index, self.name)
        
        
        
def readApplications():
    out, err = run("pacmd list-sink-inputs")
        
    app_list = []
    curr_app = None
            
    for l in iter(out.splitlines()):
        
        if( "index:" in l ):
            index = int( l[l.find(":")+1:] )
            curr_app = Application(index)
            app_list.append(curr_app)
            
            continue
        
        if( "application.name" in l):
            name = l.lstrip()
            name = name[name.find("=")+1:]
            name = name.replace('"', '')
            
            curr_app.name = name
            
            continue
        
        
        
    return app_list    
        
        
def switchAllApplications(sinkIndex, app_list=None):
    if( app_list is None ):
        app_list = readApplications() 
        
    for app in app_list:
        out, err = run("pacmd move-sink-input %d %d" % (app.index, sinkIndex))
    
    setDefaultSink(sinkIndex)


def setDefaultSink(sinkIndex):
    run("pacmd set-default-sink %d" % (sinkIndex))



def main(argv):
    
    options = [
            "list-sinks", 
            "list-apps", 
            "default-sink",
            "setdefault=",
            "toggle",
            "help"
        ]
    
    try:
        opts, args = getopt.getopt(argv,"ld:t:h", options)
        
        for opt, arg in opts:
            
            if( options[0] in opt or "-l" in opt):
                for s in readSinks():
                    print(s)
                    
                return
            
            elif( options[1] in opt ):
                for a in readApplications():
                    print(a)
                    
                return
            
            elif( options[2] in opt ):                
                for s in readSinks():
                    if( s.default ):
                        print(s)
                        
                return
            
            elif( options[3][:-1] in opt or opt == "-d"):
                index = None
                try:
                    index = int(arg)
                except:
                    # arg is given as a sink name
                    for s in readSinks():
                        if( arg in s.name ):
                            index = s.index
                            
                if index != None:                            
                    switchAllApplications( index )
                else:
                    print("Sink not found under name or index = ", index) 
                    
                return True

            elif( options[4] in opt or opt == "-t"):
                
                toggleInputs = arg.split(",")

                # get default
                sinks = readSinks()
                def_sink = None
                for s_from in sinks:
                    if s_from.default:
                        def_sink = s_from
                
                toggleToSinkName = def_sink.name
                for i in range(len(toggleInputs)):
                    if toggleInputs[i] in def_sink.name:
                        toggleToSinkName = toggleInputs[i+1 if i+1 < len(toggleInputs) else 0]

                for s in sinks:
                    if toggleToSinkName in s.name:
                        switchAllApplications(s.index)
                        break

            elif( options[5] in opt or opt == "-h" ):
                print("pulse.py [options] [arg]")
                print("Options:")
                print("\t --list-sinks or -l")
                print("\t --list-apps")
                print("\t --default-sink")
                print("\t --setdefault= or -d with substring of sink name")
                print("\t \t example: -d Hyper")
                print("\t --toggle or -t arg to toggle between given sinks")
                print("\t \t example: -t Hyper,Starship")
                print("\t --help or -h")
                
            
            
    except getopt.GetoptError:
        print('invalid arguments. run with --help')
        sys.exit(2)
    

main(sys.argv[1:])
