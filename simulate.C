void simulate(){

    //make dir
    try{
        gSystem->Exec("mkdir Data");
        gSystem->Exec("mkdir Data/run_005408");
    }
    catch(...){
        cout<<"Directory exists";
    } 


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