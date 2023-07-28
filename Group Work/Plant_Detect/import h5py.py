import h5py
# from keras.models import load_model

# model = load_model('keras_model.h5')

filename = "keras_model.h5"
h5 = h5py.File(filename, 'r')
Plant = h5['Plant']
No_plant = h5['No plant']
# print(list(h5.keys()))
h5.close()