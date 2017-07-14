#include <Python.h>
#include <numpy/arrayobject.h>


void swapPtr(uint32_t* x)
{
    char* px = (char*)x;
    for (int i=0; i<sizeof(uint32_t)/2; i++)
    {
        char temp = px[i];
        px[i] = px[sizeof(uint32_t)-1-i];
        px[sizeof(uint32_t)-1-i] = temp;
    }
}



void unpack_values(const char* data, int b, int total_nb_values, unsigned int *out) {

    int cs = 0;          // current size
    uint32_t cb = 0;     // current bits
    int i = 0;           // index in byte array
    int nb_values = 0;   // Number of values returned
    uint32_t value;

    while (nb_values < total_nb_values) {
        if (cs < b) {
            // Getting another byte
            cb = (cb << 8) ^ (data[i] & 0xFF);
            cs += 8;
            i += 1;
        }
        else {
            cs -= b;
            value = (cb >> cs) << (32 - b);
            cb ^= value << cs;
            swapPtr(&value);
            out[nb_values] = value;
            nb_values += 1;
        }
    }


}


static PyObject *
test_function(PyObject *self, PyObject *args)
{

    // Read the arguments
    const char *data;
    int b, total_nb_values;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#ii", &data, &len, &b, &total_nb_values)) {
        return NULL;
    }

    // Create the numpy array.
    npy_intp dims[] = { total_nb_values };
    PyObject* o = PyArray_SimpleNew(1, &dims, PyArray_UINT32);

    // Get a pointer to the data.
    unsigned int *out_data = PyArray_DATA((PyArrayObject *) o);

    // Fill.
    unpack_values(data, b, total_nb_values, out_data);

    return o;
}


static PyMethodDef TestMethods[] = {
    {"test_function",  test_function, METH_VARARGS,
     "Test function."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef testmodule = {
   PyModuleDef_HEAD_INIT,
   "c_test",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   TestMethods
};


PyMODINIT_FUNC
PyInit_c_test(void)
{
    import_array();
    return PyModule_Create(&testmodule);
}
