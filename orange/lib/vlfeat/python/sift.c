/** @file     sift.c
 ** @author   Andrea Vedaldi, Python-Wrapping: Thomas V. Wiecki
 ** @brief    SIFT Python wrapper
 ** @internal
 **/

#include <Python.h>

#include <numpy/arrayobject.h>
#include <vl/mathop.h>
#include <vl/sift.h>
#include <math.h>
#include <assert.h>


static PyObject *sift(PyObject *self, PyObject *args, PyObject *kwargs);

// Make the sift function available to python
static PyMethodDef _siftMethods[] = {
    {"sift", (PyCFunction)sift, METH_VARARGS | METH_KEYWORDS },
    {NULL, NULL}     /* Sentinel - marks the end of this structure */
};

/* ==== Initialize the sift functions ====================== */
void init_sift()  {
    (void) Py_InitModule("_sift", _siftMethods);
    import_array();  // Must be present for NumPy.  Called first after above line.
}

/* ==== Create 1D Carray from PyArray ======================
   Assumes PyArray is contiguous in memory.             */
double *pyvector_to_Carrayptrs(PyArrayObject *arrayin)  {
    int n;

    n=arrayin->dimensions[0];
    return (double *) arrayin->data;  /* pointer to arrayin data as double */
}

/** @brief Transpose desriptor
 ** @internal
 **
 ** @param dst destination buffer.
 ** @param src source buffer.
 **
 ** The function writes to @a dst the transpose of the SIFT descriptor
 ** @a src. The tranpsose is defined as the descriptor that one
 ** obtains from computing the normal descriptor on the transposed
 ** image.
 **/
    static VL_INLINE void
transpose_descriptor (vl_sift_pix* dst, vl_sift_pix* src) 
{
    int BO = 8 ;
    int BP = 4 ;
    int i, j, t ;

    for (j = 0 ; j < BP ; ++j) {
        int jp = BP - 1 - j ;
        for (i = 0 ; i < BP ; ++i) {
            int o  = BO * i + BP*BO * j  ;
            int op = BO * i + BP*BO * jp ;      
            dst [op] = src[o] ;      
            for (t = 1 ; t < BO ; ++t) 
                dst [BO - t + op] = src [t + o] ;
        }
    }
}

/* ----------------------------------------------------------------- */
/** @brief Keypoint ordering
 ** @internal
 **/
int
korder (void const* a, void const* b) {
    double x = ((double*) a) [2] - ((double*) b) [2] ;
    if (x < 0) return -1 ;
    if (x > 0) return +1 ;
    return 0 ;
}

