#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double func(double x)
{
    return exp(-x*x/2);
    // return x * x;
}

int main(int argc, char const *argv[])
{
    // double snr = 4.0;
    if(argc != 2){
        printf("Use: sekibun snr\n");
        exit(1);
    }
    double snr = atof(argv[1]);
    // printf("%f",snr);
    double a = sqrt(2.0)*sqrt(snr);
    // int a = 0;
    double b = 10.0;
    int kaisu = 100000;
    double delta = (b - a) / kaisu;
    int i;
    double sum = 0;
    for (i = 0; i < kaisu; i++)
    {
        sum += func(delta * i + a) * delta;
        // printf("%f\n",func(i*delta));
    }
    printf("result: %f\n", ((double)1/sqrt(2*3.14151925358979))*sum);
    return 0;
}
