#! /usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math
from array import array
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TGraph, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText, TColor, TH1D

# Import PDF library and PDF diagonalizer
gSystem.Load("PDFs/HWWLVJRooPdfs_cxx.so")
gSystem.Load("PDFs/PdfDiagonalizer_cc.so")

from ROOT import RooFit, RooRealVar, RooDataHist, RooDataSet, RooAbsData, RooAbsReal, RooAbsPdf, RooPlot, RooBinning, RooCategory, RooSimultaneous, RooArgList, RooArgSet, RooWorkspace, RooMsgService
from ROOT import RooFormulaVar, RooGenericPdf, RooGaussian, RooExponential, RooPolynomial, RooChebychev, RooBreitWigner, RooCBShape, RooExtendPdf, RooAddPdf, RooProdPdf, RooNumConvPdf, RooFFTConvPdf
from ROOT import PdfDiagonalizer, RooAlphaExp, RooErfExpPdf, Roo2ExpPdf, RooAlpha42ExpPdf, RooExpNPdf, RooAlpha4ExpNPdf, RooExpTailPdf, RooAlpha4ExpTailPdf, RooAlpha

from tools.utils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-c", "--channel", action="store", type="string", dest="channel", default="")
parser.add_option("-d", "--different", action="store_true", default=False, dest="different")
parser.add_option("-e", "--extrapolate", action="store_true", default=False, dest="extrapolate")
parser.add_option("-s", "--scan", action="store_true", default=False, dest="scan")
parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

#gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.05)

ALTERNATIVE = options.different
EXTRAPOLATE = options.extrapolate
SCAN        = options.scan
NTUPLEDIR   = "../jacopo_codes/ntuples/"
PLOTDIR     = "plotsAlpha/"
RATIO       = 4
SHOWERR     = True
BLIND       = False#True if not EXTRAPOLATE else False
LUMISILVER  = 2460.
LUMIGOLDEN  = 2110.
VERBOSE     = options.verbose

channelList = ['XZhnnb', 'XZhnnbb', 'XWhenb', 'XWhenbb', 'XWhmnb', 'XWhmnbb', 'XZheeb', 'XZhmmb', 'XZheebb', 'XZhmmbb']
massPoints = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500]

LOWMIN = 30.
LOWMAX = 65.

SIGMIN = 105. if not EXTRAPOLATE else 135.
SIGMAX = 135. if not EXTRAPOLATE else 300.

HIGMIN = 135. if not EXTRAPOLATE else 300.
HIGMAX = 300.

HBINMIN= 30.
HBINMAX= 300.
HBINS  = 54

XBINMIN= 750.
XBINMAX= 4250.
XBINS  = 35

# topSF[nLept][nBtag]
topSF = [[1, 0.852, 0.541], [1, 0.818, 0.826], [1, 1, 1]]
topSFErr = [[1, 0.062, 0.126], [1, 0.032, 0.073], [1, 1, 1]]

########## ######## ##########


