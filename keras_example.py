import matplotlib.pyplot as plt
import pandas as pd
import keras_ocr

# keras-ocr will automatically download pretrained
# weights for the detector and recognizer.
pipeline = keras_ocr.pipeline.Pipeline()

# Each list of predictions in prediction_groups is a list of
# (word, box) tuples.
prediction_groups = pipeline.recognize(["20231009-181355-189-01.jpg"])

results_df = pd.DataFrame(prediction_groups[0])
print(results_df)

# Plot the predictions
# fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))
# print(fig)
# print(axs)
# keras_ocr.tools.drawAnnotations(image=images[0], predictions=prediction_groups[0], ax=axs[0])
# for ax, image, predictions in zip(axs, images, prediction_groups):
#     keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
