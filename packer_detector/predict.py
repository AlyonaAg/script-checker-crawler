from tensorflow.keras.models import load_model

class ObfuscateDetected:
    def __init__(self, model_data='packer_detector/model_data.model'):
        self.model_data = load_model(model_data)

    def predict(self, x):
        print(x, [x])
        predict_obf = self.model_data.predict([x])
        print(predict_obf)

        print('Result: ', 1 if predict_obf > 0.5 else 0)

        return 1 if predict_obf > 0.3 else 0