def alpha(channel):

    nElec = channel.count('e')
    nMuon = channel.count('m')
    nLept = nElec + nMuon
    nBtag = channel.count('b')
    
    # Channel-dependent settings
    # Background function. Semi-working options are: EXP, EXP2, EXPN, EXPTAIL
    if nLept == 0:
        treeName = 'SR'
        signName = 'XZh'
        colorVjet = sample['DYJetsToNuNu']['linecolor']
        triName = "HLT_PFMET"
        leptCut = "0==0"
        topVeto = selection["TopVetocut"]
        massVar = "X_cmass"
        binFact = 1
        fitFunc = "EXPN" if nBtag < 2 else "EXPN"
        fitAltFunc = "EXPTAIL" if nBtag < 2 else "EXPTAIL"
        fitFuncVjet = "ERFEXP" if nBtag < 2 else "EXP"
        fitAltFuncVjet = "POL" if nBtag < 2 else "POL"
        fitFuncVV   = "EXPGAUS" if nBtag < 2 else "EXPGAUS"
        fitFuncTop  = "GAUS2"
    elif nLept == 1:
        treeName = 'WCR'
        signName = 'XWh'
        colorVjet = sample['WJetsToLNu']['linecolor']
        triName = "HLT_Ele" if nElec > 0 else "HLT_Mu"
        leptCut = "isWtoEN" if nElec > 0 else "isWtoMN"
        topVeto = selection["TopVetocut"]
        massVar = "X_mass"
        binFact = 2
        if nElec > 0:
            fitFunc = "EXPTAIL" if nBtag < 2 else "EXPN"
            fitAltFunc  = "EXPN" if nBtag < 2 else "POW"
        else:
            fitFunc = "EXPN" if nBtag < 2 else "EXPN"
            fitAltFunc  = "EXPTAIL" if nBtag < 2 else "POW"
        fitFuncVjet = "ERFEXP" if nBtag < 2 else "EXP"
        fitAltFuncVjet = "POL" if nBtag < 2 else "POL"
        fitFuncVV   = "EXPGAUS" if nBtag < 2 else "EXPGAUS"
        fitFuncTop  = "GAUS3" if nBtag < 2 else "GAUS2"
    else:
        treeName = 'XZh'
        signName = 'XZh'
        colorVjet = sample['DYJetsToLL']['linecolor']
        triName = "HLT_Ele" if nElec > 0 else "HLT_Mu"
        leptCut = "isZtoEE" if nElec > 0 else "isZtoMM"
        topVeto = "X_dPhi>2.5"
        massVar = "X_mass"
        binFact = 2
        if nElec > 0:
            fitFunc = "EXPTAIL" if nBtag < 2 else "EXPTAIL"
            fitAltFunc = "POW" if nBtag < 2 else "POW"
        else:
            fitFunc = "EXPTAIL" if nBtag < 2 else "EXPTAIL"
            fitAltFunc = "POW" if nBtag < 2 else "POW"
        fitFuncVjet = "ERFEXP" if nBtag < 2 and nElec < 1 else "EXP"
        fitAltFuncVjet = "POL" if nBtag < 2 else "POL"
        fitFuncVV   = "EXPGAUS2" if nBtag < 2 else "EXPGAUS2"
        fitFuncTop  = "GAUS"
    
    # -----------------------------------------
    # collect the function name

    list_function_name = [["fitFuncVjet",fitFuncVjet],["fitFuncVV",fitFuncVV],["fitFuncTop",fitFuncTop]]

    # -----------------------------------------

    btagCut = selection["2Btag"] if nBtag == 2 else selection["1Btag"]
    
    print "--- Channel", channel, "---"
    print "  number of electrons:", nElec, " muons:", nMuon, " b-tags:", nBtag
    print "  read tree:", treeName, "and trigger:", triName
    if ALTERNATIVE: print "  using ALTERNATIVE fit functions"
    print "-"*11*2
    
    # Silent RooFit
    RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)
    
    #*******************************************************#
    #                                                       #
    #              Variables and selections                 #
    #                                                       #
    #*******************************************************#
    
    # Define all the variables from the trees that will be used in the cuts and fits
    # this steps actually perform a "projection" of the entire tree on the variables in thei ranges, so be careful once setting the limits
    X_mass = RooRealVar(  massVar, "m_{X}" if nLept > 0 else "m_{T}^{X}", XBINMIN, XBINMAX, "GeV")
    J_mass = RooRealVar( "fatjet1_prunedMassCorr", "jet corrected pruned mass", HBINMIN, HBINMAX, "GeV")
    CSV1 = RooRealVar(   "fatjet1_CSVR1",                           "",        -1.e99,   1.e4     )
    CSV2 = RooRealVar(   "fatjet1_CSVR2",                           "",        -1.e99,   1.e4     )
    nB   = RooRealVar(   "fatjet1_nBtag",                           "",            0.,   4        )
    CSVTop = RooRealVar( "bjet1_CSVR",                              "",        -1.e99,   1.e4     )
    X_dPhi = RooRealVar( "X_dPhi",                                  "",            0.,   3.15     )
    isZtoEE = RooRealVar("isZtoEE",                                 "",            0.,   2        )
    isZtoMM = RooRealVar("isZtoMM",                                 "",            0.,   2        )
    isWtoEN = RooRealVar("isWtoEN",                                 "",            0.,   2        )
    isWtoMN = RooRealVar("isWtoMN",                                 "",            0.,   2        )
    weight = RooRealVar( "eventWeightLumi",                         "",         -1.e9,   1.       )
    
    # Define the RooArgSet which will include all the variables defined before
    # there is a maximum of 9 variables in the declaration, so the others need to be added with 'add'
    variables = RooArgSet(X_mass, J_mass, CSV1, CSV2, nB, CSVTop, X_dPhi)
    variables.add(RooArgSet(isZtoEE, isZtoMM, isWtoEN, isWtoMN, weight))
    
    # set reasonable ranges for J_mass and X_mass
    # these are used in the fit in order to avoid ROOFIT to look in regions very far away from where we are fitting 
    # (honestly, it is not clear to me why it is necessary, but without them the fit often explodes)
    J_mass.setRange("h_reasonable_range", LOWMIN, HIGMAX)
    X_mass.setRange("X_reasonable_range", XBINMIN, XBINMAX)
    
    # Set RooArgSets once for all, see https://root.cern.ch/phpBB3/viewtopic.php?t=11758
    jetMassArg = RooArgSet(J_mass)
    # Define the ranges in fatJetMass - these will be used to define SB and SR
    J_mass.setRange("LSBrange", LOWMIN, LOWMAX)
    J_mass.setRange("HSBrange", HIGMIN, HIGMAX)
    J_mass.setRange("VRrange",  LOWMAX, SIGMIN)
    J_mass.setRange("SRrange",  SIGMIN, SIGMAX)
    
    # Set binning for plots
    J_mass.setBins(HBINS)
    X_mass.setBins(binFact*XBINS)
    
    # Define the selection for the various categories (base + SR / LSBcut / HSBcut )
    baseCut = leptCut + " && " + btagCut + "&&" + topVeto
    massCut = massVar + ">%d" % XBINMIN
    baseCut += " && " + massCut
    
    # Cuts
    SRcut  = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), SIGMIN, J_mass.GetName(), SIGMAX)
    LSBcut = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), LOWMIN, J_mass.GetName(), LOWMAX)
    HSBcut = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), HIGMIN, J_mass.GetName(), HIGMAX)
    SBcut  = baseCut + " && ((%s>%d && %s<%d) || (%s>%d && %s<%d))" % (J_mass.GetName(), LOWMIN, J_mass.GetName(), LOWMAX, J_mass.GetName(), HIGMIN, J_mass.GetName(), HIGMAX)
    VRcut  = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), LOWMAX, J_mass.GetName(), SIGMIN)
    
    # Binning
    binsJmass = RooBinning(HBINS, HBINMIN, HBINMAX)
    #binsJmass.addUniform(HBINS, HBINMIN, HBINMAX)
    binsXmass = RooBinning(binFact*XBINS, XBINMIN, XBINMAX)
    #binsXmass.addUniform(binFact*XBINS, XBINMIN, XBINMAX)
    
    #*******************************************************#
    #                                                       #
    #                      Input files                      #
    #                                                       #
    #*******************************************************#
    
    # Import the files using TChains (separately for the bkg "classes" that we want to describe: here DY and VV+ST+TT)
    treeData = TChain(treeName)
    treeMC   = TChain(treeName)
    treeVjet = TChain(treeName)
    treeVV   = TChain(treeName)
    treeTop  = TChain(treeName)
    treeSign = {}
    nevtSign = {}
    for i, m in enumerate(massPoints): treeSign[m] = TChain(treeName)
    
    # Read data
    pd = getPrimaryDataset(triName)
    if len(pd)==0: raw_input("Warning: Primary Dataset not recognized, continue?")
    for i, s in enumerate(pd): treeData.Add(NTUPLEDIR + s + ".root")
    
    # Read V+jets backgrounds
    for i, s in enumerate(["WJetsToLNu_HT", "DYJetsToNuNu_HT", "DYJetsToLL_HT"]):
        for j, ss in enumerate(sample[s]['files']): treeVjet.Add(NTUPLEDIR + ss + ".root")
    
    # Read VV backgrounds
    for i, s in enumerate(["VV"]):
        for j, ss in enumerate(sample[s]['files']): treeVV.Add(NTUPLEDIR + ss + ".root")
    
    # Read Top backgrounds
    for i, s in enumerate(["ST", "TTbar"]):
        for j, ss in enumerate(sample[s]['files']): treeTop.Add(NTUPLEDIR + ss + ".root")
    
    # Read signals
    for i, m in enumerate(massPoints):
        for j, ss in enumerate(sample["%s_M%d" % (signName, m)]['files']):
            treeSign[m].Add(NTUPLEDIR + ss + ".root")
            sfile = TFile(NTUPLEDIR + ss + ".root", "READ")
            shist = sfile.Get("Counters/Counter")
            nevtSign[m] = shist.GetBinContent(1)
            sfile.Close()
    
    # Sum all background MC
    treeMC.Add(treeVjet)
    treeMC.Add(treeVV)
    treeMC.Add(treeTop)
    
    # create a dataset to host data in sideband (using this dataset we are automatically blind in the SR!)
    setDataSB = RooDataSet("setDataSB", "setDataSB", variables, RooFit.Cut(SBcut), RooFit.WeightVar(weight), RooFit.Import(treeData))
    setDataLSB = RooDataSet("setDataLSB", "setDataLSB", variables, RooFit.Import(setDataSB), RooFit.Cut(LSBcut), RooFit.WeightVar(weight))
    setDataHSB = RooDataSet("setDataHSB", "setDataHSB", variables, RooFit.Import(setDataSB), RooFit.Cut(HSBcut), RooFit.WeightVar(weight))
    
    # Observed data (WARNING, BLIND!)
    setDataSR = RooDataSet("setDataSR", "setDataSR", variables, RooFit.Cut(SRcut), RooFit.WeightVar(weight), RooFit.Import(treeData))
    setDataVR = RooDataSet("setDataVR", "setDataVR", variables, RooFit.Cut(VRcut), RooFit.WeightVar(weight), RooFit.Import(treeData)) # Observed in the VV mass, just for plotting purposes
    
    setDataSRSB = RooDataSet("setDataSRSB", "setDataSRSB", variables, RooFit.Cut("("+SRcut+") || ("+SBcut+")"), RooFit.WeightVar(weight), RooFit.Import(treeData))
    
    # same for the bkg datasets from MC, where we just apply the base selections (not blind)
    setVjet = RooDataSet("setVjet", "setVjet", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeVjet))
    setVjetSB = RooDataSet("setVjetSB", "setVjetSB", variables, RooFit.Import(setVjet), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
    setVjetSR = RooDataSet("setVjetSR", "setVjetSR", variables, RooFit.Import(setVjet), RooFit.Cut(SRcut), RooFit.WeightVar(weight))
    setVV = RooDataSet("setVV", "setVV", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeVV))
    setVVSB = RooDataSet("setVVSB", "setVVSB", variables, RooFit.Import(setVV), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
    setVVSR = RooDataSet("setVVSR", "setVVSR", variables, RooFit.Import(setVV), RooFit.Cut(SRcut), RooFit.WeightVar(weight))
    setTop = RooDataSet("setTop", "setTop", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeTop))
    setTopSB = RooDataSet("setTopSB", "setTopSB", variables, RooFit.Import(setTop), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
    setTopSR = RooDataSet("setTopSR", "setTopSR", variables, RooFit.Import(setTop), RooFit.Cut(SRcut), RooFit.WeightVar(weight))

    list_of_set = []
    list_of_set.append( [ ["setDataSB" ,setDataSB ],["setDataLSB" ,setDataLSB ],["setDataHSB" ,setDataHSB ] ]  )    
    list_of_set.append( [ ["setVjet" ,setVjet ]  , ["setVjetSB" ,setVjetSB ] , ["setVjetSR" ,setVjetSR ]  ]          )
    list_of_set.append( [ ["setVV" ,setVV ]  , ["setVVSB" ,setVVSB ] , ["setVVSR" ,setVVSR ]  ]          )
    list_of_set.append( [ ["setTop" ,setTop ]  , ["setTopSB" ,setTopSB ] , ["setTopSR" ,setTopSR ]  ]          )

#    list_set = [["fitFuncVjet",fitFuncVjet],["fitFuncVV",fitFuncVV],["fitFuncTop",fitFuncTop]]
    
    print "  Data events SB: %.2f" % setDataSB.sumEntries()
    print "  V+jets entries: %.2f" % setVjet.sumEntries()
    print "  VV, VH entries: %.2f" % setVV.sumEntries()
    print "  Top,ST entries: %.2f" % setTop.sumEntries()
    
    nVV   = RooRealVar("nVV",  "VV normalization",   setVV.sumEntries(SBcut),   0., 2*setVV.sumEntries(SBcut))
    nTop  = RooRealVar("nTop", "Top normalization",  setTop.sumEntries(SBcut),  0., 2*setTop.sumEntries(SBcut))
    nVjet = RooRealVar("nVjet","Vjet normalization", setDataSB.sumEntries(), 0., 2*setDataSB.sumEntries(SBcut))
    nVjet2 = RooRealVar("nVjet2","Vjet2 normalization", setDataSB.sumEntries(), 0., 2*setDataSB.sumEntries(SBcut))
    
    # Apply Top SF
    nTop.setVal(nTop.getVal()*topSF[nLept][nBtag])
    nTop.setError(nTop.getVal()*topSFErr[nLept][nBtag])
    
    # Define entries
    entryVjet = RooRealVar("entryVjets",  "V+jets normalization", setVjet.sumEntries(), 0., 1.e6)
    entryVV = RooRealVar("entryVV",  "VV normalization", setVV.sumEntries(), 0., 1.e6)
    entryTop = RooRealVar("entryTop",  "Top normalization", setTop.sumEntries(), 0., 1.e6)
    
    entrySB = RooRealVar("entrySB",  "Data SB normalization", setDataSB.sumEntries(SBcut), 0., 1.e6)
    entrySB.setError(math.sqrt(entrySB.getVal()))
    
    entryLSB = RooRealVar("entryLSB",  "Data LSB normalization", setDataSB.sumEntries(LSBcut), 0., 1.e6)
    entryLSB.setError(math.sqrt(entryLSB.getVal()))

    entryHSB = RooRealVar("entryHSB",  "Data HSB normalization", setDataSB.sumEntries(HSBcut), 0., 1.e6)
    entryHSB.setError(math.sqrt(entryHSB.getVal()))

    ###################################################################################
    #        _   _                                                                    #
    #       | \ | |                          | (_)         | | (_)                    #
    #       |  \| | ___  _ __ _ __ ___   __ _| |_ ___  __ _| |_ _  ___  _ __          #
    #       | . ` |/ _ \| '__| '_ ` _ \ / _` | | / __|/ _` | __| |/ _ \| '_ \         #
    #       | |\  | (_) | |  | | | | | | (_| | | \__ \ (_| | |_| | (_) | | | |        #
    #       |_| \_|\___/|_|  |_| |_| |_|\__,_|_|_|___/\__,_|\__|_|\___/|_| |_|        #
    #                                                                                 #
    ###################################################################################
    # fancy ASCII art thanks to, I guess, Jose
    
    # start by creating the fit models to get the normalization: 
    # * MAIN and SECONDARY bkg are taken from MC by fitting the whole J_mass range
    # * The two PDFs are added together using the relative normalizations of the two bkg from MC
    # * DATA is then fit in the sidebands only using the combined bkg PDF
    # * The results of the fit are then estrapolated in the SR and the integral is evaluated.
    # * This defines the bkg normalization in the SR
    
    #*******************************************************#
    #                                                       #
    #                 V+jets normalization                  #
    #                                                       #
    #*******************************************************#
    
    # Variables for V+jets
    constVjet   = RooRealVar("constVjet",   "slope of the exp",      -0.020, -1.,   0.)
    offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     30.,   -50., 400.)
    widthVjet   = RooRealVar("widthVjet",   "width of the erf",     100.,     1., 200.) #0, 400
    a0Vjet = RooRealVar("a0Vjet", "width of the erf", -0.1, -5, 0)
    a1Vjet = RooRealVar("a1Vjet", "width of the erf", 0.6,  0, 5)
    a2Vjet = RooRealVar("a2Vjet", "width of the erf", -0.1, -1, 1)
    
    if channel=="XZhnnb":
        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     500.,   200., 1000.)
    if channel=="XZhnnbb":
        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     350.,   200., 500.)
