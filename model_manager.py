from edge_impulse_linux.image import ImageImpulseRunner
import cv2

class ModelManager: 
    def __init__(self, model_path):
        self.model_path = model_path
        self.runner = ImageImpulseRunner(self.model_path)
        self.labels = self.runner.init()['model_parameters']['labels']
        self.cropped = None
        self.i = 0

    def classifyImage(self, image):
        features, self.cropped = self.runner.get_features_from_image_auto_studio_setings(image) # Extrai as features da imagem
        res = self.runner.classify(features) # Classifica a imagem usando o modelo do Edge Impulse
        if "classification" in res["result"].keys():
            #print('Resultado (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
            #for label in self.labels:
            #    score = res['result']['classification'][label]
            #    print('%s: %.2f\t' % (label, score), end='')
            #print('', flush=True)
            return res['result']['classification']

        elif "bounding_boxes" in res["result"].keys():
            print('Encontrados %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
            for bb in res["result"]["bounding_boxes"]:
                print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                cropped = cv2.rectangle(cropped, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)

        if "visual_anomaly_grid" in res["result"].keys():
            print('Encontradas %d anomalias visuais (%d ms.)' % (len(res["result"]["visual_anomaly_grid"]), res['timing']['dsp'] + res['timing']['classification']))
            for grid_cell in res["result"]["visual_anomaly_grid"]:
                print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (grid_cell['label'], grid_cell['value'], grid_cell['x'], grid_cell['y'], grid_cell['width'], grid_cell['height']))
                cropped = cv2.rectangle(cropped, (grid_cell['x'], grid_cell['y']), (grid_cell['x'] + grid_cell['width'], grid_cell['y'] + grid_cell['height']), (255, 125, 0), 1)
            values = [grid_cell['value'] for grid_cell in res["result"]["visual_anomaly_grid"]]
            mean_value = sum(values) / len(values)
            max_value = max(values)
            print('Max value: %.2f' % max_value)
            print('Mean value: %.2f' % mean_value)
        
    def saveImage(self, image): 
        print("image: ", self.i)
        cv2.imwrite('final_image.jpg', image)  # Salva a imagem processada para depuração
        self.i += 1

    def releaseRunner(self):
        self.runner.stop()    