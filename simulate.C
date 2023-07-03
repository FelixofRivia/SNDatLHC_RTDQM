


/*
void simulate(){
    TChain* event = new TChain("data");
    event->Add("./sample.root");
    TRandom* r = new TRandom();
    r->SetSeed(0);
    TFile* outf = new TFile("./Data/run_5408/data_0000.root","recreate");
    TTree* newtree = new TTree();
    newtree->SetName("data");
    int e = 15000;
    bool run = true;
    int k=0;
    int N=0;
    while(run){ 
        
        N = r->Integer(e-10000);
        newtree=event->CopyTree("","",10000,N);
        for (int i=0;i<10000;i++){} 
        outf->cd();
        newtree->Write("", TObject::kOverwrite);
        outf->Close();
        cout<<"done\n";
        k++;
        sleep(15);
        outf = new TFile("./Data/run_5408/data_0000.root","recreate");
    }
}
*/
/*
void simulate(){
    TChain* event = new TChain("data");
    event->Add("./sample.root");
    TRandom* r = new TRandom();
    r->SetSeed(0);
    TFile* outf = new TFile("./Data/run_5408/data_0000.root","recreate");
    TTree* newtree = new TTree();
    newtree->SetName("data");
    int e = 15000;
    bool run = true;
    int k=0;
    int N=0;
    N = r->Integer(e-10000);
    newtree=event->CopyTree("","",10000,N);
    outf->cd();
    newtree->Write("", TObject::kOverwrite);
    outf->Close();
    cout<<"done\n";
    k++;
    sleep(15);
    Long64_t t1=0;
    Long64_t t2=0;
    event->SetBranchAddress("evt_timestamp",&t1);
    newtree->SetBranchAddress("evt_timestamp",&t2);
    while(run){ 
        outf = new TFile("./Data/run_5408/data_0000.root","recreate");
        N = r->Integer(e-10000);
        for (int i=0;i<10000;i++){
            event->GetEntry(i+N);
            t2=10;
            newtree->Fill();
        } 
        outf->cd();
        newtree->Write("", TObject::kOverwrite);
        outf->Close();
        cout<<"done\n";
        k++;
        sleep(15);
    }
}
*/
/*
void simulate(){
    TChain* event = new TChain("data");
    event->Add("./sample.root");

    TFile* outf = new TFile("./Data/run_5408/data_0000.root","recreate");
    TTree* newtree = event->CloneTree(0);
    newtree->SetName("data");
    int e = 15000;
    bool run = true;
    int k=0;
    int steps=1000;
    while(run){ 
        k++;
        for (int i=0;i<steps*k;i++){
            event->GetEntry(i);
            for (int n=0; n<10; n++){
                newtree->Fill();
            } 
        } 
        outf->cd();
        newtree->Write("", TObject::kOverwrite);
        outf->Close();
        cout<<"done\t"<<k<<endl;
        if (k==e/steps) break;
        sleep(e/steps-k);
        outf = new TFile("./Data/run_5408/data_0000.root","update");
        newtree = event->CloneTree(0);
    }
}
*/

void simulate(){
    TChain* event = new TChain("data");
    event->Add("./sample.root");

    TFile* outf = new TFile("./Data/run_005408/data_0000.root","recreate");
    TTree* newtree = new TTree();
    //TTree* newtree = event->CloneTree(0);
    newtree->SetName("data");
    int e = 50000;
    bool run = true;
    int k=0;
    int steps=1000;
    while(run){ 
        newtree=event->CopyTree("","",steps*(k+1)+1,0);
        outf->cd();
        newtree->Write("", TObject::kOverwrite);
        outf->Close();
        cout<<"done\t"<<k<<endl;
        k++;
        if (k==e/steps) break;
        sleep(30);
        outf = new TFile("./Data/run_005408/data_0000.root","update");
        newtree = new TTree();
        //newtree = event->CloneTree(0);
    }
}