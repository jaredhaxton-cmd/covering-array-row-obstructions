// Certificate producer. Receives witness indices from scripts/generate.py.
// Each output record: 3 unsigned bytes, one t-column-subset index per removed row.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;
int main(int argc,char**argv) try {
    if(argc!=2) throw runtime_error("usage: generate OUTPUT < prepared-witnesses");
    int n,k,m; if(!(cin>>n>>k>>m)||n<3||k<1||m<1||m>255) throw runtime_error("invalid header");
    vector<vector<int>> rows(n,vector<int>(k));
    for(auto &r:rows) for(auto &s:r) if(!(cin>>s)||s<0) throw runtime_error("invalid row");
    vector<vector<int>> cols(m);
    for(auto &c:cols){int l;if(!(cin>>l)||l<1||l>k)throw runtime_error("invalid column set");for(int j=0;j<l;j++){int a;if(!(cin>>a)||a<0||a>=k)throw runtime_error("invalid column");c.push_back(a);}}
    vector<vector<int>> w(n);
    for(auto &q:w){int l;if(!(cin>>l)||l<0||l>m)throw runtime_error("invalid witness count");for(int j=0;j<l;j++){int a;if(!(cin>>a)||a<0||a>=m)throw runtime_error("invalid witness ID");q.push_back(a);}}
    ofstream f(argv[1],ios::binary); if(!f)throw runtime_error("cannot open output");
    auto has=[&](int c,int j){return find(cols[c].begin(),cols[c].end(),j)!=cols[c].end();};
    auto conflict=[&](int x,int a,int y,int b){for(int j:cols[a])if(has(b,j)&&rows[x][j]!=rows[y][j])return true;return false;};
    long long total=0,distinct=0,search=0,unresolved=0; auto start=chrono::steady_clock::now();
    for(int x=0;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
        ++total;
        unsigned char out[3]={255,255,255};
        bool found=false;
        // Fast path: three different symbols in a shared column, each with a
        // singleton witness containing the column. Never assumes this condition.
        for(int j=0;j<k&&!found;j++){
            if(rows[x][j]==rows[y][j]||rows[x][j]==rows[z][j]||rows[y][j]==rows[z][j])continue;
            int ids[3]={-1,-1,-1},r[3]={x,y,z};
            for(int h=0;h<3;h++)for(int a:w[r[h]])if(has(a,j)){ids[h]=a;break;}
            if(ids[0]>=0&&ids[1]>=0&&ids[2]>=0){for(int h=0;h<3;h++)out[h]=static_cast<unsigned char>(ids[h]);found=true;++distinct;}
        }
        if(!found){
            for(int a:w[x]){if(found)break;for(int b:w[y]){if(found)break;if(!conflict(x,a,y,b))continue;
                for(int c:w[z])if(conflict(x,a,z,c)&&conflict(y,b,z,c)){
                    out[0]=static_cast<unsigned char>(a);out[1]=static_cast<unsigned char>(b);out[2]=static_cast<unsigned char>(c);found=true;++search;break;
                }
            }}
        }
        if(!found)++unresolved;
        f.write(reinterpret_cast<const char*>(out),3);
    }
    f.close();if(!f)throw runtime_error("certificate write failed");
    cout<<"triples="<<total<<" distinct_symbol="<<distinct<<" searched_triangles="<<search<<" unresolved="<<unresolved
        <<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"\n";
    return 0;
} catch(const exception&e){cerr<<e.what()<<"\n";return 2;}
