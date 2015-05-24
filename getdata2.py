import glob
from re import split as resplit
import matplotlib.pyplot as plt
import numpy as np
    
    
reSep = "\s+"
pat = "\x00" #some txt hav it @ end

#TODO: maybe add a File class: getdata, getcycles, graph

#for files from AutoLab
class Folder(object):
    def __init__(self, fpath='', files=[], ext='.txt', verb=True):
        """
        get data from files from path of folder
        """
        self.verb = verb
        self.ext = ext
        self.fpath = fpath
        if self.verb>2: print self.fpath
        self.files = {nam.lstrip(self.fpath): {'cycles': None} for nam in (
                            self._getFiles() if not files else files)}
        if self.verb>1: print self.files
        self._getData()
        self._getCycles()
    
    def _getFiles(self):
        #TODO: exclude folders
        files = glob.glob(self.fpath + '/*' + self.ext)
        if self.verb>2: print files
        return files
    
    def getFiles(self):
        return [self.fpath + nam for nam in self.files]
        
    def getNams(self):
        return self.files.keys()
        
    def _readFile(self, path):
        #get data from file to float array skipping first row
        #deleted keys, not used
        kw = {'skiprows':1}
        if '.xls' in self.ext:
            kw['delimiter'] = ';'
        try:
            if self.verb: print "Loading", path.lstrip(self.fpath),
            data = np.loadtxt(path, **kw)
            if self.verb: print "... done."
        except Exception, e:
            if self.verb: print
            print e, '1234123412342341'
        #TODO: maybe chk 4 mas str
        return data

    def _getData(self):
        for path in self.getFiles():
            nam = path.lstrip(self.fpath)
            try:
                #mark data?
                self.files[nam]['data'] = self._readFile(path)
            except:
                if self.verb: print ".. deleting."
                del self.files[nam]
    
    def _getCycles(self):
        if self.verb: print "file   cycles"
        for nam in self.files:
            data = self.files[nam]["data"]
            #TODO: mejorar
            cycles = {}            
            if '.xls' in self.ext:
                #TODO: get headers y unpack appropriately
                try:
                    #TODO: unfold cn numpy, cut data & apply ranges 4 scans
                    for potential, time, current, scan, index, wepotential in data:
                        cycles.update({int(scan): cycles.get(eint(scan), []) + [(wepotential, current)]})
                except ValueError :
                    pass
            else:
                scan = 1
                #TODO: chk fwd
                #TODO: mejorar, xtra cycle
                fwd = True #needed?
                init = data[0][0] #first potential
                last = init
                ####
                for potential, current, time in data:
                    #toggle fwd flag
                    if not fwd:
                        if (potential - last) > 0: fwd = True
                        #if bkwrd y just past init, scan++
                        elif potential<=init and last>init: scan += 1
                    elif (potential - last) < 0:
                        fwd = False
                    #TODO: better way?
                    #cycles.update({int(scan): cycles.get(int(scan), []) + [(potential, current)]})
                    #append potencial, corriente
                    try: cycles[scan].append((potential, current))
                    #if no key, crear
                    except KeyError: cycles[scan] = [(potential,current)]
                    last = potential
            for k in cycles: cycles[k] = np.array(cycles[k])
            self.files[nam]["cycles"] = cycles
            #fix vvv
            if self.verb: print nam[-17:-10], scan if '.xls' in self.ext else scan-1
    
    def getCycles(self, nam, last=False):
        if last:
            cycle = len(self.files[nam]["cycles"].keys())-1
            return self.files[nam]["cycles"][cycle]
        else:
            return self.files[nam]["cycles"]
#        try:
#            #TODO: mejorar
#            if last:
#                cycle = len(self.files[nam]["cycles"].keys())-1
#                return self.files[nam]["cycles"][cycle]
#            else:
#                return self.files[nam]["cycles"]
#        except Exception, e:
#            print e
#            print nam
#            print self.files[nam]
#            print 'error', self.files.keys()
#
#
#..



#def graph(path):
#    keys, data = readFile(path)
#    plt.figure()
#    plt.plot(*zip(*data))
#    plt.show()

#module stuff ?????
if __name__=="__main__":
    pass
else:
    pass
    #del resplit
    #del glob
    #del reSep