#    if channel == "XWhenb" or channel == "XZheeb":
#        offsetVjet.setVal(120.)
#        offsetVjet.setConstant(True)
    if channel == "XWhenb":
        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",    120.,  80., 155.)
    if channel == "XWhenbb" or channel == "XZhmmb":
        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     67.,   50., 100.)
    if channel == "XWhmnb":
        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",    30.,   -50., 600.)
    if channel == "XZheeb":
        offsetVjet.setMin(-400)
        offsetVjet.setVal(0.)
        offsetVjet.setMax(1000)
        widthVjet.setVal(1.)
    
    # Define V+jets model
    if fitFuncVjet == "ERFEXP": VjetMass = RooErfExpPdf("VjetMass", fitFuncVjet, J_mass, constVjet, offsetVjet, widthVjet)
    elif fitFuncVjet == "EXP": VjetMass = RooExponential("VjetMass", fitFuncVjet, J_mass, constVjet)
    elif fitFuncVjet == "GAUS": VjetMass = RooGaussian("VjetMass", fitFuncVjet, J_mass, offsetVjet, widthVjet)
    elif fitFuncVjet == "POL": VjetMass = RooChebychev("VjetMass", fitFuncVjet, J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet))
    elif fitFuncVjet == "POW": VjetMass = RooGenericPdf("VjetMass", fitFuncVjet, "@0^@1", RooArgList(J_mass, a0Vjet))
    else:
        print "  ERROR! Pdf", fitFuncVjet, "is not implemented for Vjets"
        exit()
    
    if fitAltFuncVjet == "POL": VjetMass2 = RooChebychev("VjetMass2", "polynomial for V+jets mass", J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet))
    else:
        print "  ERROR! Pdf", fitAltFuncVjet, "is not implemented for Vjets"
        exit()
   
 
    # fit to main bkg in MC (whole range)
    frVjet = VjetMass.fitTo(setVjet, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))
    frVjet2 = VjetMass2.fitTo(setVjet, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))
    
    if VERBOSE: print "********** Fit result [JET MASS Vjets] *"+"*"*40, "\n", frVjet.Print(), "\n", "*"*80
    
    #likelihoodScan(VjetMass, setVjet, [constVjet, offsetVjet, widthVjet])


    list_Vjet_pars = []
    list_Vjet_pars.append( ["constVjet" ,constVjet.getVal()  ] )
    list_Vjet_pars.append( ["offsetVjet",offsetVjet.getVal() ] )
    list_Vjet_pars.append( ["widthVjet" ,widthVjet.getVal()  ] )
    list_Vjet_pars.append( ["a0Vjet"    ,a0Vjet.getVal()     ] )
    list_Vjet_pars.append( ["a1Vjet"    ,a1Vjet.getVal()     ] )
    list_Vjet_pars.append( ["a2Vjet"    ,a2Vjet.getVal()     ] )
    
    #*******************************************************#
    #                                                       #
    #                 VV, VH normalization                  #
    #                                                       #
    #*******************************************************#
    
    # Variables for VV
    # Error function and exponential to model the bulk
    constVV  = RooRealVar("constVV",  "slope of the exp",  -0.030, -0.1,   0.)
    offsetVV = RooRealVar("offsetVV", "offset of the erf", 90.,     1., 300.)
    widthVV  = RooRealVar("widthVV",  "width of the erf",  50.,     1., 100.)
    erfrVV   = RooErfExpPdf("baseVV", "error function for VV jet mass", J_mass, constVV, offsetVV, widthVV)
    expoVV   = RooExponential("baseVV", "error function for VV jet mass", J_mass, constVV)
    # gaussian for the V mass peak
    meanVV   = RooRealVar("meanVV",   "mean of the gaussian",           90.,    60., 100.)
    sigmaVV  = RooRealVar("sigmaVV",  "sigma of the gaussian",          10.,     6.,  30.)
    fracVV   = RooRealVar("fracVV",   "fraction of gaussian wrt erfexp", 3.2e-1, 0.,   1.)
    gausVV   = RooGaussian("gausVV",  "gaus for VV jet mass", J_mass, meanVV, sigmaVV)
    # gaussian for the H mass peak
    meanVH   = RooRealVar("meanVH",   "mean of the gaussian",           125.,   100., 150.)
    sigmaVH  = RooRealVar("sigmaVH",  "sigma of the gaussian",           10.,     5.,  50.)
    fracVH   = RooRealVar("fracVH",   "fraction of gaussian wrt erfexp",  1.5e-2, 0.,   1.)
    gausVH   = RooGaussian("gausVH",  "gaus for VH jet mass", J_mass, meanVH, sigmaVH)
    
    # Define VV model
    if fitFuncVV == "ERFEXPGAUS": VVMass  = RooAddPdf("VVMass",   fitFuncVV, RooArgList(gausVV, erfrVV), RooArgList(fracVV))
    elif fitFuncVV == "ERFEXPGAUS2": VVMass  = RooAddPdf("VVMass",   fitFuncVV, RooArgList(gausVH, gausVV, erfrVV), RooArgList(fracVH, fracVV))
    elif fitFuncVV == "EXPGAUS": VVMass  = RooAddPdf("VVMass",   fitFuncVV, RooArgList(gausVV, expoVV), RooArgList(fracVV))
    elif fitFuncVV == "EXPGAUS2": VVMass  = RooAddPdf("VVMass",   fitFuncVV, RooArgList(gausVH, gausVV, expoVV), RooArgList(fracVH, fracVV))
    else:
        print "  ERROR! Pdf", fitFuncVV, "is not implemented for VV"
        exit()
    
    # fit to secondary bkg in MC (whole range)
    frVV = VVMass.fitTo(setVV, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))
    
    if VERBOSE: print "********** Fit result [JET MASS VV] ****"+"*"*40, "\n", frVV.Print(), "\n", "*"*80

    list_VV_pars = []
    list_VV_pars.append( ["constVV" ,constVV.getVal()  ] )
    list_VV_pars.append( ["offsetVV",offsetVV.getVal() ] )
    list_VV_pars.append( ["widthVV" ,widthVV.getVal()  ] )
    list_VV_pars.append( ["meanVV"  ,meanVV.getVal()   ] )
    list_VV_pars.append( ["sigmaVV" ,sigmaVV.getVal()  ] )
    list_VV_pars.append( ["fracVV"  ,fracVV.getVal()   ] )
    list_VV_pars.append( ["meanVH"  ,meanVH.getVal()   ] )
    list_VV_pars.append( ["sigmaVH" ,sigmaVH.getVal()  ] )
    list_VV_pars.append( ["fracVH"  ,fracVH.getVal()   ] )
    
    #*******************************************************#
    #                                                       #
    #                 Top, ST normalization                 #
    #                                                       #
    #*******************************************************#
    
    # Variables for Top
    # Error Function * Exponential to model the bulk
    constTop  = RooRealVar("constTop",  "slope of the exp", -0.030,   -1.,   0.)
    offsetTop = RooRealVar("offsetTop", "offset of the erf", 175.0,   50., 250.)
    widthTop  = RooRealVar("widthTop",  "width of the erf",  100.0,    1., 300.)
    gausTop   = RooGaussian("baseTop",  "gaus for Top jet mass", J_mass, offsetTop, widthTop)
    erfrTop   = RooErfExpPdf("baseTop", "error function for Top jet mass", J_mass, constTop, offsetTop, widthTop)
    # gaussian for the W mass peak
    meanW     = RooRealVar("meanW",     "mean of the gaussian",           80., 70., 90.)
    sigmaW    = RooRealVar("sigmaW",    "sigma of the gaussian",          10.,  2., 20.)
    fracW     = RooRealVar("fracW",     "fraction of gaussian wrt erfexp", 0.1, 0.,  1.)
    gausW     = RooGaussian("gausW",    "gaus for W jet mass", J_mass, meanW, sigmaW)
    # gaussian for the Top mass peak
    meanT     = RooRealVar("meanT",     "mean of the gaussian",           175., 150., 200.)
    sigmaT    = RooRealVar("sigmaT",    "sigma of the gaussian",           12.,   5.,  30.)
    fracT     = RooRealVar("fracT",     "fraction of gaussian wrt erfexp",  0.1,  0.,   1.)
    gausT     = RooGaussian("gausT",    "gaus for T jet mass", J_mass, meanT, sigmaT)
    
    if channel=="XZheeb" or channel=="XZheebb" or channel=="XZhmmb" or channel=="XZhmmbb":
        offsetTop = RooRealVar("offsetTop", "offset of the erf", 200.0,   -50., 450.)
        widthTop  = RooRealVar("widthTop",  "width of the erf",  100.0,    1., 1000.)
    
    # Define Top model
    if fitFuncTop == "ERFEXPGAUS2": TopMass = RooAddPdf("TopMass",   fitFuncTop, RooArgList(gausW, gausT, erfrTop), RooArgList(fracW, fracT))
    elif fitFuncTop == "ERFEXPGAUS": TopMass = RooAddPdf("TopMass",   fitFuncTop, RooArgList(gausT, erfrTop), RooArgList(fracT))
    elif fitFuncTop == "GAUS3": TopMass  = RooAddPdf("TopMass",   fitFuncTop, RooArgList(gausW, gausT, gausTop), RooArgList(fracW, fracT))
    elif fitFuncTop == "GAUS2": TopMass  = RooAddPdf("TopMass",   fitFuncTop, RooArgList(gausT, gausTop), RooArgList(fracT))
    elif fitFuncTop == "GAUS": TopMass  = RooGaussian("TopMass", fitFuncTop, J_mass, offsetTop, widthTop)
    else:
        print "  ERROR! Pdf", fitFuncTop, "is not implemented for Top"
        exit()
    
    # fit to secondary bkg in MC (whole range)
    frTop = TopMass.fitTo(setTop, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))
    
    if VERBOSE: print "********** Fit result [JET MASS TOP] ***"+"*"*40, "\n", frTop.Print(), "\n", "*"*80
    
    #likelihoodScan(TopMass, setTop, [offsetTop, widthTop])

    list_Top_pars = []
    list_Top_pars.append( ["constTop" ,  constTop.getVal() ] )
    list_Top_pars.append( ["offsetTop",  offsetTop.getVal()] )
    list_Top_pars.append( ["widthTop" ,  widthTop.getVal() ] )
    list_Top_pars.append( ["meanW"    ,  meanW.getVal()    ] )
    list_Top_pars.append( ["sigmaW" ,  sigmaW.getVal()  ] )
    list_Top_pars.append( ["fracW"    ,  fracW.getVal()    ] )
    list_Top_pars.append( ["meanT"    ,  meanT.getVal()    ] )
    list_Top_pars.append( ["sigmaT"   ,  sigmaT.getVal()   ] )
    list_Top_pars.append( ["fracT"    ,  fracT.getVal()    ] )


    #*******************************************************#
    #                                                       #
    #                 All bkg normalization                 #
    #                                                       #
    #*******************************************************#
    
