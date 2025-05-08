import numpy as np
import operator
import os 
import time
import tflite_runtime.interpreter as tflite

userDir = os.path.expanduser('~')
labels_file = "labels"

class Model():

    def __init__(self, model, threads=2):
        self.model_path = userDir + "/" + model + ".tflite"

        self.myinterpreter = tflite.Interpreter(model_path=self.model_path, num_threads=threads)
        self.myinterpreter.allocate_tensors()
        input_details = self.myinterpreter.get_input_details()
        output_details = self.myinterpreter.get_output_details()
        self.INPUT_LAYER_INDEX = input_details[0]['index']
        self.OUTPUT_LAYER_INDEX = output_details[0]['index']

         # Load labels
        self.CLASSES = []
        labelspath = userDir +"/" + labels_file + '.txt'
        with open(labelspath, 'r') as lfile:
            for line in lfile.readlines():
                self.CLASSES.append(line.replace('\n', '').split("_")[1])
        self.last_seen={}
        print('Model loaded')

    def custom_sigmoid(self, x, sensitivity=1.0):
        return 1 / (1.0 + np.exp(-sensitivity * x))

    def predict(self, sample, sensitivity=1.0):
        self.myinterpreter.set_tensor(self.INPUT_LAYER_INDEX, np.array(sample, dtype='float32'))
        self.myinterpreter.invoke()
        prediction = self.myinterpreter.get_tensor(self.OUTPUT_LAYER_INDEX)[0]
        p_sigmoid = self.custom_sigmoid(prediction, sensitivity)
        p_labels = dict(zip(self.CLASSES, p_sigmoid))
        return sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)

    def predict_threshold(self, sample, sensitivity=1.0, min_p=0.25, timestamp=0):
        p_labels = self.predict(sample, sensitivity)
        top_labels = [p for p in p_labels if p[1] >= min_p]
        new_labels = [p for p in top_labels if p[0] not in self.last_seen or timestamp - self.last_seen[p[0]] > 5]
        for label, _ in new_labels:
            self.last_seen[label] = timestamp
        return new_labels