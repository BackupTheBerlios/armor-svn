/*
 *
 *
 *
 *
 */

#include<python2.5/Python.h>

extern "C" {
    

class PyThread {
    protected: 
        PyThread(); //The class can only be inherited, never instantiated.

    public:
        virtual int setParameters(PyObject *parameters); //Set the parameters, you can not use PyObject elements
        //once the GIL is released
        virtual PyObject* getReturns();
        PyObject* setReturnCallback(PyObject *callBack);
        PyObject* setErrorCallback(PyObject *callBack);
        virtual int callFunc();      //Call the actual function which should run in its own thread
        int finished(PyObject *returnList);
    private:
        PyObject *returnCallback;
        PyObject *errorCallback;
};

PyThread::PyThread() {
    returnCallback = NULL;
    errorCallback = NULL;
}

int PyThread::finished(PyObject *returnValues) {
    PyObject *result;

    result = PyEval_CallObject(returnCallback, returnValues);
    Py_DECREF(returnValues);

    if (result == NULL)
        Py_XDECREF(result);
        result = PyEval_CallObject(errorCallback, Py_None); 
        return -1; /* Pass error back */
    Py_DECREF(result);
    return 0;
}


PyObject* PyThread::setReturnCallback(PyObject *callBack) {
    if (!PyCallable_Check(callBack)) {
        PyErr_SetString(PyExc_TypeError, "parameter must be callable");
        return NULL;
    }

    Py_XINCREF(callBack);
    Py_XDECREF(returnCallback);  /* Dispose of previous callback */
    returnCallback = callBack;
    return(Py_None);
}

PyObject* PyThread::setErrorCallback(PyObject *callBack) {
    if (!PyCallable_Check(callBack)) {
        PyErr_SetString(PyExc_TypeError, "parameter must be callable");
        return NULL;
    }

    Py_XINCREF(callBack);
    Py_XDECREF(returnCallback);  /* Dispose of previous callback */
    returnCallback = callBack;
    return(Py_None);
}

int PyThread::setParameters(PyObject *parameters) {} //To be overwritten
int PyThread::callFunc() {} //To be overwritten
PyObject* PyThread::getReturns() {} //To be overwritten


PyThread* createPyThreadObject();

static PyObject* start(PyObject *self, PyObject *args) {
    static PyObject *returnCallback;
    static PyObject *errorCallback;
    static PyObject *returnValues;
    PyThread *pythread;
    pythread = createPyThreadObject();

    if (!PyArg_ParseTuple(args, "OO", &returnCallback, &errorCallback))
        return NULL;
        
    pythread->setReturnCallback(returnCallback);
    pythread->setErrorCallback(errorCallback);
    pythread->setParameters(args);
    
//    Py_BEGIN_ALLOW_THREADS
    pythread->callFunc();
//    Py_END_ALLOW_THREADS

    printf("Reached start!\n");
    returnValues = pythread->getReturns();
    pythread->finished(returnValues);
    return(Py_None);
}

static PyMethodDef PyThreadMethods[] = {
    {"start", start , METH_VARARGS | METH_KEYWORDS,
        "Do the computations without holding the GIL."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initPyThread(void)
{
    (void) Py_InitModule("PyThread", PyThreadMethods);
}

}