#    nVjet.setConstant(False)
#    nVjet2.setConstant(False)
#    
#    constVjet.setConstant(False)
#    offsetVjet.setConstant(False)
#    widthVjet.setConstant(False)
#    a0Vjet.setConstant(False)
#    a1Vjet.setConstant(False)
#    a2Vjet.setConstant(False)
    
    constVV.setConstant(True)
    offsetVV.setConstant(True)
    widthVV.setConstant(True)
    meanVV.setConstant(True)
    sigmaVV.setConstant(True)
    fracVV.setConstant(True)
    meanVH.setConstant(True)
    sigmaVH.setConstant(True)
    fracVH.setConstant(True)
    
    constTop.setConstant(True)
    offsetTop.setConstant(True)
    widthTop.setConstant(True)
    meanW.setConstant(True)
    sigmaW.setConstant(True)
    fracW.setConstant(True)
    meanT.setConstant(True)
    sigmaT.setConstant(True)
    fracT.setConstant(True)
    
    nVV.setConstant(True)
    nTop.setConstant(True)
    nVjet.setConstant(False)
    nVjet2.setConstant(False)

    # -------------------------------------------
    # bias study

    Save_Dir = "/afs/cern.ch/user/y/yuchang/www/jacopo_plotsAlpha/yu_hsiang_bias_study_new"
    Save_Dir = Save_Dir +"/"+ channel 
    
    Yu_Hsiang_Box(J_mass, channel, list_function_name, list_Vjet_pars, list_VV_pars, list_Top_pars, list_of_set, Save_Dir  )


    # -------------------------------------------
    
    # Final background model by adding the main+secondary pdfs (using 'coef': ratio of the secondary/main, from MC)
    TopMass_ext  = RooExtendPdf("TopMass_ext",  "extended p.d.f", TopMass,  nTop)
    VVMass_ext   = RooExtendPdf("VVMass_ext",   "extended p.d.f", VVMass,   nVV)
    VjetMass_ext = RooExtendPdf("VjetMass_ext", "extended p.d.f", VjetMass, nVjet)
    VjetMass2_ext = RooExtendPdf("VjetMass_ext", "extended p.d.f", VjetMass, nVjet2)
    BkgMass = RooAddPdf("BkgMass", "BkgMass", RooArgList(TopMass_ext, VVMass_ext, VjetMass_ext), RooArgList(nTop, nVV, nVjet))
    BkgMass2 = RooAddPdf("BkgMass2", "BkgMass2", RooArgList(TopMass_ext, VVMass_ext, VjetMass2_ext), RooArgList(nTop, nVV, nVjet2))
    BkgMass.fixAddCoefRange("h_reasonable_range")
    BkgMass2.fixAddCoefRange("h_reasonable_range")
   
    # Extended fit model to data in SB
    frMass = BkgMass.fitTo(setDataSB, RooFit.SumW2Error(True), RooFit.Extended(True), RooFit.Range("LSBrange,HSBrange"), RooFit.Strategy(2), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1)) #, RooFit.NumCPU(10)
    if VERBOSE: print "********** Fit result [JET MASS DATA] **"+"*"*40, "\n", frMass.Print(), "\n", "*"*80
    frMass2 = BkgMass2.fitTo(setDataSB, RooFit.SumW2Error(True), RooFit.Extended(True), RooFit.Range("LSBrange,HSBrange"), RooFit.Strategy(2), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))
    if VERBOSE: print "********** Fit result [JET MASS DATA] **"+"*"*40, "\n", frMass2.Print(), "\n", "*"*80
    
    #if SCAN:
    #    likelihoodScan(VjetMass, setVjet, [constVjet, offsetVjet, widthVjet])
    
    # Fix normalization and parameters of V+jets after the fit to data
    nVjet.setConstant(True)
    nVjet2.setConstant(True)
    
    constVjet.setConstant(True)
    offsetVjet.setConstant(True)
    widthVjet.setConstant(True)
    a0Vjet.setConstant(True)
    a1Vjet.setConstant(True)
    a2Vjet.setConstant(True)

    
    # integrals for global normalization
    # do not integrate the composte model: results have no sense
    
    # integral for normalization in the SB
    iSBVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
    iSBVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
    iSBTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
    
    # integral for normalization in the SR
    iSRVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
    iSRVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
    iSRTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
    
    # integral for normalization in the VR
    iVRVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
    iVRVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
    iVRTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
    
    # formual vars
    SByield = RooFormulaVar("SByield", "extrapolation to SR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSBVjet, nVjet, iSBVV, nVV, iSBTop, nTop))
    VRyield = RooFormulaVar("VRyield", "extrapolation to VR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iVRVjet, nVjet, iVRVV, nVV, iVRTop, nTop))
    SRyield = RooFormulaVar("SRyield", "extrapolation to SR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSRVjet, nVjet, iSRVV, nVV, iSRTop, nTop))
   
    print "SByield: ", SByield.getVal()
 
    # fractions
    fSBVjet = RooRealVar("fVjet", "Fraction of Vjet events in SB", iSBVjet.getVal()*nVjet.getVal()/SByield.getVal(), 0., 1.)
    fSBVV = RooRealVar("fSBVV", "Fraction of VV events in SB", iSBVV.getVal()*nVV.getVal()/SByield.getVal(), 0., 1.)
    fSBTop = RooRealVar("fSBTop", "Fraction of Top events in SB", iSBTop.getVal()*nTop.getVal()/SByield.getVal(), 0., 1.)
    
    fSRVjet = RooRealVar("fSRVjet", "Fraction of Vjet events in SR", iSRVjet.getVal()*nVjet.getVal()/SRyield.getVal(), 0., 1.)
    fSRVV = RooRealVar("fSRVV", "Fraction of VV events in SR", iSRVV.getVal()*nVV.getVal()/SRyield.getVal(), 0., 1.)
    fSRTop = RooRealVar("fSRTop", "Fraction of Top events in SR", iSRTop.getVal()*nTop.getVal()/SRyield.getVal(), 0., 1.)
    
    # final normalization values
    bkgYield            = SRyield.getVal()
    bkgYield2           = (VjetMass2.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))).getVal()*nVjet2.getVal() + iSRVV.getVal()*nVV.getVal() + iSRTop.getVal()*nTop.getVal()
    bkgYield_syst       = math.sqrt(SRyield.getPropagatedError(frVV)**2 + SRyield.getPropagatedError(frTop)**2)
    bkgYield_stat       = math.sqrt(SRyield.getPropagatedError(frMass)**2)
    bkgYield_alte       = abs(bkgYield - bkgYield2) #/bkgYield
    bkgYield_eig_norm   = RooRealVar("predSR_eig_norm", "expected yield in SR", bkgYield, 0., 1.e6)   
    
    print "Events in channel", channel, ": V+jets %.3f (%.1f%%),   VV %.3f (%.1f%%),   Top %.3f (%.1f%%)" % (iSRVjet.getVal()*nVjet.getVal(), fSRVjet.getVal()*100, iSRVV.getVal()*nVV.getVal(), fSRVV.getVal()*100, iSRTop.getVal()*nTop.getVal(), fSRTop.getVal()*100)
    print "Events in channel", channel, ": Integral = $%.3f$ & $\pm %.3f$ & $\pm %.3f$ & $\pm %.3f$, observed = %.0f" % (bkgYield, bkgYield_stat, bkgYield_syst, bkgYield_alte, setDataSR.sumEntries() if not False else -1)


    # -------------------------------------------
    # test to plot the fit

    print "nVjet: ", nVjet.getVal()
    print "nVV: ", nVV.getVal()
    print "nTop: ", nTop.getVal()
    nTotal = nVjet.getVal() + nVV.getVal() + nTop.getVal()
    print "nTotal: ", nTotal

    nData_SB = setDataSB.sumEntries(SBcut)
    print "nData_SB: ", nData_SB

    test_frame = J_mass.frame(RooFit.Title("test frame"))

    # data SB
    setDataSB.plotOn(test_frame)

    # fit MC
    BkgMass.plotOn(test_frame,RooFit.Normalization( SByield.getVal()  , RooAbsReal.NumEvent), RooFit.LineColor(2))
    BkgMass.plotOn(test_frame,RooFit.Normalization( SByield.getVal()  , RooAbsReal.NumEvent), RooFit.LineColor(6),RooFit.Components("TopMass_ext,VVMass_ext"))
    BkgMass.plotOn(test_frame,RooFit.Normalization( SByield.getVal()  , RooAbsReal.NumEvent), RooFit.LineColor(7),RooFit.Components("VVMass_ext"))

    c_test = TCanvas("test","test draw",800,600)
    c_test.cd()
    test_frame.Draw()
    c_test.SaveAs(Save_Dir+"/"+"test_to_plot_dataSB_and_several_background_new.pdf")

    # -------------------------------------------

    
    # ====== CONTROL VALUE ======

    # -------------------------------------------

def Yu_Hsiang_Box(J_mass, channel, list_function_name, list_Vjet_pars, list_VV_pars, list_Top_pars, list_of_set ,Save_Dir  ):

    print ""
    print "start Yu-hsiang Box"
    print ""

    # ------ 0. check ----------
    print "channel: ", channel

    print ""
    print "for list_function_name"
    for i in range(0,len(list_function_name) ):
	print "   ",list_function_name[i][0], ": ", list_function_name[i][1]
    print ""


    # ------ 1. plot fit MC ----------
	
    

    # Vjet -----------
    plot_MC_fit_Vjet_frame = J_mass.frame(RooFit.Title("plot fit Vjet MC"))

    print "the used data set is: ", list_of_set[1][0][0]
    setVjet = list_of_set[1][0][1] 
    setVjet.plotOn(plot_MC_fit_Vjet_frame) 

    constVjet_   = RooRealVar("constVjet_" , "slope of the exp" ,  list_Vjet_pars[0][1],  -1.,   0.)
    offsetVjet_  = RooRealVar("offsetVjet_", "offset of the erf",  list_Vjet_pars[1][1], -50., 400.)
    widthVjet_   = RooRealVar("widthVjet_" , "width of the erf" ,  list_Vjet_pars[2][1],   1., 200.) #0, 400
    a0Vjet_      = RooRealVar("a0Vjet_"    , "width of the erf" ,  list_Vjet_pars[3][1],  -5 ,   0 )
    a1Vjet_      = RooRealVar("a1Vjet_"    , "width of the erf" ,  list_Vjet_pars[4][1],   0 ,   5 )
    a2Vjet_      = RooRealVar("a2Vjet_"    , "width of the erf" ,  list_Vjet_pars[5][1],  -1 ,   1 )

    if channel=="XZhnnb":
        offsetVjet_  = RooRealVar("offsetVjet_",  "offset of the erf",    list_Vjet_pars[1][1],   200., 1000.)
    if channel=="XZhnnbb":
        offsetVjet_  = RooRealVar("offsetVjet_",  "offset of the erf",    list_Vjet_pars[1][1],   200., 500.)

    fitFuncVjet = list_function_name[0][1] 
    if fitFuncVjet == "ERFEXP": VjetMass_ = RooErfExpPdf("VjetMass_"  , fitFuncVjet, J_mass, constVjet_, offsetVjet_, widthVjet_)
    elif fitFuncVjet == "EXP" : VjetMass_ = RooExponential("VjetMass_", fitFuncVjet, J_mass, constVjet_)
    elif fitFuncVjet == "GAUS": VjetMass_ = RooGaussian("VjetMass_"   , fitFuncVjet, J_mass, offsetVjet_, widthVjet_)
    elif fitFuncVjet == "POL" : VjetMass_ = RooChebychev("VjetMass_"  , fitFuncVjet, J_mass, RooArgList(a0Vjet_, a1Vjet_, a2Vjet_))
    elif fitFuncVjet == "POW" : VjetMass_ = RooGenericPdf("VjetMass_" , fitFuncVjet, "@0^@1", RooArgList(J_mass, a0Vjet_))


    VjetMass_.plotOn(plot_MC_fit_Vjet_frame, RooFit.Normalization(setVjet.sumEntries() ,RooAbsReal.NumEvent))

    # VV -----------
    plot_MC_fit_VV_frame = J_mass.frame(RooFit.Title("plot fit VV MC"))

    print "the used data set is: ", list_of_set[2][0][0]
    setVV = list_of_set[2][0][1]
    setVV.plotOn(plot_MC_fit_VV_frame)

    constVV_  = RooRealVar("constVV_",  "slope of the exp",                list_VV_pars[0][1] ,   -0.1,   0.)
    offsetVV_ = RooRealVar("offsetVV_", "offset of the erf",               list_VV_pars[1][1] ,     1., 300.)
    widthVV_  = RooRealVar("widthVV_",  "width of the erf",                list_VV_pars[2][1] ,     1., 100.)
    erfrVV_   = RooErfExpPdf("baseVV_", "error function for VV jet mass", J_mass, constVV_, offsetVV_, widthVV_)
    expoVV_   = RooExponential("baseVV_", "error function for VV jet mass", J_mass, constVV_)

    meanVV_   = RooRealVar("meanVV_",   "mean of the gaussian",            list_VV_pars[3][1] ,    60., 100.)
    sigmaVV_  = RooRealVar("sigmaVV_",  "sigma of the gaussian",           list_VV_pars[4][1] ,     6.,  30.)
    fracVV_   = RooRealVar("fracVV_",   "fraction of gaussian wrt erfexp", list_VV_pars[5][1] ,     0.,   1.)
    gausVV_   = RooGaussian("gausVV_",  "gaus for VV jet mass", J_mass, meanVV_, sigmaVV_)

    meanVH_   = RooRealVar("meanVH_",   "mean of the gaussian",            list_VV_pars[6][1] ,   100., 150.)
    sigmaVH_  = RooRealVar("sigmaVH_",  "sigma of the gaussian",           list_VV_pars[7][1] ,     5.,  50.)
    fracVH_   = RooRealVar("fracVH_",   "fraction of gaussian wrt erfexp", list_VV_pars[8][1] ,     0.,   1.)
    gausVH_   = RooGaussian("gausVH_",  "gaus for VH jet mass", J_mass, meanVH_, sigmaVH_)

    fitFuncVV = list_function_name[1][1]
    if fitFuncVV   == "ERFEXPGAUS" : VVMass_ = RooAddPdf("VVMass_",fitFuncVV , RooArgList(gausVV_, erfrVV_), RooArgList(fracVV_))
    elif fitFuncVV == "ERFEXPGAUS2": VVMass_ = RooAddPdf("VVMass_",fitFuncVV , RooArgList(gausVH_, gausVV_, erfrVV_), RooArgList(fracVH_, fracVV_))
    elif fitFuncVV == "EXPGAUS"    : VVMass_ = RooAddPdf("VVMass_",fitFuncVV , RooArgList(gausVV_, expoVV_), RooArgList(fracVV_))
    elif fitFuncVV == "EXPGAUS2"   : VVMass_ = RooAddPdf("VVMass_",fitFuncVV , RooArgList(gausVH_, gausVV_, expoVV_), RooArgList(fracVH_, fracVV_))


    VVMass_.plotOn(plot_MC_fit_VV_frame, RooFit.Normalization(setVV.sumEntries() ,RooAbsReal.NumEvent))

    # top -----------
    plot_MC_fit_Top_frame = J_mass.frame(RooFit.Title("plot fit Top MC"))

    print "the used data set is: ", list_of_set[3][0][0]
    setTop = list_of_set[3][0][1]
    setTop.plotOn(plot_MC_fit_Top_frame)

    constTop_  = RooRealVar("constTop_",  "slope of the exp",                list_Top_pars[0][1] ,   -1.,   0.)
    offsetTop_ = RooRealVar("offsetTop_", "offset of the erf",               list_Top_pars[1][1] ,   50., 250.)
    widthTop_  = RooRealVar("widthTop_",  "width of the erf",                list_Top_pars[2][1] ,    1., 300.)
    gausTop_   = RooGaussian("baseTop_",  "gaus for Top jet mass", J_mass, offsetTop_, widthTop_)
    erfrTop_   = RooErfExpPdf("baseTop_", "error function for Top jet mass", J_mass, constTop_, offsetTop_, widthTop_)

    meanW_     = RooRealVar("meanW_",     "mean of the gaussian",            list_Top_pars[3][1] , 70., 90.)
    sigmaW_    = RooRealVar("sigmaW_",    "sigma of the gaussian",           list_Top_pars[4][1] ,  2., 20.)
    fracW_     = RooRealVar("fracW_",     "fraction of gaussian wrt erfexp", list_Top_pars[5][1] , 0.,  1.)
    gausW_     = RooGaussian("gausW_",    "gaus for W jet mass", J_mass, meanW_, sigmaW_)

    meanT_     = RooRealVar("meanT_",     "mean of the gaussian",            list_Top_pars[6][1] , 150., 200.)
    sigmaT_    = RooRealVar("sigmaT_",    "sigma of the gaussian",           list_Top_pars[7][1] ,   5.,  30.)
    fracT_     = RooRealVar("fracT_",     "fraction of gaussian wrt erfexp", list_Top_pars[8][1] ,  0.,   1.)
    gausT_     = RooGaussian("gausT_",    "gaus for T jet mass", J_mass, meanT_, sigmaT_)

    if channel=="XZheeb" or channel=="XZheebb" or channel=="XZhmmb" or channel=="XZhmmbb":
        offsetTop_ = RooRealVar("offsetTop_", "offset of the erf", list_Top_pars[1][1],   -50., 450.)
        widthTop_  = RooRealVar("widthTop_",  "width of the erf" , list_Top_pars[2][1],    1., 1000.)

    fitFuncTop = list_function_name[2][1]
    if fitFuncTop == "ERFEXPGAUS2" : TopMass_ = RooAddPdf("TopMass_"  , fitFuncTop, RooArgList(gausW_, gausT_, erfrTop_), RooArgList(fracW_, fracT_))
    elif fitFuncTop == "ERFEXPGAUS": TopMass_ = RooAddPdf("TopMass_"  , fitFuncTop, RooArgList(gausT_, erfrTop_)        , RooArgList(fracT_))
    elif fitFuncTop == "GAUS3"     : TopMass_ = RooAddPdf("TopMass_"  , fitFuncTop, RooArgList(gausW_, gausT_, gausTop_), RooArgList(fracW_, fracT_))
    elif fitFuncTop == "GAUS2"     : TopMass_ = RooAddPdf("TopMass_"  , fitFuncTop, RooArgList(gausT_, gausTop_)        , RooArgList(fracT_))
    elif fitFuncTop == "GAUS"      : TopMass_ = RooGaussian("TopMass_", fitFuncTop, J_mass, offsetTop_, widthTop_)


    TopMass_.plotOn(plot_MC_fit_Top_frame, RooFit.Normalization(setTop.sumEntries() ,RooAbsReal.NumEvent))

    # save plot 

    Save_name = Save_Dir + "/" + "plot_fit_MC.pdf"
    c1 = TCanvas("c1","",800,600)

    c1.cd()
    plot_MC_fit_Vjet_frame.Draw()
    c1.Print(Save_name + "(")

    c1.cd()
    plot_MC_fit_VV_frame.Draw()
    c1.Print(Save_name)

    c1.cd()
    plot_MC_fit_Top_frame.Draw()
    c1.Print(Save_name + ")" )

    # ------ 2. use the shape and number from MC to generate toy MC ----------


    constVjet_ .setConstant(True)
    offsetVjet_.setConstant(True)
    widthVjet_ .setConstant(True)
    a0Vjet_    .setConstant(True)
    a1Vjet_    .setConstant(True)
    a2Vjet_    .setConstant(True)
    
    constVV_   .setConstant(True)
    offsetVV_  .setConstant(True)
    widthVV_   .setConstant(True)
    meanVV_    .setConstant(True)
    sigmaVV_   .setConstant(True)
    fracVV_    .setConstant(True)
    meanVH_    .setConstant(True)
    sigmaVH_   .setConstant(True)
    fracVH_    .setConstant(True)
    
    constTop_  .setConstant(True)
    offsetTop_ .setConstant(True)
    widthTop_  .setConstant(True)
    meanW_     .setConstant(True)
    sigmaW_    .setConstant(True)
    fracW_     .setConstant(True)
    meanT_     .setConstant(True)
    sigmaT_    .setConstant(True)
    fracT_     .setConstant(True)

    nTotal_MC = setVjet.sumEntries() + setVV.sumEntries()+  setTop.sumEntries() 

    print ""
    print "setVjet.sumEntries(): ", setVjet.sumEntries()
    print "setVV.sumEntries(): ", setVV.sumEntries()
    print "setTop.sumEntries(): ", setTop.sumEntries()
    print "nTotal_MC: ", nTotal_MC 
    print ""

    frac_Vjet_MC   = RooRealVar("frac_Vjet_MC", "", setVjet.sumEntries() / nTotal_MC  , 0., 1.)
    frac_VV_MC     = RooRealVar("frac_VV_MC", ""  , setVV.sumEntries()   / nTotal_MC  , 0., 1.)

    print ""
    frac_Vjet_MC.Print()
    frac_VV_MC.Print()
    print ""

    frac_Vjet_MC.setConstant(True)
    frac_VV_MC.setConstant(True)

    list_frac_Vjet_VV_Top = [ frac_Vjet_MC.getVal(), frac_VV_MC.getVal(), (1- frac_Vjet_MC.getVal() - frac_VV_MC.getVal() ) ]

    # use this PDF of three backgrounds to generate toy MC 
    Bkg_Mass_MC = RooAddPdf("Bkg_Mass_MC","Vjet + VV + Top", RooArgList( VjetMass_ , VVMass_ , TopMass_ ), RooArgList(frac_Vjet_MC ,frac_VV_MC ))

    
    Save_name1 = Save_Dir + "/" + "plot_toy_MC.pdf"
    c2 = TCanvas("c2","",800,600)

    Save_name2 = Save_Dir + "/" + "plot_fit_toy_MC.pdf"
    c3 = TCanvas("c3","",800,600)

    Save_name3 = Save_Dir + "/" + "plot_fit_toy_MC_with_component.pdf"
    c4 = TCanvas("c4","",800,600)

    list_frame1 = []
    list_frame2 = []
    list_frame3 = []

    h_Bias = TH1D("h_Bias","h_Bias ",40,-1,1)
    h_Pull = TH1D("h_Pull","h_Pull ",40,-8,8)

    h_Bias_converged = TH1D("h_Bias_converged","h_Bias ",40,-1,1)
    h_Pull_converged = TH1D("h_Pull_converged","h_Pull ",40,-8,8)

    # starts loop

    times_max = 1000

    counter_all = 0
    counter_converged =0
    counter_bias_deno_zero = 0

    nTotal_MC = nTotal_MC*10
#    nTotal_MC = nTotal_MC*100
    print "the # used to generate pesudo-data: ", nTotal_MC

    print ""
    print "starting loop"
    for times in range(0,times_max):  

	print "times:", times

	if times % 50 == 0 :
		print "Processing times:", times+1 ,"of", times_max

        plot_toy_MC_frame, fit_toy_MC_frame, fit_toy_MC_component_frame,  Bias, Pull, fit_status = Bias_and_Pull_Box(J_mass, channel, list_function_name, list_Vjet_pars, list_VV_pars, list_Top_pars, list_of_set ,Save_Dir, nTotal_MC, Bkg_Mass_MC, list_frac_Vjet_VV_Top )

        # to avoid to save too many plot in list
	if times < 20 : 
		list_frame1.append( plot_toy_MC_frame  )
                list_frame2.append( fit_toy_MC_frame  )
                list_frame3.append( fit_toy_MC_component_frame  )

	counter_all = counter_all+1

	if fit_status ==0: counter_converged = counter_converged+1

        if fit_status ==0 and Bias != 999 : 
		h_Bias_converged.Fill( Bias ) 
		h_Pull_converged.Fill( Pull )

	if Bias != 999:
        	h_Bias.Fill( Bias )
        	h_Pull.Fill( Pull )

	if Bias == 999: counter_bias_deno_zero = counter_bias_deno_zero+1


    # end loop

    converged_rate = float(counter_converged)/counter_all

    print "counter_all: ", counter_all, " counter_converged: ", counter_converged, " converged rate: ", converged_rate 
    print "counter_bias_deno_zero: ", counter_bias_deno_zero

    # plot loop
    for i in range(0, len(list_frame1)  ):

	if i == 0:
		c2.cd()
        	list_frame1[i].Draw()
        	c2.Print(Save_name1 + "(")

                c3.cd()
                list_frame2[i].Draw()
                c3.Print(Save_name2 + "(") 

                c4.cd()
                list_frame3[i].Draw()
                c4.Print(Save_name3 + "(")


        if i!= 0 and i!= len(list_frame1)-1  :
                c2.cd()
                list_frame1[i].Draw()
                c2.Print(Save_name1)

                c3.cd()
                list_frame2[i].Draw()
                c3.Print(Save_name2)

                c4.cd()
                list_frame3[i].Draw()
                c4.Print(Save_name3)



        if i == len(list_frame1)-1 :
                c2.cd()
                list_frame1[i].Draw()
                c2.Print(Save_name1 + ")")

                c3.cd()
                list_frame2[i].Draw()
                c3.Print(Save_name2 + ")") 

                c4.cd()
                list_frame3[i].Draw()
                c4.Print(Save_name3 + ")")



    # end plot loop

    Save_name = Save_Dir + "/" + "Bias_and_Pull.pdf"
    c_1 = TCanvas("c_1","",800,400)
    c_1.Divide(2)

    c_1.cd(1)
    h_Bias.Draw()

    c_1.cd(2)
    h_Pull.Draw()
    c_1.SaveAs(Save_name)

    # ----------
    Save_name = Save_Dir + "/" + "Bias_and_Pull_converged.pdf"
    c_2 = TCanvas("c_1","",800,400)
    c_2.Divide(2)
    
    c_2.cd(1)
    h_Bias_converged.Draw()

    c_2.cd(2)
    h_Pull_converged.Draw()
    c_2.SaveAs(Save_name)

        

    # ------
    print ""
    print " End Yu_Hsiang_Box"
    print ""


    # end Yu_Hsiang_Box
    # -------------------------------------------





def Bias_and_Pull_Box(J_mass, channel, list_function_name, list_Vjet_pars, list_VV_pars, list_Top_pars, list_of_set ,Save_Dir, nTotal_MC, Bkg_Mass_MC , list_frac_Vjet_VV_Top ):

#    print ""
#    print "start Bias_and_Pull_Box"
#    print ""

    plot_toy_MC_frame = J_mass.frame(RooFit.Title("plot toy MC"))

    setVjet = list_of_set[1][0][1] 
    setVV = list_of_set[2][0][1]
    setTop = list_of_set[3][0][1]

    # generate toy MC

    nPseudo_data_fluc = gRandom.Poisson( nTotal_MC )

    pseudo_data_fluc = Bkg_Mass_MC.generate(RooArgSet(J_mass), nPseudo_data_fluc  ) 

    pseudo_data_SB_fluc = RooDataSet("pseudo_data_SB_fluc", "pseudo_data_SB_fluc", RooArgSet(J_mass), RooFit.Import(pseudo_data_fluc), RooFit.Cut("fatjet1_prunedMassCorr<65 || fatjet1_prunedMassCorr>135") )

    pseudo_data_SR_fluc = RooDataSet("pseudo_data_SR_fluc", "pseudo_data_SR_fluc", RooArgSet(J_mass), RooFit.Import(pseudo_data_fluc), RooFit.Cut("fatjet1_prunedMassCorr>105 && fatjet1_prunedMassCorr<135") )

    pseudo_data_VR_fluc = RooDataSet("pseudo_data_VR_fluc", "pseudo_data_VR_fluc", RooArgSet(J_mass), RooFit.Import(pseudo_data_fluc), RooFit.Cut("fatjet1_prunedMassCorr>65 && fatjet1_prunedMassCorr<105") )


    color1 = 8
    Bkg_Mass_MC.plotOn(plot_toy_MC_frame, RooFit.Normalization(nPseudo_data_fluc ,RooAbsReal.NumEvent),RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))
    color1 = 6
    Bkg_Mass_MC.plotOn(plot_toy_MC_frame, RooFit.Normalization(nPseudo_data_fluc ,RooAbsReal.NumEvent),RooFit.Components("VVMass_,TopMass_"),RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))
    color1 = 7
    Bkg_Mass_MC.plotOn(plot_toy_MC_frame, RooFit.Normalization(nPseudo_data_fluc ,RooAbsReal.NumEvent),RooFit.Components("TopMass_"),RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))
    pseudo_data_SB_fluc.plotOn(plot_toy_MC_frame)

    Bkg_Mass_MC.plotOn( plot_toy_MC_frame , RooFit.Normalization(nPseudo_data_fluc  ,RooAbsReal.NumEvent),RooFit.LineColor(4) )


    # ------ 3. fit the toy MC with ext PDF of background, fixed two secondary backgrounds' shape and normalization ----------

    fit_toy_MC_frame = J_mass.frame(RooFit.Title("fit toy MC"))
    fit_toy_MC_component_frame = J_mass.frame(RooFit.Title("fit toy MC with component"))

    # build another three PDF for 3 backgrounds

    # Vjet --------------------

    constVjet_fit   = RooRealVar("constVjet_fit" , "slope of the exp" ,  list_Vjet_pars[0][1],  -1.,   0.)
    offsetVjet_fit  = RooRealVar("offsetVjet_fit", "offset of the erf",  list_Vjet_pars[1][1], -50., 400.)
    widthVjet_fit   = RooRealVar("widthVjet_fit" , "width of the erf" ,  list_Vjet_pars[2][1],   1., 200.) #0, 400
    a0Vjet_fit      = RooRealVar("a0Vjet_fit"    , "width of the erf" ,  list_Vjet_pars[3][1],  -5 ,   0 )
    a1Vjet_fit      = RooRealVar("a1Vjet_fit"    , "width of the erf" ,  list_Vjet_pars[4][1],   0 ,   5 )
    a2Vjet_fit      = RooRealVar("a2Vjet_fit"    , "width of the erf" ,  list_Vjet_pars[5][1],  -1 ,   1 )

    if channel=="XZhnnb":
        offsetVjet_fit  = RooRealVar("offsetVjet_fit",  "offset of the erf",    list_Vjet_pars[1][1],   200., 1000.)
    if channel=="XZhnnbb":
        offsetVjet_fit  = RooRealVar("offsetVjet_fit",  "offset of the erf",    list_Vjet_pars[1][1],   200., 500.)

    fitFuncVjet = list_function_name[0][1]
    if fitFuncVjet == "ERFEXP": VjetMass_fit = RooErfExpPdf("VjetMass_fit"  , fitFuncVjet, J_mass,  constVjet_fit, offsetVjet_fit, widthVjet_fit)
    elif fitFuncVjet == "EXP" : VjetMass_fit = RooExponential("VjetMass_fit", fitFuncVjet, J_mass,  constVjet_fit)
    elif fitFuncVjet == "GAUS": VjetMass_fit = RooGaussian("VjetMass_fit"   , fitFuncVjet, J_mass,  offsetVjet_fit, widthVjet_fit)
    elif fitFuncVjet == "POL" : VjetMass_fit = RooChebychev("VjetMass_fit"  , fitFuncVjet, J_mass,  RooArgList(a0Vjet_fit, a1Vjet_fit, a2Vjet_fit))
    elif fitFuncVjet == "POW" : VjetMass_fit = RooGenericPdf("VjetMass_fit" , fitFuncVjet, "@0^@1", RooArgList(J_mass, a0Vjet_fit))


    # VV --------------------


    constVV_fit  = RooRealVar("constVV_fit",  "slope of the exp",                list_VV_pars[0][1] ,   -0.1,   0.)
    offsetVV_fit = RooRealVar("offsetVV_fit", "offset of the erf",               list_VV_pars[1][1] ,     1., 300.)
    widthVV_fit  = RooRealVar("widthVV_fit",  "width of the erf",                list_VV_pars[2][1] ,     1., 100.)
    erfrVV_fit   = RooErfExpPdf("baseVV_fit", "error function for VV jet mass", J_mass, constVV_fit, offsetVV_fit, widthVV_fit)
    expoVV_fit   = RooExponential("baseVV_fit", "error function for VV jet mass", J_mass, constVV_fit)

    meanVV_fit   = RooRealVar("meanVV_fit",   "mean of the gaussian",            list_VV_pars[3][1] ,    60., 100.)
    sigmaVV_fit  = RooRealVar("sigmaVV_fit",  "sigma of the gaussian",           list_VV_pars[4][1] ,     6.,  30.)
    fracVV_fit   = RooRealVar("fracVV_fit",   "fraction of gaussian wrt erfexp", list_VV_pars[5][1] ,     0.,   1.)
    gausVV_fit   = RooGaussian("gausVV_fit",  "gaus for VV jet mass", J_mass, meanVV_fit, sigmaVV_fit)

    meanVH_fit   = RooRealVar("meanVH_fit",   "mean of the gaussian",            list_VV_pars[6][1] ,   100., 150.)
    sigmaVH_fit  = RooRealVar("sigmaVH_fit",  "sigma of the gaussian",           list_VV_pars[7][1] ,     5.,  50.)
    fracVH_fit   = RooRealVar("fracVH_fit",   "fraction of gaussian wrt erfexp", list_VV_pars[8][1] ,     0.,   1.)
    gausVH_fit   = RooGaussian("gausVH_fit",  "gaus for VH jet mass", J_mass, meanVH_fit, sigmaVH_fit)

    fitFuncVV = list_function_name[1][1]
    if fitFuncVV   == "ERFEXPGAUS" : VVMass_fit = RooAddPdf("VVMass_fit",fitFuncVV , RooArgList(gausVV_fit, erfrVV_fit), RooArgList(fracVV_fit))
    elif fitFuncVV == "ERFEXPGAUS2": VVMass_fit = RooAddPdf("VVMass_fit",fitFuncVV , RooArgList(gausVH_fit, gausVV_fit, erfrVV_fit), RooArgList(fracVH_fit, fracVV_fit))
    elif fitFuncVV == "EXPGAUS"    : VVMass_fit = RooAddPdf("VVMass_fit",fitFuncVV , RooArgList(gausVV_fit, expoVV_fit), RooArgList(fracVV_fit))
    elif fitFuncVV == "EXPGAUS2"   : VVMass_fit = RooAddPdf("VVMass_fit",fitFuncVV , RooArgList(gausVH_fit, gausVV_fit, expoVV_fit), RooArgList(fracVH_fit, fracVV_fit))


    # Top --------------------

    constTop_fit  = RooRealVar("constTop_fit",  "slope of the exp",                list_Top_pars[0][1] ,   -1.,   0.)
    offsetTop_fit = RooRealVar("offsetTop_fit", "offset of the erf",               list_Top_pars[1][1] ,   50., 250.)
    widthTop_fit  = RooRealVar("widthTop_fit",  "width of the erf",                list_Top_pars[2][1] ,    1., 300.)
    gausTop_fit   = RooGaussian("baseTop_fit",  "gaus for Top jet mass", J_mass, offsetTop_fit, widthTop_fit)
    erfrTop_fit   = RooErfExpPdf("baseTop_fit", "error function for Top jet mass", J_mass, constTop_fit, offsetTop_fit, widthTop_fit)

    meanW_fit     = RooRealVar("meanW_fit",     "mean of the gaussian",            list_Top_pars[3][1] , 70., 90.)
    sigmaW_fit    = RooRealVar("sigmaW_fit",    "sigma of the gaussian",           list_Top_pars[4][1] ,  2., 20.)
    fracW_fit     = RooRealVar("fracW_fit",     "fraction of gaussian wrt erfexp", list_Top_pars[5][1] , 0.,  1.)
    gausW_fit     = RooGaussian("gausW_fit",    "gaus for W jet mass", J_mass, meanW_fit, sigmaW_fit)

    meanT_fit     = RooRealVar("meanT_fit",     "mean of the gaussian",            list_Top_pars[6][1] , 150., 200.)
    sigmaT_fit    = RooRealVar("sigmaT_fit",    "sigma of the gaussian",           list_Top_pars[7][1] ,   5.,  30.)
    fracT_fit     = RooRealVar("fracT_fit",     "fraction of gaussian wrt erfexp", list_Top_pars[8][1] ,  0.,   1.)
    gausT_fit     = RooGaussian("gausT_fit",    "gaus for T jet mass", J_mass, meanT_fit, sigmaT_fit)

    if channel=="XZheeb" or channel=="XZheebb" or channel=="XZhmmb" or channel=="XZhmmbb":
        offsetTop_fit = RooRealVar("offsetTop_fit", "offset of the erf", list_Top_pars[1][1],   -50., 450.)
        widthTop_fit  = RooRealVar("widthTop_fit",  "width of the erf" , list_Top_pars[2][1],    1., 1000.)

    fitFuncTop = list_function_name[2][1]
    if fitFuncTop == "ERFEXPGAUS2" : TopMass_fit = RooAddPdf("TopMass_fit"  , fitFuncTop, RooArgList(gausW_fit, gausT_fit, erfrTop_fit), RooArgList(fracW_fit, fracT_fit))
    elif fitFuncTop == "ERFEXPGAUS": TopMass_fit = RooAddPdf("TopMass_fit"  , fitFuncTop, RooArgList(gausT_fit, erfrTop_fit)        , RooArgList(fracT_fit))
    elif fitFuncTop == "GAUS3"     : TopMass_fit = RooAddPdf("TopMass_fit"  , fitFuncTop, RooArgList(gausW_fit, gausT_fit, gausTop_fit), RooArgList(fracW_fit, fracT_fit))
    elif fitFuncTop == "GAUS2"     : TopMass_fit = RooAddPdf("TopMass_fit"  , fitFuncTop, RooArgList(gausT_fit, gausTop_fit)        , RooArgList(fracT_fit))
    elif fitFuncTop == "GAUS"      : TopMass_fit = RooGaussian("TopMass_fit", fitFuncTop, J_mass, offsetTop_fit, widthTop_fit)


    # extended PDF --------------------

    N_Vjet = nPseudo_data_fluc * list_frac_Vjet_VV_Top[0] 
    N_VV   = nPseudo_data_fluc * list_frac_Vjet_VV_Top[1]
    N_Top  = nPseudo_data_fluc * list_frac_Vjet_VV_Top[2]

    nVjet_fit = RooRealVar("nVjet_fit","", N_Vjet, 0., 2*N_Vjet )
    nVV_fit   = RooRealVar("nVV_fit"  ,"", N_VV  , 0., 2*N_VV )
    nTop_fit  = RooRealVar("nTop_fit" ,"", N_Top , 0., 2*N_Top )

    nVV_fit.setConstant(True)
    nTop_fit.setConstant(True)

    constVV_fit .setConstant(True)
    offsetVV_fit.setConstant(True)
    widthVV_fit .setConstant(True)
    meanVV_fit  .setConstant(True)
    sigmaVV_fit .setConstant(True)
    fracVV_fit  .setConstant(True)
    meanVH_fit  .setConstant(True)
    sigmaVH_fit .setConstant(True)
    fracVH_fit  .setConstant(True)
    
    constTop_fit .setConstant(True)
    offsetTop_fit.setConstant(True)
    widthTop_fit .setConstant(True)
    meanW_fit    .setConstant(True)
    sigmaW_fit   .setConstant(True)
    fracW_fit    .setConstant(True)
    meanT_fit    .setConstant(True)
    sigmaT_fit   .setConstant(True)
    fracT_fit    .setConstant(True)


    VjetMass_ext_fit = RooExtendPdf("VjetMass_ext_fit",  "", VjetMass_fit,  nVjet_fit)
    VVMass_ext_fit = RooExtendPdf("VVMass_ext_fit",  "", VVMass_fit,  nVV_fit)
    TopMass_ext_fit = RooExtendPdf("TopMass_ext_fit",  "", TopMass_fit,  nTop_fit)

    BkgMass_fit = RooAddPdf("BkgMass_fit", "", RooArgList(VjetMass_ext_fit , VVMass_ext_fit, TopMass_ext_fit), RooArgList(nVjet_fit, nVV_fit, nTop_fit)) 

    BkgMass_fit.fixAddCoefRange("h_reasonable_range")

    # fit pseudo data in SB only


    VERBOSE = False
