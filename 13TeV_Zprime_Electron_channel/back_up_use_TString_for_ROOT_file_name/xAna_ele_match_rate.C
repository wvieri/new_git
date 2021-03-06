// example code to run Bulk Graviton->ZZ->ZlepZhad selections on electron-channel

// Now Yu-Hsiang change it to Zprime->Zh->ZlepZhad selections on electron-channel
#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <TString.h>
#include <map>
#include <TH1D.h>
#include <TFile.h>
#include "untuplizer.h"
#include <TClonesArray.h>
#include <TLorentzVector.h>
#include <string>
#include "TCanvas.h"

using namespace std;
void xAna_ele_match_rate(/*std::string*/ TString inputFile, /*TCanvas *c1 , TCanvas *c2 , TCanvas *c3 ,TCanvas *c4 ,TCanvas *c5 , */
int mass_point ,double eff,double eff_err, TString dir_name, int dir_flag ){


  // define histograms

 TString title2 = Form("ele pT for Zprime mass = %d",mass_point);
 TString title3 = Form("lepton pairs' pT for Zprime mass = %d",mass_point);
 TString title4 = Form("SD mass for Zprime mass = %d",mass_point);
 TString title5 = Form("Z mass for Zprime mass = %d",mass_point);

 TH1D* h_ele_pT = new TH1D("h_ele_pT", title2 ,300 , 0,3000 );
 TH1D* h_lepton_pair_pT = new TH1D("h_lepton_pair_pT", title3 ,400 , 0,4000 );
// TH1D* h_SD_mass = new TH1D("h_SD_mass", title4 ,100 , 0,1000 );
 TH1D* h_SD =new TH1D("h_SD",title4 ,100,0,200);
 TH1D* h_Z_mass= new TH1D("h_Z_mass",title5 ,250,0,500);

  //get TTree from file ...
//  TreeReader data(inputFile.data());
  TreeReader data(inputFile.Data());

  Long64_t nTotal=0;
  Long64_t nPass[20]={0};
  Long64_t nJets_Nminus3Cuts=0;
  Long64_t nJets_Nminus3Cuts_=0;

  Long64_t nMatchZeroB=0;
  Long64_t nMatchOneB=0;
  Long64_t nMatchTwoB=0;

  ofstream fout;
  fout.open("ele_Eiko.txt");
//  TH1F* h_SD=new TH1F("h_SD","",100,0,200);

  //Event loop
  for(Long64_t jEntry=0; jEntry<data.GetEntriesFast() ;jEntry++){

    if (jEntry % 50000 == 0)
      fprintf(stderr, "Processing event %lli of %lli\n", jEntry + 1, data.GetEntriesFast());

    data.GetEntry(jEntry);
    nTotal ++;

    // 0. check the generator-level information and make sure there is a Z->e+e-
    Int_t nGenPar        = data.GetInt("nGenPar");
    Int_t* genParId      = data.GetPtrInt("genParId");
    Int_t* genParSt      = data.GetPtrInt("genParSt");
    Int_t* genMomParId   = data.GetPtrInt("genMomParId");
    Int_t* genDa1      = data.GetPtrInt("genDa1");
    Int_t* genDa2      = data.GetPtrInt("genDa2");
    TClonesArray* genParP4 = (TClonesArray*) data.GetPtrTObject("genParP4");

    bool hasLepton=false;

    for(int ig=0; ig < nGenPar; ig++){

      if(genParId[ig]!=23)continue;
      int da1=genDa1[ig];
      int da2=genDa2[ig];

      if(da1<0 || da2<0)continue;
      int da1pdg = genParId[da1];
      int da2pdg = genParId[da2];

      if(abs(da1pdg)==11)
     	hasLepton=true;

      if(hasLepton)break;

    }

    // 1. make sure there is a h-> bb, Yu-Hsiang change it
    bool hasHadron=false;
    std::vector<int> B_quark_from_Higgs_gen_index;

    for(int ig=0; ig < nGenPar; ig++){

      if(genParId[ig]!=25)continue;
      int da1=genDa1[ig];
      int da2=genDa2[ig];

      if(da1<0 || da2<0)continue;
      int da1pdg = genParId[da1];
      int da2pdg = genParId[da2];

      if(abs(da1pdg)==5)
     	{hasHadron=true;
	B_quark_from_Higgs_gen_index.push_back(da1);
	B_quark_from_Higgs_gen_index.push_back(da2);}

      if(hasHadron)break;

    }

/*    for(unsigned int i=0; i< B_quark_from_Higgs_gen_index.size(); i++){
       cout<<"i: "<< i <<endl;
       cout<<"gen index: "<< B_quark_from_Higgs_gen_index[i] <<endl;
       cout<<"particle IDi: "<< genParId[B_quark_from_Higgs_gen_index[i]] <<endl;
    }
*/


    
    if(!hasLepton)continue;
    nPass[0]++;
    if(!hasHadron)continue;
    nPass[1]++;
     
    //2. pass electron or muon trigger
    std::string* trigName = data.GetPtrString("hlt_trigName");
    vector<bool> &trigResult = *((vector<bool>*) data.GetPtr("hlt_trigResult"));
    const Int_t nsize = data.GetPtrStringSize();

    bool passTrigger=false;
    for(int it=0; it< nsize; it++)
      {
 	std::string thisTrig= trigName[it];
 	bool results = trigResult[it];

	// std::cout << thisTrig << " : " << results << std::endl;
	
 	if( (thisTrig.find("HLT_Ele105")!= std::string::npos && results==1)
	    ||
	    (thisTrig.find("HLT_Mu45")!= std::string::npos && results==1)
	    )
 	  {
 	    passTrigger=true;
 	    break;
 	  }


      }


    if(!passTrigger)continue;
    nPass[2]++;


    //3. has a good vertex
    Int_t nVtx        = data.GetInt("nVtx");
    if(nVtx<1)continue;
    nPass[3]++;

    //4. look for good electrons first
    Int_t nEle         = data.GetInt("nEle");
    Int_t run          = data.GetInt("runId");
    Int_t lumi         = data.GetInt("lumiSection");
    Int_t event        = data.GetInt("eventId");
    vector<bool> &passHEEPID = *((vector<bool>*) data.GetPtr("eleIsPassHEEPNoIso"));
    TClonesArray* eleP4 = (TClonesArray*) data.GetPtrTObject("eleP4");
    Float_t* eleSCEta         = data.GetPtrFloat("eleScEta");
    Float_t* eleMiniIso       = data.GetPtrFloat("eleMiniIso");
    Int_t*   eleCharge        = data.GetPtrInt("eleCharge");

    //5. select good electrons
    std::vector<int> goodElectrons;

    for(int ie=0; ie< nEle; ie++)
      {

    	TLorentzVector* thisEle = (TLorentzVector*)eleP4->At(ie);

    	if(fabs(thisEle->Eta())>2.5)continue;

    	if(! (fabs(eleSCEta[ie])<1.442 || fabs(eleSCEta[ie])>1.566))continue;

	double ele_pt_threshold = -999;
	if (dir_flag ==1){ele_pt_threshold = 0;}
        if (dir_flag ==2 || dir_flag ==3 || dir_flag ==6 ){ele_pt_threshold = 85;}
        if (dir_flag ==4){ele_pt_threshold = 100;}
        if (dir_flag ==5){ele_pt_threshold = 115;}
        if (dir_flag ==7 || dir_flag ==8 || dir_flag ==9 ){ele_pt_threshold = 115;}


    	if(thisEle->Pt() < ele_pt_threshold )continue;
//     	  if(thisEle->Pt() < 115)continue;
//        if(thisEle->Pt() < 100)continue;
//        if(thisEle->Pt() < 85)continue;

    	if(!passHEEPID[ie])continue;
    	
    	if(eleMiniIso[ie]>0.1)continue;

    	goodElectrons.push_back(ie);
      }

	
    //6. select a good Z boson
    bool findEPair=false;
    TLorentzVector l4_Z(0,0,0,0);
    std::vector<double> LeptonPairPt;
    std::vector<double> LeptonPairM;

    for(unsigned int i=0; i< goodElectrons.size(); i++)
      {
	int ie = goodElectrons[i];
	TLorentzVector* thisEle = (TLorentzVector*)eleP4->At(ie);

	for(unsigned int j=0; j< i; j++)
	  {
	    int je= goodElectrons[j];

	    if(eleCharge[ie]*eleCharge[je]>0)continue;

	    TLorentzVector* thatEle = (TLorentzVector*)eleP4->At(je);

	    Float_t mll  = (*thisEle+*thatEle).M();
	    Float_t ptll = (*thisEle+*thatEle).Pt();
	    

	    if(mll<70 || mll>110)continue;

            double ll_pt_threshold = -999;
            if (dir_flag ==1){ll_pt_threshold = 0;}
            if (dir_flag ==2 ||dir_flag ==3 ||dir_flag ==4 ||dir_flag ==5 ||dir_flag ==6 ){ll_pt_threshold = 200;}

            if(ptll<ll_pt_threshold )continue;
//	    if(ptll<200)continue;


            LeptonPairPt.push_back(ptll);
            LeptonPairM.push_back(mll);

	    if(!findEPair)l4_Z=(*thisEle+*thatEle);

	    findEPair=true;
	  }	
      }

    if(!findEPair)
      continue;
    nPass[4]++;


    //7.select a good CA8 and cleaned jet

    // first select muons for cleaning against jet
    std::vector<int> goodMuons;
    Int_t nMu          = data.GetInt("nMu");
    vector<bool> &isHighPtMuon = *((vector<bool>*) data.GetPtr("isHighPtMuon"));
    vector<bool> &isCustomTrackerMuon = *((vector<bool>*) data.GetPtr("isCustomTrackerMuon"));
    TClonesArray* muP4 = (TClonesArray*) data.GetPtrTObject("muP4");
    Float_t* muMiniIso       = data.GetPtrFloat("muMiniIso");

    for(int im=0; im< nMu; im++)
      {

    	TLorentzVector* thisMu = (TLorentzVector*)muP4->At(im);

    	if(!isHighPtMuon[im] && !isCustomTrackerMuon[im])continue;
    	
    	if(muMiniIso[im]>0.1)continue;	

        if ( goodMuons.size()==1 ) {
	  bool highPt_AND_tracker = isHighPtMuon[0] && isCustomTrackerMuon[im];
	  bool tracker_AND_highPt = isHighPtMuon[im] && isCustomTrackerMuon[0]; 
            if ( !(highPt_AND_tracker or tracker_AND_highPt) ) continue; 
        }

    	if(fabs(thisMu->Eta())>2.1)continue;

    	if(thisMu->Pt() < 50)continue;

    	goodMuons.push_back(im);
      }

	
    Int_t nJet         = data.GetInt("FATnJet");
    TClonesArray* jetP4 = (TClonesArray*) data.GetPtrTObject("FATjetP4");
    Float_t*  jetSDmass = data.GetPtrFloat("FATjetSDmass");

    std::vector<double> SD_Mass;
    std::vector<int> SD_jet_index;
    TLorentzVector l4_leadingJet(0,0,0,0);
    bool findAJet=false;
    for(int ij=0; ij<nJet; ij++)
      {
    	
     	TLorentzVector* thisJet = (TLorentzVector*)jetP4->At(ij);


        double SD_low = -999, SD_high = 999;
        if (dir_flag ==1){ SD_low= 0; SD_high = 9999;}
        if (dir_flag ==2){ SD_low= 40; SD_high = 140;}
        if (dir_flag ==3){ SD_low= 50; SD_high = 140;}
        if (dir_flag ==4 || dir_flag ==5 || dir_flag ==6){ SD_low= 60; SD_high = 140;}

        if (dir_flag ==7){ SD_low= 93; SD_high = 143;}
        if (dir_flag ==8){ SD_low= 95; SD_high = 145;}
        if (dir_flag ==9){ SD_low= 91; SD_high = 141;}

        if(jetSDmass[ij]<SD_low || jetSDmass[ij]>SD_high)continue;
//	if(jetSDmass[ij]<50 || jetSDmass[ij]>110)continue; // this is soft drop mass ?
//      if(jetSDmass[ij]<105 || jetSDmass[ij]>145)continue;  // Yu-Hsiang change to Higgs mass window
//      if(jetSDmass[ij]<60 || jetSDmass[ij]>140)continue;  // Yu-Hsiang change to Higgs mass window
//      if(jetSDmass[ij]<50 || jetSDmass[ij]>140)continue;  // Yu-Hsiang change to Higgs mass window
//      if(jetSDmass[ij]<40 || jetSDmass[ij]>140)continue;  // Yu-Hsiang change to Higgs mass window

	bool hasOverLap=false;
	for(unsigned int ie=0; ie < goodElectrons.size(); ie++)
	  {
	    TLorentzVector* thisEle = (TLorentzVector*)eleP4->At(goodElectrons[ie]);
	    if(thisEle->DeltaR(*thisJet)<0.8)hasOverLap=true;
	    if(hasOverLap)break;
	    
	  }
	for(unsigned int im=0; im < goodMuons.size(); im++)
	  {
	    TLorentzVector* thisMuo = (TLorentzVector*)muP4->At(goodMuons[im]);
	    if(thisMuo->DeltaR(*thisJet)<0.8)hasOverLap=true;
	    if(hasOverLap)break;
	    
	  }
	
	if(hasOverLap)continue;
	
	if(thisJet->Pt()<200)continue;
	if(fabs(thisJet->Eta())>2.4)continue;

     	if(!findAJet)
	  {
	    l4_leadingJet = *thisJet;
//	    h_SD->Fill(jetSDmass[ij]);
//            SD_Mass.push_back( jetSDmass[ij] );
	  }
	    
     	findAJet=true;
        SD_Mass.push_back( jetSDmass[ij] ); // change to this place so that loop to all jets passing cuts    	
	SD_jet_index.push_back( ij );
        nJets_Nminus3Cuts ++;// count # of jets passing N-3 cuts
      }
    
    if(!findAJet)
      continue;
    nPass[5]++;

     Float_t MGrav = (l4_leadingJet + l4_Z).M();
     if(MGrav<400)continue;
     nPass[6]++;

  // if event can go here, then fill the histograms to plot the distributions. Yu-Hsiang add 

    for(unsigned int i=0; i< goodElectrons.size(); i++)
      {         int ie = goodElectrons[i];
		TLorentzVector* thisEle = (TLorentzVector*)eleP4->At(ie);
		h_ele_pT->Fill( thisEle->Pt() );
      }

    for(unsigned int i=0; i< LeptonPairPt.size(); i++)
      {         
                
                h_lepton_pair_pT->Fill( LeptonPairPt[i] );
      }

    for(unsigned int i=0; i< LeptonPairM.size(); i++)
      {

                h_Z_mass->Fill( LeptonPairM[i] );
      }

    for(unsigned int i=0; i< SD_Mass.size(); i++)
      {

                h_SD->Fill( SD_Mass[i] );
                nJets_Nminus3Cuts_++;
      }

  //////// ask the b quark match rate


if(B_quark_from_Higgs_gen_index.size()!=2){cout<<"# of b quarks != 2"<<endl;}
if(B_quark_from_Higgs_gen_index.size()==2){

    int da1 = B_quark_from_Higgs_gen_index[0];
                TLorentzVector* thisBquark = (TLorentzVector*)genParP4->At(da1);

    int da2 = B_quark_from_Higgs_gen_index[1];
                TLorentzVector* thatBquark = (TLorentzVector*)genParP4->At(da2);

    for(unsigned int i=0; i< SD_jet_index.size(); i++){
        
//	if(SD_Mass[i]<20)continue;
//      if(SD_Mass[i]>20)continue;

//      if(SD_Mass[i]<40)continue;
//      if(SD_Mass[i]>40)continue;

//      if(SD_Mass[i]<60)continue;
//      if(SD_Mass[i]>60)continue;

      if(SD_Mass[i]<20 || SD_Mass[i]>220 )continue;

	int jet_index = SD_jet_index[i];
        TLorentzVector* theJet = (TLorentzVector*)jetP4->At( jet_index );
//        if( SD_Mass )

        // no match B quark
        if( (theJet->DeltaR(*thisBquark)) >=0.8 && (theJet->DeltaR(*thatBquark)) >=0.8  )
	{ nMatchZeroB++; }

        // match only one B quark
        if( ((theJet->DeltaR(*thisBquark)) <0.8 && (theJet->DeltaR(*thatBquark)>=0.8)) || 
	    ((theJet->DeltaR(*thisBquark)) >=0.8 && (theJet->DeltaR(*thatBquark)<0.8)) )
	{ nMatchOneB++;} 

	// match two B quark
        if( (theJet->DeltaR(*thisBquark)) <0.8 && (theJet->DeltaR(*thatBquark))<0.8)
	{ nMatchTwoB++;}


      }// end loop
}//end if
  ////////

    fout << run << " " << lumi << " " << event << endl;
    

  } // end of loop over entries

  fout.close();
  std::cout << "nTotal    = " << nTotal << std::endl;
  for(int i=0;i<20;i++)
    if(nPass[i]>0)
      std::cout << "nPass[" << i << "]= " << nPass[i] << std::endl;




  //  Yu-Hsiang add calulation of total efficiency and eff uncertainty


  double pass =-99,fail=-99,f_over_p=-99,f_over_p_error=-99;
//  double n_total = nTotal;// from int to double
  double n_total = nPass[1];// from int to double

eff = nPass[6]/n_total;
pass = nPass[6];
fail = nTotal -  nPass[6];
f_over_p = fail/pass;
f_over_p_error = f_over_p * sqrt( (1/fail) + (1/pass) );
eff_err = f_over_p_error/pow( 1 + f_over_p ,2);

//cout<<"eff: "<< eff << "   eff_err: "<< eff_err <<endl;

cout<< "nJets_Nminus3Cuts: "<< nJets_Nminus3Cuts <<endl;
cout<< "nJets_Nminus3Cuts_: "<< nJets_Nminus3Cuts_ <<endl;

cout<< "nMatchZeroB: "<< nMatchZeroB <<endl;
cout<< "nMatchOneB: "<< nMatchOneB <<endl;
cout<< "nMatchTwoB: "<< nMatchTwoB <<endl;

double NMatchZeroB,NMatchOneB,NMatchTwoB,match_at_least_1_rate,match_2_rate;
NMatchZeroB = nMatchZeroB;
NMatchOneB = nMatchOneB;
NMatchTwoB = nMatchTwoB;

match_at_least_1_rate = (NMatchOneB + NMatchTwoB)/(NMatchZeroB + NMatchOneB + NMatchTwoB);
match_2_rate = NMatchTwoB/(NMatchZeroB + NMatchOneB + NMatchTwoB);

cout<<"match_at_least_1_rate: "<< match_at_least_1_rate <<endl;
cout<<"match_2_rate:"<< match_2_rate <<endl;
  // Yu-Hsiang add cut flow figure


  TString title1 = Form("Cut Flow for Zprime mass = %d, eff=%f +/- %f",mass_point,eff,eff_err);

  TH1D* h_CutFlow = new TH1D("h_CutFlow", title1 ,8 , 0,8 );

  char* cut_name[8] = {"Began","Z->ee in Gen","H->bb in Gen","HLT","Vertex","Leptons","V-jet","Zprime mass"};

	for(int i=1;i<=8;i++){ // i is the index of column of cut flow plot 
		if(i==1) {h_CutFlow->SetBinContent(i,nTotal); }
        	else {h_CutFlow->SetBinContent(i,nPass[i-2]); }
		h_CutFlow->GetXaxis()->SetBinLabel( i , cut_name[i-1] );
	}

//

  TString png1_name = Form("Zprime_Cut_Flow_M_%d.png",mass_point);
  TString png2_name = Form("Zprime_ele_pT_M_%d.png",mass_point);
  TString png3_name = Form("Zprime_ll_pT_M_%d.png",mass_point);
  TString png4_name = Form("Zprime_SD_mass_M_%d.png",mass_point);
  TString png5_name = Form("Zprime_Z_mass_M_%d.png",mass_point);



//   TCanvas *c1 = new TCanvas("c1","try to show cut flow ",200,10,700,500);
  //c1->cd();
/*
  gPad->SetGridx();
//  gPad->SetLogy();

  h_CutFlow->SetMarkerStyle(8);
  h_CutFlow->SetMarkerSize(1);
  h_CutFlow->GetXaxis()->SetLabelSize(0.041);
//  h_CutFlow->GetYaxis()->SetLabelSize(0.035);

  h_CutFlow->SetStats(0);
  h_CutFlow->SetMarkerSize(2.0);

 // h_CutFlow->Draw();
 // h_CutFlow->Draw("HIST TEXT0 SAME");

*/
//
    // Yu-Hsiang add drawing histogram of distributuion
/*
  c2->cd();
  h_ele_pT->Draw();

  c3->cd();
  h_lepton_pair_pT->Draw();

  c4->cd();
  h_SD->Draw();

  c5->cd();
  h_Z_mass->Draw();
*/
////

   // Yu-Hsiang add that save TH1D in the ROOT file


//   TString ROOT_name = Form("test_ROOT_name_M-%d.root",mass_point);
//   TString ROOT_name = Form("plot_TurnOff3Cuts/Zprime_shape_M-%d.root",mass_point);

//   TString ROOT_name = Form("plot_Cut_SD40to140_ElePt85_llPt200/Zprime_shape_M-%d.root",mass_point);
//   TString ROOT_name = Form("plot_Cut_SD50to140_ElePt85_llPt200/Zprime_shape_M-%d.root",mass_point);
//   TString ROOT_name = Form("plot_Cut_SD60to140_ElePt100_llPt200/Zprime_shape_M-%d.root",mass_point);
//   TString ROOT_name = Form("plot_Cut_SD60to140_ElePt115_llPt200/Zprime_shape_M-%d.root",mass_point);
//   TString ROOT_name = Form("plot_Cut_SD60to140_ElePt85_llPt200/Zprime_shape_M-%d.root",mass_point);

/*
   TString ROOT_name = Form("Zprime_shape_M-%d.root",mass_point);
   ROOT_name = dir_name + ROOT_name; 

   TFile *myFile = new TFile(ROOT_name,"recreate");

   h_CutFlow->Write();
   h_ele_pT->Write();
   h_lepton_pair_pT->Write();
   h_SD->Write();
   h_Z_mass->Write();

   myFile->Close();
   delete myFile;
*/

   // delete the finished used TH1D so it will not replacing the existing TH1 (no potential memory leak warning) when loop again 
/*
   delete h_CutFlow;
   delete h_ele_pT;
   delete h_lepton_pair_pT;
   delete h_SD;
   delete h_Z_mass;
*/
}
