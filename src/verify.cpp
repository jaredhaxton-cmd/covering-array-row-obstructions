// Certificate checker: reconstructs the interaction multiplicities from the
// original array itself; neither imports nor calls the certificate producer.
// Input: N K t v header followed by N*K integers. Certificate: raw 3-byte records.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
int main(int argc,char**argv) try {
    if(argc!=3&&argc!=4)throw runtime_error("usage: verify HEADERED_ARRAY RAW_CERT [--allow-unresolved]");
    bool allow=argc==4&&string(argv[3])=="--allow-unresolved";if(argc==4&&!allow)throw runtime_error("unknown flag");
    ifstream a(argv[1]); int n,k,t,v;
    if(!(a>>n>>k>>t>>v)||n<3||k<1||t<1||t>k||v<2||k>64)throw runtime_error("invalid array dimensions");
    vector<vector<int>> row(n,vector<int>(k));for(auto &r:row)for(int &s:r)if(!(a>>s)||s<0||s>=v)throw runtime_error("invalid symbol or truncated input");
    string tail;if(a>>tail)throw runtime_error("extra array input");
    vector<vector<int>> columns;vector<int> cur;
    function<void(int)> visit=[&](int j){if((int)cur.size()==t){columns.push_back(cur);if(columns.size()>255)throw runtime_error("too many column sets for certificate v1");return;}
       for(int c=j;c<=k-(t-(int)cur.size());++c){cur.push_back(c);visit(c+1);cur.pop_back();}};
    visit(0);size_t m=columns.size(),q=1;
    for(int i=0;i<t;i++){if(q>static_cast<size_t>(n)/v)throw runtime_error("not covering: v^t > N");q*=v;}
    // Independent approach: base-v encoding and direct multiplicity arrays.
    vector<vector<unsigned char>> unique(n,vector<unsigned char>(m,0));
    vector<uint64_t> mask(m);
    long long singleton=0;size_t minw=m,maxw=0,all_columns_rows=0;
    for(size_t c=0;c<m;c++){
        for(int j:columns[c])mask[c]|=uint64_t(1)<<j;
        vector<int> count(q),last(q,-1);
        for(int r=0;r<n;r++){size_t e=0;for(int j:columns[c])e=e*v+row[r][j];++count[e];last[e]=r;}
        for(size_t e=0;e<q;e++){if(count[e]==0)throw runtime_error("input is not covering");if(count[e]==1){unique[last[e]][c]=1;++singleton;}}
    }
    const uint64_t full=k==64?~uint64_t(0):(uint64_t(1)<<k)-1;
    for(int r=0;r<n;r++){uint64_t cm=0;size_t count=0;for(size_t c=0;c<m;c++)if(unique[r][c]){cm|=mask[c];++count;}
        if(cm==full)++all_columns_rows;
        minw=min(minw,count);maxw=max(maxw,count);
    }
    // Direct conflict test; independently checks each certificate edge.
    auto conflict=[&](int r,int c,int s,int d){uint64_t common=mask[c]&mask[d];for(int j=0;j<k;j++)if((common&(uint64_t(1)<<j))&&row[r][j]!=row[s][j])return true;return false;};
    ifstream f(argv[2],ios::binary);if(!f)throw runtime_error("cannot read certificate stream");
    long long total=0,verified=0,unresolved=0;auto start=chrono::steady_clock::now();
    for(int x=0;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
        unsigned char b[3]; if(!f.read(reinterpret_cast<char*>(b),3))throw runtime_error("truncated certificate at triple "+to_string(total));++total;
        if(b[0]==255&&b[1]==255&&b[2]==255){++unresolved;if(!allow)throw runtime_error("unresolved triple "+to_string(total-1));continue;}
        int i=b[0],j=b[1],l=b[2];
        if(i>=(int)m||j>=(int)m||l>=(int)m||!unique[x][i]||!unique[y][j]||!unique[z][l])
            throw runtime_error("invalid singleton witness at triple "+to_string(total-1));
        if(!conflict(x,i,y,j)||!conflict(x,i,z,l)||!conflict(y,j,z,l))
            throw runtime_error("missing conflict edge at triple "+to_string(total-1));
        ++verified;
    }
    char b;if(f.get(b))throw runtime_error("extra certificate bytes");if(!f.eof())throw runtime_error("certificate read error");
    cout<<"coverage=verified interactions="<<q*m<<" distinct_rows="<<set<vector<int>>(row.begin(),row.end()).size()
        <<" singleton_interactions="<<singleton<<" witnesses_per_row_min="<<minw<<" witnesses_per_row_max="<<maxw
        <<" all_columns_rows="<<all_columns_rows<<"\n";
    cout<<"triples="<<total<<" verified="<<verified<<" unresolved="<<unresolved
        <<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"\n";
    return 0;
} catch(const exception&e){cerr<<"REJECT: "<<e.what()<<"\n";return 1;}
