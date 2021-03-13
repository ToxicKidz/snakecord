#include "opus.h"
#include "Python.h"

#define SAMPLING_RATE 48000
#define CHANNELS 2
#define FRAME_DURATION 0.02
#define SAMPLE_SIZE sizeof(short) * CHANNELS
#define SAMPLES_PER_FRAME (int)(SAMPLING_RATE * FRAME_DURATION)
#define FRAME_SIZE SAMPLE_SIZE * SAMPLES_PER_FRAME
#define MAX_FRAME_SIZE SAMPLES_PER_FRAME * 6

#define APPLICATION OPUS_APPLICATION_VOIP

#define RETURN_IF_NULL(value) if ((value) == NULL) { \
                                    return NULL; \
                                }


typedef struct OpusEncoderObject {
    PyObject_HEAD
    OpusEncoder* encoder;
} OpusEncoderObject;


typedef struct OpusDecoderObject {
    PyObject_HEAD
    opus_int16* buffer;
    OpusDecoder* decoder;
} OpusDecoderObject;


static PyObject* OpusEncoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds);
static void OpusEncoder_Dealloc(OpusEncoderObject* self);
static PyObject* OpusEncoder_Encode(PyObject* self, PyObject* args);


static PyObject* OpusDecoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds);
static void OpusDecoder_Dealloc(OpusDecoderObject* self);
static PyObject* OpusDecoder_Decode(PyObject* self, PyObject* args);
static PyObject* OpusDecoder_GetLastPacketDuration(PyObject *self, PyObject *args);


static PyObject* OpusPacket_GetNBFrames(PyObject* self, PyObject* args);
static PyObject* OpusPacket_GetNBChannels(PyObject* self, PyObject* args);
static PyObject* OpusPacket_GetSamplesPerFrame(PyObject* self, PyObject* args);


static PyMethodDef OpusEncoderMethods[] = {
    {"encode", OpusEncoder_Encode, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


static PyMethodDef OpusDecoderMethods[] = {
    {"decode", OpusDecoder_Decode, METH_VARARGS, NULL},
    {"get_last_packet_duration", OpusDecoder_GetLastPacketDuration, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


static PyTypeObject OpusEncoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "opus.OpusEncoder",
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(OpusEncoderObject),
    .tp_new = OpusEncoder_New,
    .tp_dealloc = (destructor)OpusEncoder_Dealloc,
    .tp_methods = OpusEncoderMethods
};


static PyTypeObject OpusDecoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "opus.OpusDecoder",
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(OpusDecoderObject),
    .tp_new = OpusDecoder_New,
    .tp_dealloc = (destructor)OpusDecoder_Dealloc,
    .tp_methods = OpusDecoderMethods
};


static PyObject* OpusSetException(int error, PyObject* ret)
{
    switch (error) {
    case OPUS_BAD_ARG:
        PyErr_SetString(PyExc_ValueError, "Opus received a bad argument");
    case OPUS_BUFFER_TOO_SMALL:
        PyErr_SetString(PyExc_ValueError, "Opus received a buffer that is too small");
    case OPUS_INTERNAL_ERROR:
        PyErr_SetString(PyExc_RuntimeError, "Opus ran into an internal error");
    case OPUS_INVALID_PACKET:
        PyErr_SetString(PyExc_ValueError, "Opus received an invalid packet");
    case OPUS_UNIMPLEMENTED:
        PyErr_SetString(PyExc_NotImplementedError, "Opus was asked to do something that is not implemented");
    case OPUS_INVALID_STATE:
        PyErr_SetString(PyExc_RuntimeError, "Opus was asked to do something with an invalid encoder/decoder");
    case OPUS_ALLOC_FAIL:
        PyErr_SetString(PyExc_MemoryError, "Opus failed to allocate memory");
    }
    return ret;
}


PyObject* OpusEncoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    int error;
    OpusEncoderObject* opus_encoder;
    opus_encoder = PyObject_New(OpusEncoderObject, &OpusEncoderType);
    opus_encoder->encoder = opus_encoder_create(SAMPLING_RATE, CHANNELS, APPLICATION, &error);
    return OpusSetException(error, (PyObject*)opus_encoder);
}


PyObject* OpusEncoder_Encode(PyObject* self, PyObject* args)
{
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)self;

    PyObject* data;
    RETURN_IF_NULL(data = PyTuple_GetItem(args, 0));
    int size = PyBytes_Size(data);
    const opus_int16* pcm = (const opus_int16*)PyBytes_AsString(data);

    PyObject* frame_sizeo;
    RETURN_IF_NULL(frame_sizeo = PyTuple_GetItem(args, 1));
    int frame_size = PyLong_AsLong(frame_sizeo);

    unsigned char* buffer = PyMem_Calloc(1, size);
    if (buffer == NULL) {
        PyErr_NoMemory();
        return NULL;
    }

    int val;

    Py_BEGIN_ALLOW_THREADS
    val = opus_encode(opus_encoder->encoder, pcm, frame_size, buffer, size);
    Py_END_ALLOW_THREADS

    if (val < 0) {
        PyMem_Free(buffer);
        return OpusSetException(val, NULL);
    }

    PyObject* encoded = PyBytes_FromStringAndSize((const char*)buffer, val);
    PyMem_Free(buffer);

    return encoded;
}


void OpusEncoder_Dealloc(OpusEncoderObject* self)
{
    opus_encoder_destroy(self->encoder);
    PyTypeObject* tp = Py_TYPE(self);
    tp->tp_free(self);
}