static PyObject *sift(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *input, *input_frames = NULL;
    PyArrayObject *matin, *out_descr, *out_frames; 
    /* Input arguments */
    static char *kwlist[] = {"input", "Octave", "Levels", "FirstOctave", "Frames", 
        "PeakThresh", "EdgeThresh", "Orientations", "Verbose", NULL};

    enum {IN_I=0,IN_END} ;
    enum {OUT_FRAMES=0, OUT_DESCRIPTORS} ;

    int                verbose = 0 ;
    int nout = 2;   
    vl_sift_pix const *data ;
    int                M, N ;

    int                O     =  -1 ;
    int                S     =   3 ;
    int                o_min =   0 ; 

    double             edge_tresh = -1 ;
    double             peak_tresh = -1 ;

    PyArrayObject     *ikeys_array = NULL ;
    double            *ikeys = 0 ;
    int                nikeys = -1 ;
    vl_bool            force_orientations = 0 ;

    /* Parse Python tuples into their appropriate variables */
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|iiiddOii", kwlist, &input, &O, &S, &o_min, &input_frames, 
                &peak_tresh, &edge_tresh, &force_orientations, &verbose))  return NULL;

    matin = (PyArrayObject *) PyArray_ContiguousFromObject(input, PyArray_FLOAT, 2, 2);
    if (matin == NULL)
        return NULL;


    if (NULL == matin)  return NULL;


    /** -----------------------------------------------------------------
     **                                               Check the arguments
     ** -------------------------------------------------------------- */

    if (matin->nd != 2) {
        printf("I must be a 2d matrix\n") ;
        return NULL;
    }

    // Pointer to the data array in matin
    data = (vl_sift_pix *) pyvector_to_Carrayptrs(matin);
    M = matin->dimensions[0];
    N = matin->dimensions[1];

    if (input_frames != NULL) {
        ikeys_array = (PyArrayObject *) PyArray_ContiguousFromObject(input_frames, PyArray_FLOAT, 2, 2);
        if (ikeys_array->dimensions[0] != 4) {
            printf("'Frames' must be a 4 x N matrix.x\n");
            return NULL;
        }
        nikeys = ikeys_array->dimensions[1];
        ikeys = (double *) ikeys_array->data;
        qsort (ikeys, nikeys, 4 * sizeof(double), korder);
    }

    /* -----------------------------------------------------------------
     *                                                     Run algorithm
     * -------------------------------------------------------------- */
    {
        VlSiftFilt        *filt ;    
        vl_bool            first ;
        double            *frames = 0 ;
        short             *descr  = 0 ;
        int                nframes = 0, reserved = 0, i,j,q ;

        /* create a filter to process the image */
        filt = vl_sift_new (M, N, O, S, o_min) ;

        if (peak_tresh >= 0) vl_sift_set_peak_tresh (filt, peak_tresh) ;
        if (edge_tresh >= 0) vl_sift_set_edge_tresh (filt, edge_tresh) ;

        if (verbose) {    
            printf("siftmx: filter settings:\n") ;
            printf("siftmx:   octaves      (O)     = %d\n", 
                    vl_sift_get_octave_num   (filt)) ;
            printf("siftmx:   levels       (S)     = %d\n",
                    vl_sift_get_level_num    (filt)) ;
            printf("siftmx:   first octave (o_min) = %d\n", 
                    vl_sift_get_octave_first (filt)) ;
            printf("siftmx:   edge tresh           = %g\n",
                    vl_sift_get_edge_tresh   (filt)) ;
            printf("siftmx:   peak tresh           = %g\n",
                    vl_sift_get_peak_tresh   (filt)) ;
            /*      printf((nikeys >= 0) ? 
                    "siftmx: will source frames? yes (%d)\n" :
                    "siftmx: will source frames? no\n", nikeys) ;
                    printf("siftmx: will force orientations? %s\n",
                    force_orientations ? "yes" : "no") ;      
                    */
        }


        /* ...............................................................
         *                                             process each octave
         * ............................................................ */
        i     = 0 ;
        first = 1 ;
        while (1) {
            int                   err ;
            VlSiftKeypoint const *keys  = 0 ;
            int                   nkeys = 0 ;

            if (verbose) {
                printf ("siftmx: processing octave %d\n",
                        vl_sift_get_octave_index (filt)) ;
            }

            /* calculate the GSS for the next octave .................... */
            if (first) {
                err   = vl_sift_process_first_octave (filt, data) ;
                first = 0 ;
            } else {
                err   = vl_sift_process_next_octave  (filt) ;
            }        

            if (err) break ;

            if (verbose > 1) {
                printf("siftmx: GSS octave %d computed\n",
                        vl_sift_get_octave_index (filt));
            }

            /* run detector ............................................. */
            if (nikeys < 0) {
                vl_sift_detect (filt) ;

                keys  = vl_sift_get_keypoints     (filt) ;
                nkeys = vl_sift_get_keypoints_num (filt) ;
                i     = 0 ;

                if (verbose > 1) {
                    printf ("siftmx: detected %d (unoriented) keypoints\n", nkeys) ;
                }
            } else {
                nkeys = nikeys ;
            }

            /* for each keypoint ........................................ */
            for (; i < nkeys ; ++i) {
                double                angles [4] ;
                int                   nangles ;
                VlSiftKeypoint        ik ;
                VlSiftKeypoint const *k ;

                /* obtain keypoint orientations ........................... */
                if (nikeys >= 0) {
                    vl_sift_keypoint_init (filt, &ik, 
                            ikeys [4 * i + 1] - 1,
                            ikeys [4 * i + 0] - 1,
                            ikeys [4 * i + 2]) ;

                    if (ik.o != vl_sift_get_octave_index (filt)) {
                        break ;
                    }

                    k = &ik ;

                    /* optionally compute orientations too */
                    if (force_orientations) {
                        nangles = vl_sift_calc_keypoint_orientations 
                            (filt, angles, k) ;            
                    } else {
                        angles [0] = VL_PI / 2 - ikeys [4 * i + 3] ;
                        nangles    = 1 ;
                    }
                } else {
                    k = keys + i ;
                    nangles = vl_sift_calc_keypoint_orientations 
                        (filt, angles, k) ;
                }

                /* for each orientation ................................... */
                for (q = 0 ; q < nangles ; ++q) {
                    vl_sift_pix  buf [128] ;
                    vl_sift_pix rbuf [128] ;

                    /* compute descriptor (if necessary) */
                    if (nout > 1) {
                        vl_sift_calc_keypoint_descriptor 
                            (filt, buf, k, angles [q]) ;
                        transpose_descriptor (rbuf, buf) ;
                    }

                    /* make enough room for all these keypoints */
                    if (reserved < nframes + 1) {
                        reserved += 2 * nkeys ;
                        frames = malloc (4 * sizeof(double) * reserved) ;
                        if (nout > 1) {
                            descr  = malloc (128 * sizeof(short) * reserved) ;
                        }
                    }

                    frames [4 * nframes + 0] = k -> y + 1 ;
                    frames [4 * nframes + 1] = k -> x + 1 ;
                    frames [4 * nframes + 2] = k -> sigma ;
                    frames [4 * nframes + 3] = VL_PI / 2 - angles [q] ;

                    if (nout > 1) {
                        for (j = 0 ; j < 128 ; ++j) {
                            descr [128 * nframes + j] = (short) (512.0 * rbuf [j]) ;
                        }
                    }

                    ++ nframes ;
                } /* next orientation */
            } /* next keypoint */
        } /* next octave */

        if (verbose) {
            printf ("siftmx: found %d keypoints\n", nframes) ;
        }

        /* save back */
        {
            int dims [2] ;

            /* set to our stuff */
            dims [0] = 4 ;
            dims [1] = nframes ;
            // We are allocating new memory here because its the only way to make
            // sure that it will get free()ed when there are no more references
            out_frames = (PyArrayObject*) PyArray_FromDims(2, dims, PyArray_DOUBLE);
            memcpy((double*) out_frames->data, frames, 4 * nframes * sizeof(double));
            dims [0] = 128 ;
            dims [1] = nframes ;
            out_descr = (PyArrayObject*) PyArray_FromDims(2, dims, PyArray_SHORT);
            memcpy((short *) out_descr->data, descr, 128 * nframes * sizeof(short));
        }

        /* cleanup */
        vl_sift_delete (filt) ;
        free(frames);
        free(descr);
        Py_DECREF(matin);

    }
    // Return both arrays in a tuple
    return Py_BuildValue("(OO)",PyArray_Return(out_frames), PyArray_Return(out_descr));
}
