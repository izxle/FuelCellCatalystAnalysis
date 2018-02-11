from glob import glob
from os import path

import numpy as np


# TODO: maybe add a File class: getdata, getcycles, graph

# for files from AutoLab
class Folder(object):
    def __init__(self, fpath='', filenames=[], ext='.txt', delimiter=' ', autolab=False, verb=True):
        """
        get data from files from path of folder
        """
        self.verb = verb
        self.ext = ext
        self.delimiter = delimiter
        self.autolab = autolab
        self.fpath = fpath
        # if self.verb>2: print self.fpath
        self.files = self.__getFiles(fpath, filenames)
        # if self.verb>1: print self.files
        self._getData()
        self._getCycles()

    def __getFiles(self, fpath, filenames):
        "returns"
        return {path.basename(filepath): {'cycles': None}
                for filepath in (filenames if filenames else self._getFiles())}

    def _getFiles(self):
        # TODO: exclude folders
        files = glob(path.join(self.fpath, f'*{self.ext}'))
        # TODO: insert filter 4 No files
        self.verb > 2 and print(files)
        return files

    def get_filepaths(self):
        return [path.join(self.fpath, filenames) for filenames in self.files]

    def getfilenames(self):
        return list(self.files.keys())

    def _readFile(self, filepath):
        # get data from file to float array skipping first row
        # deleted keys, not used
        kw = {'skiprows': 1,
              'delimiter': self.delimiter}

        try:
            self.verb and print("Loading", path.basename(filepath), end=' ')
            data = np.loadtxt(filepath, **kw)
            self.verb and print("... done.")
        except Exception as e:
            self.verb and print()
            raise e
        # TODO: maybe chk 4 mas str
        return data

    def _getData(self):
        for filepath in self.get_filepaths():
            # filename = filepath.lstrip(self.fpath)
            filename = path.basename(filepath)
            try:
                # mark data?
                self.files[filename]['data'] = self._readFile(filepath)
            except Exception as err:
                self.verb and print(f"{err}\n.. {filename} not read.")
                del self.files[filename]

    def _getCycles(self):
        self.verb and print("file   cycles")
        for filename in self.files:
            data = self.files[filename]["data"]
            # TODO: mejorar
            cycles = {}
            if self.autolab:
                # TODO: get headers y unpack appropriately
                try:
                    # TODO: unfold con numpy, cut data & apply ranges 4 scans
                    for applied_potential, time, current, scan, index, wepotential, *other in data:
                        cycles.update({int(scan): cycles.get(int(scan), []) + [(wepotential, current)]})

                except ValueError:
                    pass
            else:
                scan = 1
                # TODO: chk fwd
                # TODO: mejorar, xtra cycle
                fwd = True  # needed?
                init = data[0][0]  # first potential
                last = init
                ####
                for potential, current, time in data:
                    # toggle fwd flag
                    if not fwd:
                        if (potential - last) > 0:
                            fwd = True
                        # if bkwrd y just past init, scan++
                        elif potential <= init < last:
                            scan += 1
                    elif (potential - last) < 0:
                        fwd = False
                    # TODO: better way?
                    # cycles.update({int(scan): cycles.get(int(scan), []) + [(potential, current)]})
                    # append potencial, corriente
                    try:
                        cycles[scan].append((potential, current))
                    # if no key, crear
                    except KeyError:
                        cycles[scan] = [(potential, current)]
                    last = potential

            for k in cycles:
                cycles[k] = np.array(cycles[k])

            self.files[filename]["cycles"] = cycles
            # fix vvv
            scan = max(cycles.keys())
            self.verb and print(filename[-17:-10], scan if self.autolab else scan - 1)

    def getCycle(self, filename, index=-1):
        if index == -1:
            index = len(self.files[filename]["cycles"])
        return self.files[filename]["cycles"][index]

    def getCycles(self, filename, last=False):
        if last:
            cycle = len(list(self.files[filename]["cycles"].keys())) - 1
            return self.files[filename]["cycles"][cycle]
        else:
            return self.files[filename]["cycles"]


#        try:
#            #TODO: mejorar
#            if last:
#                cycle = len(self.files[filename]["cycles"].keys())-1
#                return self.files[filename]["cycles"][cycle]
#            else:
#                return self.files[filename]["cycles"]
#        except Exception, e:
#            print e
#            print filename
#            print self.files[filename]
#            print 'error', self.files.keys()
#
#
# ..


# def graph(path):
#    keys, data = readFile(path)
#    plt.figure()
#    plt.plot(*zip(*data))
#    plt.show()


if __name__ == "__main__":
    pass
else:
    pass
