// arguments [-c] [-f filename] [-c count]  fields
// -f filename
//	will put last retrieved value to filename , overwriting anyother contents
//
// -c The number of full frames to decode, then exit
//
// fields
//	4 values , seperated by commas, where value
// 	 	1 = offset from start of data, this value is bytes
//		2 = length, how many bits
//		3 =  if length > 1 this is the multiplier
//			 if length = 1 this is the bit position within the byte
//					use for bit fields, like error mask, relay mask etc.
//		4 = format, p = plus , add the returned value to the next field
//					t = time , format the output as time
//					any other value is ignored.
//					future will include c=*C, f=*F, l=logical (bit fields true/false), y = yes/no (bit fields)
// to get this information for your model, check the wiki or look in the Vbus XMl file in Resol lite.
//
// example:
// cat raw.log | ./a.out -f rrdvals -c 1 0,15,0.1 2,15,0.1 4,15,0.1 6,15,0.1 8,7,1 9,7,1 20,16,1,p 22,16,1000,p 24,16,1000000 12,16,0,t 10,1,0 10,1,1
// will give temp of s1,s2,s3,s4 pumpspeed pump1,pump2 and total of watts, formatted system time, r1 and r2 status for a resol deltasol bs plus, put them into a file called rrdvals, and exit after decoding one frame successfully
//45.7 24.6 49.8 29.1 100 0 2609964 14:36 1 0

#include <stdio.h>
#include <iostream>
using namespace std;

int adding = 0,model=0;
float totals;
string presults;
unsigned char frame[4],allframes[256];

void giveresults(char parray[])
{
    string formatter;
    char *format = NULL;
    float f;
    char results[24];
    int offset = atoi(strtok (parray,","));
    int length = atoi(strtok (NULL, ","));
    if (length == 1) {
        int bitposition = atoi(strtok (NULL, ","));
        f = (((allframes[offset] >> bitposition) & 0x01 ) * 0x01);
        sprintf(results, "%.0f ",f);
        presults.append(results);
    } else {
        float multiplier = atof(strtok (NULL, ","));
        if (((length -1) /24) ) {
            f = (allframes[offset] + (allframes[offset+1]*0x100) + (allframes[offset+2]*0x1000) + (allframes[offset+3]*0x10000) ) * multiplier;
        } else if (((length -1) /16) ) {
            f = (allframes[offset] + (allframes[offset+1]*0x100) + (allframes[offset+2]*0x1000) ) * multiplier;
        } else if (((length -1) /8) ) {
            f = (allframes[offset] + (allframes[offset+1]*0x100)) * multiplier;
        } else if (multiplier !=0 ) {
            f = (allframes[offset] ) * multiplier;
        }
        format = strtok (NULL, ",");
        if (format != NULL) {
            formatter = format;
            if (formatter == "p" ) {
                adding = 1;
                totals = totals + f;
            } else if (formatter == "t" ) {
                int time  = (allframes[offset] + (allframes[offset+1]*0x100));
                int hours = time/60;
                int mins = time - (hours*60);
                sprintf(results, "%02d:%02d ",hours,mins);
            }
        } else if (multiplier < 1) {
            sprintf(results, "%.1f ",f);
        } else sprintf(results, "%.0f ",f);
        if ((formatter != "p") && (adding == 1)) {
            totals = totals + f;
            sprintf(results, "%.0f ",totals);
            adding = 0;
            totals = 0;
        }
        if (formatter != "p") presults.append(results);
    }
}

int decodeheader()
{
    char  buffer[10];
    unsigned char a;
    unsigned char b;
    if (scanf("%c%c%c%c%c%c%c%c%c",&buffer[0],&buffer[1],&buffer[2],&buffer[3],&buffer[4],&buffer[5],&buffer[6],&buffer[7],&buffer[8],&buffer[9]) != 1)
    {
        a = buffer[0] + buffer[1] + buffer[2] + buffer[3] + buffer[4] + buffer[5] + buffer[6] + buffer[7];
        b = ~ a;
        a = buffer[8];
    }
    if (  a == b )
    {
        model = buffer[3] * 0x100  + buffer[2];
        a = buffer[7];
        return a;
    } else {
        return 0;
    }
}

int decodeframe(int x)
{
    char  buffer[7] ;
    unsigned char a;
    unsigned char b;
    if (scanf("%c%c%c%c%c%c",&buffer[0],&buffer[1],&buffer[2],&buffer[3],&buffer[4],&buffer[5]) != 1)
    {
        a = buffer[0]  + buffer[1]  + buffer[2] + buffer[3] + buffer[4] ;
        b = 0;
        b =  (( ~a | 0x80) - 0x80 ) ;
        a = buffer[5];
        if ( a == b )
        {
            frame[0] =  buffer[0] + (( buffer[4] & 0x01 ) * 0x80 ) ;
            frame[1] =  buffer[1] + (( buffer[4] >> 1 & 0x01 ) * 0x80 ) ;
            frame[2] =  buffer[2] + (( buffer[4] >> 2 & 0x01 ) * 0x80 ) ;
            frame[3] =  buffer[3] + (( buffer[4] >> 3 & 0x01 ) * 0x80 ) ;
        } else {
            frame[0] = 0;
            frame[1] = 0;
            frame[2] = 0;
            frame[3] = 0;
        }
    }
    return a - b;
}

int main(int argc, char* argv[])
{
    char  buffer[2];
    unsigned char a;
    char* arg_dup;
    int framecount,c=0,decodecount=0,decodedcount=0;
    FILE * pFile;
    while (( (decodedcount < decodecount) | (decodecount==0 ) ) && ( fgets(buffer, 2, stdin) != NULL))
    {
        a = buffer[0];
        if ( a ==  0xAA) {
            framecount  =  decodeheader();
            if (framecount !=0 )
            {
                for ( int x = 0; x < framecount ; x++ )
                {
                    c = c + decodeframe(x);
                    allframes[4*x] = frame[0];
                    allframes[(4*x)+1] = frame[1];
                    allframes[(4*x)+2] = frame[2];
                    allframes[(4*x)+3] = frame[3];
                }
                // if all crcs are ok
                decodedcount++;
                if (c == 0) {
                    string filen = "stdout";
                    for (int i = 1; i < argc; i++)
                    {
                        string sw = argv[i];
                        if (sw == "-f") {
                            i++;
                            filen = argv[i];
                        } else if (sw == "-c") {
                            i++;
                            decodecount = atoi(argv[i]);
                        } else {
                            arg_dup = strdup(argv[i]);
                            giveresults(arg_dup);
                            free(arg_dup);
                        }
                    }
                    if (filen == "stdout")
                    {
                        fprintf(stdout,"%s\n",presults.c_str());
                    } else {
                        pFile = fopen (filen.c_str(),"w");
                        fprintf (pFile,"%s\n",presults.c_str());
                        fclose (pFile);
                    }
                }
                presults = "";
            }
        }
    }
    return 0;
}

