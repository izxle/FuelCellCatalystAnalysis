from os import path
from numpy import loadtxt, array
from numpy import max as npmax

class Folder(object):
    def __init__(self, path='', nams=[]):
        self.path = path
        self.nams = nams
        self._chkExt()
        self._getFiles()
        self._getCycles()

    def _getFiles(self):
        self.files = {}
        kw = {"skiprows": 1}
        if self.xls:
            kw["delimiter"] = ";"
        #loads data from every file as numpy array
        for nam in self.nams:
            self.files[nam] = {"data": 
                               loadtxt(path.join(self.path, nam), **kw)}

    def _chkExt(self):
        #to diferentiate extentions
        self.ext = self.nams[0][-4:]
        self._chkXls()

    def _chkXls(self):
        self.xls = self.ext==".xls"
    
    def _getCycles(self):
        #TODO: check fields from first line of file instead of ext
        # xls files have a cycle label so they're easier to process
        if self.xls:
            self._getCyclesFromXls()
        else:
            self._getCyclesFromElse()

    def _getCyclesFromXls(self):
        for nam in self.files.iterkeys():
            # potential, time, current, scan, index, we.potential
            data = self.files[nam]["data"]
            n = npmax(data[:, 3]) # get max scan number
            cycles = [[] for ix in range(n + 1)]
            for ditto in data:
                potential = ditto[5]
                current = ditto[2]
                scan = int(ditto[3])
                cycles[scan].append((potential, current))
            for ix in range(1, n + 1):
                cycles[ix] = array(cycles[ix])
                self.files[nam]["cycles"] = cycles

    def _getCyclesFromElse(self):
        for nam in self.files.iterkeys():
            # potential, current, time
            data = self.files[nam]["data"]
            cycles = [None, []]
            scan = 1
            fwd = True
            init = data[0][0] #first potential
            last = init
            for ditto in data:
                potential = ditto[0]
                current = ditto[1]
                time = ditto[2] #for later use
                #toggle fwd flag
                if not fwd:
                    #toggle fwd when changing direction
                    if (potential - last) > 0:
                        fwd = True
                    #if bkwrd and just past init, scan++
                    elif potential<=init and last>init:
                        scan += 1
                        cycles.append([])
                #toggle fwd when changing direction
                elif (potential - last) < 0:
                    fwd = False
                cycles[scan].append((potential, current))
                last = potential
            for ix in range(1, len(cycles)+1):
                cycles[ix] = array(cycles[ix])
            self.files[nam]["cycles"] = cycles
