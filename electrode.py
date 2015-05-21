from numpy import pi

class Electrode(object):
    #TODO: able 2 edit y recalc
    def __init__(self, area=None, ink=None, vInk=None, diam=None, MEA=False):
        """
        area: [cm2]
        diam: diametre [cm]
        ink: Ink obj
        vInk: ink volume [uL]
        """
        if MEA:
            self.area = Area(float(area))
            #TODO: side
        else:
            if area:
                self.area = Area(float(area))
                self.diam = (area*4./pi)**0.5
            elif diam:
                self.diam = float(diam)
                self.area = Area((pi*diam**2.)/4.)
            else:
                raise Exception("Missing area data.")
        self.ink = ink
        self.vInk = float(vInk) if vInk else None
        self.catCen = ink.catCen
        self.mCat = vInk * ink.mCat / ink.vSolv #ug
        self.mCatCen = self.mCat * ink.pCatCen / 100. #ug
        self.catLoad = self.mCatCen/self.area.geom #ug/cm2
        #default None
        self.ECSA = None
        self.acts = {key: {mode: {potential: None
                for potential in [0.9,0.85,0.8]}
                for mode in ["area", "mass"]}
                for key in ["low", "high"]}
        self.acts['tafel'] = None
        self.B = None
        #TODO: calc o ask dens
        self.dens = 21.45 if self.catCen=="Pt" else None #Pt [g/cm3]
        
    def _calcParticleSize(self):
        self.partSize = 6*self.mCatCen/(self.dens*self.area.big()) if self.dens else None
    
    def setKL(self, B):
        self.B = B
    
    def setECSA(self):
        #chkUnits
        self.ECSA = 100.*self.area.big()/self.catLoad/self.area.geom
        
    def setActs(self, acts):
        self.acts = acts
    
    def getRug(self, key=None):
        if key:
            return self.area[key]/self.area.geom
        for key in self.area:
            print key,"/ geom =", self.area[key]/self.area.geom
            
    #def setRug(self):
    #    try: self.rug = self.ECSA.CO/self.area
    #    except: print "ECSA.CO:", self.ECAA, "    area:", self.area
    #    try: self.rug = self.ECSA.H/self.area
    #    except: print "ECSA.H:", self.ECAA, "    area:", self.area
    
    def __str__(self):
        blah = (
"""
Area:
    geom: {0} cm^2
    CO:   {1} cm^2
    CO-H: {2} cm^2
    CV-H: {3} cm^2    
Deposited ink:
    Volume:        {4} uL
    Catalyst mass: {5} ug
    {6} mass:        {7} ug
    {6} loading: {8} ug/cm^2
acts@0.9V:
    {9} A/mgPt
    {10} A/cm^2
    {11} V/dec[i]
KL: B = {12}
Electrochemical Active Area: {13} cm^2/ug{6}
""")
#"""
#Area:
#    geom: {0:.3f} cm^2
#    CO:   {1:.3f} cm^2
#    CO-H: {2:.3f} cm^2
#    CV-H: {3:.3f} cm^2    
#Deposited ink:
#    Volume:        {4:.2f} uL
#    Catalyst mass: {5} ug
#    {6} mass:        {7} ug
#    {6} loading: {8:.2f} ug/cm^2
#acts@0.9V:
#    {9:.3e} A/mgPt
#    {10:.3e} A/cm^2
#    {11} V/dec[i]
#KL: B = {12}
#Electrochemical Active Area: {13} cm^2
#""")
        try:
            return blah.format(self.area.geom, self.area.CO, self.area.H, self.area.CV,
                self.vInk, self.mCat, self.catCen, self.mCatCen, self.catLoad,
                self.acts['low']['mass'][0.9], self.acts['low']['area'][0.9],
                self.acts['tafel'], self.B, self.ECSA)
        #except TypeError, e:
        #    return str(e)
        except ValueError, e:
            print [self.area.geom, self.area.CO, self.area.CV, self.area.H,
                self.vInk, self.mCat, self.catCen, self.mCatCen, self.catLoad,
                self.acts['low']['mass'][0.9], self.acts['low']['area'][0.9],
                self.acts['tafel'], self.B, self.ECSA]
            return str(e)

#..

class Ink(object):
    def __init__(self, solv=None, vSolv=None, cat=None, mCat=None, pCatCen=None,
                nafion=None, supp=None, mSupp=None, catCen="Pt", mCatCen=None):
        """
        solv: solvent
        vSolv: solvent volume [mL]
        cat: catalyst
        mCat: catalyst mass [mg]
        catCen: catalyst center
        mCatCen: catalyst center mass [mg]
        pCatCen: catalyst center percentage [%]
        supp: support
        mSupp: support mass [mg]
        nafion: nafion quantity
        """
        self.solv = solv
        self.vSolv = float(vSolv) if vSolv else None
        self.cat = cat
        self.mCat = float(mCat) if mCat else None
        self.catCen = catCen
        self.mCatCen = float(mCatCen) if mCatCen else None
        self.pCatCen = float(pCatCen) if pCatCen else None
        self.nafion = nafion
        self.supp = supp
        self.mSupp = float(mSupp) if mSupp else None
 
#..
  
class Area(object):
    #TODO: maybe inherit d dict
    def __init__(self, geom=None, CO=None, H=None, CV=None):
        self.geom = geom
        self.CO = CO
        self.H = H
        self.CV = CV
    
    def big(self):
        #TODO: mejorar
        stuff = self.vars()
        del stuff['geom']
        maxV = max(stuff.values())
        return maxV if maxV else self.geom
        
    def update(self, **stuff):
        vars(self).update(**stuff)
        
    def get(self, key):
        return vars(self).get(key)
    
    def values(self):
        for v in vars(self).values(): yield v
        
    def keys(self):
        for k in vars(self).values(): yield k
    
    def __iter__(self):
        for k in vars(self).keys(): yield k
    
    def __getitem__(self, key):
        return vars(self)[key]
    
    def vars(self):
        return dict(vars(self))
    #TODO: call

#..