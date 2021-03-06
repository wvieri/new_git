/// \file
/// \ingroup tutorial_roofit
///  'BASIC FUNCTIONALITY' RooFit tutorial macro #101
///
///  Fitting, plotting, toy data generation on one-dimensional p.d.f
///
///  pdf = gauss(x,m,s)
///
///
/// \macro_code
/// \author 07/2008 - Wouter Verkerke 


#ifndef __CINT__
#include "RooGlobalFunc.h"
#endif
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooCBShape.h"
#include "TCanvas.h"
#include "RooPlot.h"
#include "TAxis.h"
#include "RooGenericPdf.h"
#include "RooAddPdf.h"
#include "RooProdPdf.h"
#include "TFile.h"
#include <TString.h>
#include "TTree.h"
#include "TRandom.h"
//#include ""


using namespace RooFit ;

TTree* makeTTree() ;


void roofit_test2()
{

/*

  // 1. basic test
  // ------------------------------------------------------------------------------------------


  // S e t u p   m o d e l 
  // ---------------------

  // Declare variables x,mean,sigma with associated name, title, initial value and allowed range
  RooRealVar x("x","x",-10,10) ;
  RooRealVar mean("mean","mean of gaussian",0,-10,10) ;
  RooRealVar sigma("sigma","width of gaussian",1,0.1,10) ;

  cout<<"test"<< endl;
  mean.Print() ;
  sigma.Print() ;

  // Build gaussian p.d.f in terms of x,mean and sigma
  RooGaussian gauss("gauss","gaussian PDF",x,mean,sigma) ;  

  // Construct plot frame in 'x'
  RooPlot* xframe = x.frame(Title("Gaussian p.d.f."),Bins(20)) ;


  // P l o t   m o d e l   a n d   c h a n g e   p a r a m e t e r   v a l u e s
  // ---------------------------------------------------------------------------

  // Plot gauss in frame (i.e. in x) 
  gauss.plotOn(xframe) ;

  // Change the value of sigma to 3
  sigma.setVal(3) ;

  // Plot gauss in frame (i.e. in x) and draw frame on canvas
  gauss.plotOn(xframe,LineColor(kRed)) ;


  // G e n e r a t e   e v e n t s 
  // -----------------------------

  // Generate a dataset of 1000 events in x from gauss
  RooDataSet* data = gauss.generate(x,2000) ;  
  
  // Make a second plot frame in x and draw both the 
  // data and the p.d.f in the frame
  RooPlot* xframe2 = x.frame(Title("Gaussian p.d.f. with data"),Bins(20)) ;
  data->plotOn(xframe2) ;

  cout<<"before fit"<< endl;
  mean.Print() ;
  sigma.Print() ;


  // F i t   m o d e l   t o   d a t a
  // -----------------------------

  // Fit pdf to data
  gauss.fitTo(*data) ;

  // Print values of mean and sigma (that now reflect fitted values and errors)
  gauss.plotOn(xframe2,LineColor(kRed)) ;

  cout<<"after fit"<< endl;
  mean.Print() ;
  sigma.Print() ;

  gauss.Print();
  Double_t val = gauss.getVal();
//  Double_t val = sigma.getVal();
  cout<<"val: "<< val << endl;


  RooArgSet* paramSet1 = gauss.getDependents(data) ; 
  paramSet1->Print("v") ;

  RooArgSet* paramSet2 = gauss.getParameters(data) ; 
  paramSet2->Print("v") ;

  RooArgSet s1(mean,sigma);
  s1.Print() ;

  RooArgList l1(mean,mean,sigma) ;
  l1.Print() ;

  // Draw all frames on a canvas
  TCanvas* c = new TCanvas("rf101_basics","rf101_basics",800,400) ;
  c->Divide(2) ;
  c->cd(1) ; gPad->SetLeftMargin(0.15) ; xframe->GetYaxis()->SetTitleOffset(1.6) ; xframe->Draw() ;
  c->cd(2) ; gPad->SetLeftMargin(0.15) ; xframe2->GetYaxis()->SetTitleOffset(1.6) ; xframe2->Draw() ;




  // 2. building PDFs
  // ------------------------------------------------------------------------------------------


  // observable y and its frame
  RooRealVar y("y","y",-10,10) ;
  RooPlot* yframe = y.frame(Title("frame of y")) ;


  // Gaussian
  // -----------------------------

  RooRealVar mean_g2("mean","mean of gaussian",0,-10,10) ;
  RooRealVar sigma_g2("sigma","width of gaussian",1,0.1,10) ;

  RooGaussian gauss2("gauss2","gaussian PDF",y,mean_g2,sigma_g2) ;

  gauss2.plotOn(yframe,LineColor(kRed)) ;

  // Crystal ball shape
  // -----------------------------

  RooRealVar mean_CB("mean","mean of crystal ball",4,-10,10) ;
  RooRealVar sigma_CB("sigma","width of crystal ball",1,0.1,10) ;
  RooRealVar alpha_CB("alpha","alpha of crystal ball",1,0.1,10) ;
  RooRealVar N_CB("N","N of crystal ball",3,0.1,10) ;

  RooCBShape crystal_ball("CB_shape","crystal ball PDF",y,mean_CB,sigma_CB,alpha_CB,N_CB) ; 

  crystal_ball.plotOn(yframe,LineColor(kGreen)) ;


  // Generic PDF defined by C++ math formula 
  // -----------------------------


//  RooRealVar z("z","z",0,5) ;
  RooRealVar z("z","z",1.0) ;
//  RooPlot* zframe = z.frame(Title("frame of z")) ;

  RooRealVar a("a","a",3.0) ;
  RooRealVar b("b","b",-5000.0) ;

  RooGenericPdf gp("gp","Generic PDF","exp(y*z+a)-b*y", RooArgSet(y,z,a,b)) ;
//  RooGenericPdf gp("gp","Generic PDF","-b*y", RooArgSet(y,z,a,b)) ;
//  RooGenericPdf gp("gp","Generic PDF","exp(y*z)", RooArgSet(y,z,a,b)) ;

  gp.plotOn(yframe,LineColor(kOrange)) ;
//  gp.plotOn(zframe,LineColor(kOrange)) ;



*/

  // Addition 
  // -----------------------------
/*
  RooRealVar frac1("frac1","fraction of fn 1",0.5) ;

  RooAddPdf sum("sum","g2+CB",RooArgList(gauss2,crystal_ball),RooArgList(frac1)) ;

  sum.plotOn(yframe); 
//  sum.plotOn(yframe,Components(RooArgSet(crystal_ball)),LineColor(kGreen)) ;
//  sum.plotOn(yframe,Components(RooArgSet(gauss2)),LineColor(kGreen)) ;
*/


/*

  RooRealVar frac1("frac1","fraction of fn 1",0.5) ;
//  RooRealVar frac2("frac2","fraction of fn 1",0.33) ;

//  RooAddPdf sum("sum","g2+CB+gp",RooArgList(gauss2,gp),RooArgList(frac1)) ;
  RooAddPdf sum("sum","g2+CB+gp",RooArgList(crystal_ball,gp),RooArgList(frac1)) ;


  sum.plotOn(yframe) ;
//  sum.plotOn(yframe,Components(RooArgSet(gauss2,crystal_ball)),LineColor(kGreen)) ;

  // Has Problem ***
  RooAddPdf sum2("sum2","g2+CB+gp",RooArgList(crystal_ball,gauss2),RooArgList(frac1)) ;
  sum2.plotOn(yframe,LineColor(kMagenta)) ;


  RooRealVar mean_g5("mean","mean of gaussian",-6,-10,10) ;
  RooRealVar sigma_g5("sigma","width of gaussian",1,0.1,10) ;

  RooGaussian gauss5("gauss3","gaussian PDF",y,mean_g5,sigma_g5) ;

  gauss5.plotOn(yframe,LineColor(kViolet)) ;

  // Has Problem ***
  RooAddPdf sum3("sum3","g2+CB+gp",RooArgList(gauss2,gauss5),RooArgList(frac1)) ;
  sum3.plotOn(yframe,LineColor(kGray)) ;


  // multiplying 
  // -----------------------------

  // ------------test in y frame and w frame
  RooRealVar w("w","w",0,5) ;
  RooPlot* wframe = w.frame(Title("frame of w")) ;


  RooRealVar mean_g3("mean","mean of gaussian",3,-10,10) ;
  RooRealVar sigma_g3("sigma","width of gaussian",1,0.1,10) ;

  RooGaussian gauss3("gauss3","gaussian PDF",w,mean_g3,sigma_g3) ;
//  gauss3.plotOn(wframe,LineColor(kRed)) ;


  RooProdPdf prod("Gaus_times_gp","g3 * gp", RooArgList(gauss3,gp)) ;

//  prod.plotOn(yframe) ;
//  prod.plotOn(wframe) ;


  // ------------test all in y frame
  RooRealVar mean_g4("mean","mean of gaussian",0,-10,10) ;
  RooRealVar sigma_g4("sigma","width of gaussian",4,0.1,10) ;

  RooGaussian gauss4("gauss4","gaussian PDF",y,mean_g4,sigma_g4) ;
//  gauss4.plotOn(yframe,LineColor(kRed)) ;

//  gp.plotOn(yframe,LineColor(kOrange)) ;

  RooProdPdf prod2("Gaus_times_gp","g4 * gp", RooArgList(gauss4,gp)) ;

//  prod2.plotOn(yframe) ;



  // Plot
  // -----------------------------
  TCanvas* c2 = new TCanvas("c2","Canvas for building PDFs",800,400) ;
  c2->Divide(2) ;
  c2->cd(1) ; gPad->SetLeftMargin(0.15) ; yframe->GetYaxis()->SetTitleOffset(1.6) ; yframe->Draw() ;
  c2->cd(2) ; gPad->SetLeftMargin(0.15) ; wframe->GetYaxis()->SetTitleOffset(1.6) ; wframe->Draw() ;
//  c2->cd(2) ; gPad->SetLeftMargin(0.15) ; wframe->GetYaxis()->SetTitleOffset(1.6) ; zframe->Draw() ;


*/

  // test to open the ROOT file and TTree


  TString inputFile ="../jacopo_codes/ntuples/ZprimeToZhToZinvhbb_narrow_M-1000_13TeV-madgraph-v1.root" ; 
  TFile *file = new TFile (inputFile );

  TTree* tree = (TTree*)file->Get("SR") ;


  // test 1 ------------


  RooRealVar genV_pt("genV_pt","gen V pt",0,1200) ;
  RooRealVar jet1_pt("jet1_pt","jet 1 pt",0,1500) ;

//  RooDataSet dataset("dataset","data set",tree,RooArgSet(gen_V_pt,jet_1_pt));
  RooDataSet dataset("dataset","data set",RooArgSet(genV_pt,jet1_pt), Import(*tree),Cut("genV_pt>300 && genV_pt<500") );

  cout<<endl<<endl<<endl;
  cout<<"---------open ROOT file and TTree in Roofit----------------------"<< endl;
  cout<<"dataset entry: "<< dataset.sumEntries() << endl;




  const RooArgSet* row ;//= dataset.get(901) ;
  RooRealVar* xrow ;//= (RooRealVar*) row->find("gen_V_pt") ;

  for(int index = 1; index <=1000;index++){
	
	row = dataset.get(index) ;
	xrow = (RooRealVar*) row->find("genV_pt") ;
        cout <<"index: "<< index << "  value: "<< xrow->getVal() << endl ;

  }


  // show what variables this dataset has
//  dataset.Print("v") ;

  // show the 900 th row of the dataset, i.e. the value of variables in the 900th event 
//  const RooArgSet* row = dataset.get(901) ;
//  row->Print("v") ;

  // in the 900th event, show only the value of variable "gen_V_pt"
//  RooRealVar* xrow = (RooRealVar*) row->find("gen_V_pt") ;
//  cout << xrow->getVal() << endl ;

  // from dataset to make new dataset d1 that has only one variable gen_V_pt 
  RooDataSet* d1 = (RooDataSet*) dataset.reduce(RooArgSet(genV_pt)) ;
  d1->Print("v") ;  

  // from dataset to make new dataset d2 that has only one variable jet_1_pt
//  RooDataSet* d2 = (RooDataSet*) dataset.reduce(RooArgSet(jet_1_pt)) ;
//  d2->Print("v") ;


  RooPlot* d1_frame = genV_pt.frame(Title("frame of genV_pt")) ;
  d1->plotOn(d1_frame) ;

//  RooPlot* d2_frame = jet_1_pt.frame(Title("frame of jet_1_pt")) ;
//  d2->plotOn(d2_frame) ;


  // ------------------------------------------

/*

  TTree* tree2 = makeTTree() ;

  // Define observables x,y,z
  RooRealVar x("x","x",-10,10) ;
  RooRealVar y("y","y",-10,10) ;
  RooRealVar z("z","z",-10,10) ;

  // Import only observables (y,z)
  RooDataSet ds("ds","ds",RooArgSet(x,y),Import(*tree2)) ;
  ds.Print() ;

  // Import observables (x,y,z) but only event for which (y+z<0) is true
  RooDataSet ds2("ds2","ds2",RooArgSet(x,y,z),Import(*tree2),Cut("y+z<0")) ;
  ds2.Print() ;


  // reduce to 1 variable
//  RooDataSet* d3 = (RooDataSet*) ds.reduce(RooArgSet(x)) ;
  RooDataSet* d3 = (RooDataSet*) ds.reduce(RooArgSet(y)) ;
  d3->Print("v") ;


  RooPlot* xframe = x.frame(Title("frame of x")) ;
//  d3->plotOn(xframe) ;

  RooPlot* yframe = y.frame(Title("frame of y")) ;
  d3->plotOn(yframe) ;


    cout<<"d3 dataset entry: "<< d3->sumEntries() << endl;


  const RooArgSet* row2 ; ;
  RooRealVar* xrow2 ;

  for(int index = 0; index < d3->sumEntries();index++){

        row2 = d3->get(index) ;
        xrow2 = (RooRealVar*) row2->find("y") ;
        cout <<"index: "<< index << "  value: "<< xrow2->getVal() << endl ;

  }
*/


  // ------------------------------------------




  TCanvas* c3 = new TCanvas("c3","Canvas for draw the two variable separately",800,400) ;
  c3->Divide(2) ;
  c3->cd(1) ; gPad->SetLeftMargin(0.15) ; d1_frame->GetYaxis()->SetTitleOffset(1.6) ; d1_frame->Draw() ;
//  c3->cd(2) ; gPad->SetLeftMargin(0.15) ; d2_frame->GetYaxis()->SetTitleOffset(1.6) ; d2_frame->Draw() ;
//  c3->cd(); yframe->Draw() ;





}

TTree* makeTTree() 
{

// Create ROOT TTree filled with a Gaussian distribution in x and a uniform distribution in y

  TTree* tree = new TTree("tree","tree") ;
  Double_t* px = new Double_t ;
  Double_t* py = new Double_t ;
  Double_t* pz = new Double_t ;
  Int_t*    pi = new Int_t ;
  tree->Branch("x",px,"x/D") ;
  tree->Branch("y",py,"y/D") ;
  tree->Branch("z",pz,"z/D") ;
  tree->Branch("i",pi,"i/I") ;
  for (int i=0 ; i<1000 ; i++) {
    *px = gRandom->Gaus(0,3) ;
    *py = gRandom->Uniform()*30 - 15 ;
    *pz = gRandom->Gaus(0,5) ;
    *pi = i % 3 ;
    tree->Fill() ;
  }
  return tree ;
}





