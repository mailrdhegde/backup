#include <opencv2/opencv.hpp>
#include <opencv2/video/background_segm.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <vector>
#include <opencv2/highgui/highgui.hpp>
using namespace cv;
using namespace std;
//CvCapture * cap1;
int tamper(Mat &frame);
Mat fore;
 Mat frame;
  Mat back;
cv::Ptr<cv::BackgroundSubtractorMOG2> bg = cv::createBackgroundSubtractorMOG2();

 
	 vector < vector < Point > >contours;  
int main ()
{
 
  bg->setNMixtures(10);

  VideoCapture cap1(0);/*to capture from camera*/

 // int i=0;
	 for(;;)
	 {
	 
   //std::cout << "Hello World!";
	cap1 >> frame;
	 // std::cout << "Hello Worldss!";
	    
	  int passed = tamper(frame);
	 
	  }
	  }
int tamper (cv::Mat &frame)
	  {


	  bg->apply(frame, fore);
    	bg->getBackgroundImage (back);

  //bg->setNMixtures(10);

	  // Mat frame;
  
  //Mat fore;
	
  //bg->apply(img,mask);
 // BackgroundSubtractorMOG2 bg;//works on GMM
 // bg.set ("nmixtures", 10);
  
  namedWindow ("Frame");
  int i=0;
    //bg->operator()(frame, fore);
    	//bg->apply(frame, fore);
    	//bg->getBackgroundImage (back);
    	erode (fore, fore, cv::Mat ());
    	erode (fore, fore, cv::Mat ());
    	dilate (fore, fore, cv::Mat ());
	dilate (fore, fore, cv::Mat ());
	dilate (fore, fore, cv::Mat ());
	findContours (fore, contours, CV_RETR_EXTERNAL,CV_CHAIN_APPROX_NONE);
    	drawContours (frame, contours, -1, Scalar (255, 255, 255), 1);
	//cout<<"contours size = "<<contours.size()<< endl; 
	Scalar color = Scalar(200,200,200);
	int a=0;
	vector<Rect> boundRect( contours.size() );
    for( int i = 0; i < contours.size(); i++ )
	  {
	    //std::cout << "Hello World24!";
		   boundRect[i] = boundingRect( contours[i] );
	  }
	for( i = 0; i< contours.size(); i++ )
     {
		if(boundRect[i].width>=40 || boundRect[i].height>=40)//eliminates small boxes
			{
				a=a+(boundRect[i].height)*(boundRect[i].width);
			 }
		//  cout<<"Net contour area is "<<a<<"\n";
	    if(a>=int(frame.rows)*int(frame.cols)/2)//change denominator as per convenience
			{
				putText(frame,"Tampering",Point(5,30),FONT_HERSHEY_SIMPLEX,1,Scalar(0,255,255),2);
				//PlaySound("/home/preeti/Downloads/YOLO-Object-Detection-master/1.mp3", NULL, SND_ASYNC);
				cout<<"\a";
			//	  std::cout << "Hello World20!";
			}
	   }
	   contours.clear();
   imshow ("Frame", frame);
   cvWaitKey(10);
   frame.release();
   fore.release();
   back.release();
   boundRect.clear();
    //std::cout << "Hello Worlddone!";

  return 1;
}
