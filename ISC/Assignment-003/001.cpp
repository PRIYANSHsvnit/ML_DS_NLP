#include <bits/stdc++.h>
using namespace std;

int main()
{
    string s; // CipherText String
    cout<<"Enter the CipherText = ";
    cin>>s;
    cout<<"\n All possible decryptions of the given CipherText are = \n\n";
    for(int i=1;i<26;i++)
    {
        string x = "";
        for(char c:s)
        {
            if(c>='A' && c<='Z')
            {
                x += char((c-'A'-i+26)%26+'A');
            }
            else if(c>='a' && c<='z')
            {
                x += char((c-'a'-i+26)%26+'a');
            }
            else
            {
                x += c;
            }
        }
        cout<<"Shift "<<i<<" = "<<x<<endl;
    }
    return 0;
}