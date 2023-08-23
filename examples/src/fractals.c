#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>

#define XSIZE    3200
#define YSIZE    3200
#define MAXITER  1500
#define PI       3.141592654


void color(int red, int green, int blue, FILE *ofp){
  fputc((char)red, ofp);
  fputc((char)green, ofp);
  fputc((char)blue, ofp);
}

int main(int argc, char *argv[]) {

  double xmin = -1.5, xmax = 1.5, ymin = -1.2, ymax = 1.2;
  double deltax, deltay, x, y, x0, y0;
  double p = -0.5101, q =  0.5101, radius, zr, zi;
  int xsize=XSIZE;
  int ysize=YSIZE;
  int maxiter=MAXITER;
  int c;
  char default_filename[] = "fractal.ppm";
  char *filename;
  char filenameSet = 0;
  extern char *optarg;
  extern int optopt;

  while ((c = getopt(argc, argv, "q:d:m:o:")) != -1) {
    switch(c) {
      case 'q':
        q = strtod( optarg, NULL );
        p = q * -1.0;
        break;
      case 'd':
        xsize = atoi(optarg);
        ysize = xsize;
        break;
      case 'm':
        maxiter = atoi(optarg);
        break;
      case 'o':
        filename = optarg;
        filenameSet = 1;
        break;
      case '?':
        fprintf(stderr, "Unrecognized option: -%c\n", optopt);
    }
  }

  if ( 0 == filenameSet ) {
    filename = default_filename;
  }

  int color_index, xpix, ypix;
  int colorred, colorgreen, colorblue;
  FILE *ofp;

  ofp = fopen(filename, "w");
  fprintf(ofp,"P6\n# Y2K Compliant / Julia Set\n");
  fprintf(ofp,"%d %d\n255\n",xsize,ysize);
  deltax = (xmax - xmin)/(xsize-1);
  deltay = (ymax - ymin)/(ysize-1);
  for (xpix = 0; xpix < xsize; xpix++){
    x0 = xmin + (double)xpix*deltax;
    for (ypix = 0; ypix < ysize; ypix++){
      y0 = ymin + (double)ypix*deltay;
      //colorred = (int)(255*sin( fabs(y0) / sqrt(y0*y0 + x0*x0) ));
      //colorgreen = (int)(255*cos( fabs(x0) / sqrt(y0*y0 + x0*x0) ));
      //colorblue = 0;
      x = x0; y = y0;
      color_index = 0;
      do{
        zr = x*x-y*y + p;
        zi = 2.0*x*y + q;
        radius = zr*zr + zi*zi;
        //colorred = (int)(255*sin( fabs(ypix) / radius ));
        //colorgreen = (int)(255*cos( fabs(xpix) / radius ));
        //colorblue = (int)(255*tan( fabs(xpix-ypix) / radius ));
        colorred = 0;
        colorgreen = (int)(x*ypix) % 255;
        colorblue = (int)(y*xpix) % 255;
        color_index++;
        if (radius >= maxiter) color(255, 255, 255, ofp);
        //if (color_index == maxiter) color(0, (int)(x*ypix) % 255, (int)(y*xpix) % 255, ofp);
        if (color_index == maxiter) color( colorred, colorgreen, colorblue, ofp);
        x = zr; y = zi;
      } while (radius <= maxiter && color_index <= maxiter);
    }
  }
  fclose(ofp);
}
