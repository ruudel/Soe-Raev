//I have included only the integral parts of code. There are no compilation errors.

    int lowerH =80, upperH =100, lowerS =80, upperS =255, lowerV =80, upperV =255;

    CvScalar output_min =cvScalar(lowerH, lowerS, lowerV, 0); //Color Track
    CvScalar output_max =cvScalar(upperH, upperS, upperV, 0);

    CvScalar output_min2 =cvScalar(0, lowerS, lowerV, 0); //Color Track
    CvScalar output_max2 =cvScalar(180, upperS, upperV, 0);

    while(true){
        frame =cvQueryFrame(capture);

        cvCvtColor(frame, output, CV_BGR2HSV);
        cvInRangeS(output, output_min, output_max, output_mask);

        blobs =CBlobResult(output_mask, NULL, 0);
        blobs.Filter(blobs, B_EXCLUDE, CBlobGetArea(), B_LESS, 35);

        int num_blobs =blobs.GetNumBlobs();
        for(int i=0; i<num_blobs;++i){
            currentBlob = blobs.GetBlob( i );
            sortedBlobs.push_back(currentBlob);
        }

        if(num_blobs){
            sort(sortedBlobs.begin(), sortedBlobs.end(), local::sortBlobs);
            CvRect blobRect =sortedBlobs[0].GetBoundingBox();

            initX =blobRect.x;
            initY =blobRect.y;
            initWidth =blobRect.width;
            initHeight =blobRect.height;
            initFrame =cvCloneImage(frame);
        }

            int c=cvWaitKey(40);
        if((char)c ==27)break;
    }

    CvRect selection;
    selection.x = initX;
    selection.y = initY;
    selection.width = initWidth;
    selection.height = initHeight;

    CvHistogram *hist;
    int hist_bins = 30;
    float hist_range[] = {0, 180};
    float* range = hist_range;
    hist = cvCreateHist(1, &hist_bins, CV_HIST_ARRAY, &range, 1);

    cvCvtColor(initFrame, output, CV_BGR2HSV);
    cvInRangeS(output, output_min2, output_max2, output_mask);
    cvSplit(output, hue, 0, 0, 0);

    cvSetImageROI(hue, selection);
    cvSetImageROI(output_mask, selection);

    cvCalcHist(&hue, hist, 0, output_mask);
    float max_val = 0.f;
    cvGetMinMaxHistValue(hist, 0, &max_val, 0, 0 );
    cvConvertScale(hist->bins, hist->bins,
                 max_val ? 255.0/max_val : 0, 0);

    cvResetImageROI(hue);
    cvResetImageROI(output_mask);


    CvBox2D curr_box;
    CvRect prev_rect =selection;
    CvConnectedComp components;
    bool rectFlag =false;
    CvPoint Pt =cvPoint(0,0), prevPt =cvPoint(0,0);
    int clearCounter =0;
    while(true){
        frame =cvQueryFrame(capture);
        if(!frame)break;

        cvCvtColor(frame, output, CV_BGR2HSV);
        cvInRangeS(output, output_min2, output_max2, output_mask);
        cvSplit(output, hue, 0, 0, 0);

        cvCalcBackProject(&hue, prob, hist);
        cvAnd(prob, output_mask, prob, 0);

        cvCamShift(prob, prev_rect, cvTermCriteria(CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 20, 1), &components, &curr_box);

        prev_rect = components.rect;
        curr_box.angle = -curr_box.angle;

        cvEllipseBox(frame, curr_box, CV_RGB(255,0,0), 3, CV_AA, 0);

        int c=cvWaitKey(40);
        if((char)c ==27)break;
    }