#    VERBOSE = True
    frMass_fit = BkgMass_fit.fitTo(pseudo_data_SB_fluc, RooFit.SumW2Error(True), RooFit.Extended(True), RooFit.Range("LSBrange,HSBrange"), RooFit.Strategy(2), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.PrintLevel(1 if VERBOSE else -1))

    if VERBOSE: print "********** Fit result [JET MASS DATA] **"+"*"*40, "\n", frMass_fit.Print(), "\n", "*"*80

    fit_status = frMass_fit.status()

    cor_fit = frMass_fit.correlationMatrix()

#    print ""

    jetMassArg = RooArgSet(J_mass)
    iSBVjet_fit = VjetMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
    iSBVV_fit = VVMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
    iSBTop_fit = TopMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))

    n_fit_MC_SB = nVjet_fit.getVal()*iSBVjet_fit.getVal() + nVV_fit.getVal()*iSBVV_fit.getVal() + nTop_fit.getVal()*iSBTop_fit.getVal()

    # plot

    pseudo_data_SB_fluc.plotOn( fit_toy_MC_frame )

    BkgMass_fit.plotOn( fit_toy_MC_frame, RooFit.Normalization(n_fit_MC_SB  ,RooAbsReal.NumEvent),RooFit.VisualizeError(frMass_fit ,1),RooFit.FillColor(5) )
    BkgMass_fit.plotOn( fit_toy_MC_frame, RooFit.Normalization(n_fit_MC_SB  ,RooAbsReal.NumEvent),RooFit.Range("h_reasonable_range") ,RooFit.LineColor(2) )
    Bkg_Mass_MC.plotOn( fit_toy_MC_frame, RooFit.Normalization(nPseudo_data_fluc  ,RooAbsReal.NumEvent),RooFit.LineColor(4) )
    pseudo_data_SB_fluc.plotOn( fit_toy_MC_frame )


    # plot with component

    pseudo_data_SB_fluc.plotOn( fit_toy_MC_component_frame )

    color1 = 8    
    BkgMass_fit.plotOn( fit_toy_MC_component_frame, RooFit.Normalization( n_fit_MC_SB ,RooAbsReal.NumEvent),RooFit.Range("h_reasonable_range"), RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))

    color1 = 6
    BkgMass_fit.plotOn( fit_toy_MC_component_frame, RooFit.Normalization( n_fit_MC_SB ,RooAbsReal.NumEvent),RooFit.Range("h_reasonable_range"), RooFit.Components("VVMass_ext_fit,TopMass_ext_fit"), RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))

    color1 = 7
    BkgMass_fit.plotOn( fit_toy_MC_component_frame, RooFit.Normalization( n_fit_MC_SB ,RooAbsReal.NumEvent),RooFit.Range("h_reasonable_range"), RooFit.Components("TopMass_ext_fit"),RooFit.LineColor(color1),RooFit.DrawOption("F"), RooFit.FillColor(color1), RooFit.FillStyle(1001))

    pseudo_data_SB_fluc.plotOn( fit_toy_MC_component_frame )
    Bkg_Mass_MC.plotOn( fit_toy_MC_component_frame , RooFit.Normalization(nPseudo_data_fluc  ,RooAbsReal.NumEvent),RooFit.LineColor(4) )

    BkgMass_fit.plotOn( fit_toy_MC_component_frame , RooFit.Normalization( n_fit_MC_SB ,RooAbsReal.NumEvent),RooFit.Range("h_reasonable_range") ,RooFit.LineColor(2) )


    # ------ 4. calculate the Signal region yield, bias and pull ----------

    iSRVjet_fit = VjetMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
    iSRVV_fit = VVMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
    iSRTop_fit = TopMass_fit.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))

    SRyield_fit = RooFormulaVar("SRyield_fit", "extrapolation to SR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSRVjet_fit, nVjet_fit, iSRVV_fit, nVV_fit, iSRTop_fit, nTop_fit))


    SRyield_fit_error = SRyield_fit.getPropagatedError( frMass_fit )

#    print "pseudo_data_SR_fluc.sumEntries(): ", pseudo_data_SR_fluc.sumEntries()

    if pseudo_data_SR_fluc.sumEntries() != 0: Bias = ( SRyield_fit.getVal() - pseudo_data_SR_fluc.sumEntries() )/ pseudo_data_SR_fluc.sumEntries()
    if pseudo_data_SR_fluc.sumEntries() == 0: Bias = 999


    Pull = ( SRyield_fit.getVal() - pseudo_data_SR_fluc.sumEntries() )/ SRyield_fit_error  

#    print "SRyield_fit.getVal(): ", SRyield_fit.getVal() 
#    print "pseudo_data_SR_fluc.sumEntries(): ", pseudo_data_SR_fluc.sumEntries()
#    print "SRyield_fit_error: ", SRyield_fit_error
#    print "Bias: ", Bias
#    print "Pull: ", Pull

    return ( plot_toy_MC_frame , fit_toy_MC_frame , fit_toy_MC_component_frame,  Bias, Pull, fit_status )

#    print ""
#    print "end Bias_and_Pull_Box"
#    print ""
    # end Bias_and_Pull_Box
    # -------------------------------------------


jobs = []

if options.all:
    for c in channelList:
        p = multiprocessing.Process(target=alpha, args=(c,))
        jobs.append(p)
        p.start()
else:
    if options.channel in channelList: alpha(options.channel)
    else:
        print "Channel not set or not recognized. Quitting..."
        exit()