PyObject* OpusDecoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    int err;
    OpusDecoderObject* decoder;
    decoder = PyObject_New(OpusDecoderObject, &OpusDecoderType);
    decoder->buffer = PyMem_Calloc(1, MAX_FRAME_SIZE * SAMPLE_SIZE);
    if (decoder->buffer == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    decoder->decoder = opus_decoder_create(SAMPLING_RATE, CHANNELS, &err);
    return OpusSetException(err, (PyObject*)decoder);
}


PyObject* OpusDecoder_Decode(PyObject* self, PyObject* args)
{
    OpusDecoderObject* opus_decoder = (OpusDecoderObject*)self;
    
    PyObject* bytes;
    RETURN_IF_NULL(bytes = PyTuple_GetItem(args, 0));
    int size = PyBytes_Size(bytes);
    const unsigned char* data = (const unsigned char*)PyBytes_AsString(bytes);

    PyObject* frame_sizeo;
    RETURN_IF_NULL(frame_sizeo = PyTuple_GetItem(args, 1));
    int frame_size = PyLong_AsLong(frame_sizeo);

    PyObject* channelso;
    RETURN_IF_NULL(channelso = PyTuple_GetItem(args, 2));
    int channels = PyLong_AsLong(channelso);

    PyObject* decode_feco;
    RETURN_IF_NULL(decode_feco = PyTuple_GetItem(args, 3));
    int decode_fec = PyObject_IsTrue(decode_feco);

    int val;

    Py_BEGIN_ALLOW_THREADS
    val = opus_decode(opus_decoder->decoder, data, size, opus_decoder->buffer, frame_size, decode_fec);
    Py_END_ALLOW_THREADS

    if (val < 0) {
        return OpusSetException(val, NULL);
    }

    PyObject* decoded = PyBytes_FromStringAndSize((const char*)opus_decoder->buffer, val * channels * 2);

    return decoded;
}


PyObject* OpusDecoder_GetLastPacketDuration(PyObject *self, PyObject *args)
{
    int duration;
    OpusDecoderObject* opus_decoder = (OpusDecoderObject*)self;
    opus_decoder_ctl(opus_decoder->decoder, OPUS_GET_LAST_PACKET_DURATION(&duration));
    return PyLong_FromLong(duration);
}


void OpusDecoder_Dealloc(OpusDecoderObject* self)
{
    PyMem_Free(self->buffer);
    opus_decoder_destroy(self->decoder);
    PyTypeObject* tp = Py_TYPE(self);
    tp->tp_free(self);
}


PyObject* OpusPacket_GetNBFrames(PyObject* self, PyObject* args)
{
    PyObject* bytes;
    RETURN_IF_NULL(bytes = PyTuple_GetItem(args, 0));
    int size = PyBytes_Size(bytes);
    const unsigned char* data = (const unsigned char*)PyBytes_AsString(bytes);

    int val = opus_packet_get_nb_frames(data, size);
    return PyLong_FromLong(val);
}


PyObject* OpusPacket_GetNBChannels(PyObject* self, PyObject* args)
{
    PyObject* bytes;
    RETURN_IF_NULL(bytes = PyTuple_GetItem(args, 0));
    const unsigned char* data = (const unsigned char*)PyBytes_AsString(bytes);

    int val = opus_packet_get_nb_channels(data);
    return PyLong_FromLong(val);
}


PyObject* OpusPacket_GetSamplesPerFrame(PyObject* self, PyObject* args)
{
    PyObject* bytes;
    RETURN_IF_NULL(bytes = PyTuple_GetItem(args, 0));
    const unsigned char* data = (const unsigned char*)PyBytes_AsString(bytes);

    int val = opus_packet_get_samples_per_frame(data, SAMPLING_RATE);
    return PyLong_FromLong(val);
}


static PyMethodDef OpusMethods[] = {
    {"get_nb_frames", OpusPacket_GetNBFrames, METH_VARARGS, NULL},
    {"get_nb_channels", OpusPacket_GetNBChannels, METH_VARARGS, NULL},
    {"get_samples_per_frame", OpusPacket_GetSamplesPerFrame, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef opusmodule = {
    PyModuleDef_HEAD_INIT,
    "opus",
    NULL,
    -1,
    OpusMethods
};


PyMODINIT_FUNC PyInit_opus(void)
{
    PyObject* module = PyModule_Create(&opusmodule);
    PyTypeObject* encoder_type = &OpusEncoderType;
    PyTypeObject* decoder_type = &OpusDecoderType;

    Py_INCREF(encoder_type);
    Py_INCREF(decoder_type);

    if (PyType_Ready(encoder_type) < 0) {
        Py_DECREF(encoder_type);
        return NULL;
    }

    if (PyType_Ready(decoder_type) < 0) {
        Py_DECREF(decoder_type);
        return NULL;
    }

    PyModule_AddObject(module, "OpusEncoder", (PyObject*)encoder_type);
    PyModule_AddObject(module, "OpusDecoder", (PyObject*)decoder_type);
    PyModule_AddIntConstant(module, "SAMPLING_RATE", SAMPLING_RATE);
    PyModule_AddIntConstant(module, "CHANNELS", CHANNELS);
    PyModule_AddObject(module, "FRAME_DURATION", PyFloat_FromDouble(FRAME_DURATION));
    PyModule_AddIntConstant(module, "SAMPLE_SIZE", SAMPLE_SIZE);
    PyModule_AddIntConstant(module, "SAMPLES_PER_FRAME", SAMPLES_PER_FRAME);
    PyModule_AddIntConstant(module, "FRAME_SIZE", FRAME_SIZE);
    PyModule_AddIntConstant(module, "MAX_FRAME_SIZE", MAX_FRAME_SIZE);

    return module;
}
