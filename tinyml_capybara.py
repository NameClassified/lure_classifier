"""
Collect images from Esp32-cam web server
"""
from everywhereml.data import ImageDataset
from everywhereml.data.collect import MjpegCollector
from everywhereml.preprocessing.image.object_detection import HogPipeline
from everywhereml.preprocessing.image.transform import Resize
from everywhereml.sklearn.ensemble import RandomForestClassifier

base_folder = 'animals'
def load_data():
    try:
        # if our dataset folder already exists, load it
        
        image_dataset = ImageDataset.from_nested_folders(
            name='animals', 
            base_folder=base_folder
        )
       

    except FileNotFoundError:
        # if the dataset folder does not exists, collect the samples
        # from the Esp32-cam web server
        # duration is how long (in seconds) the program will collect 
        # the images for each class
        mjpeg_collector = MjpegCollector(address='http://192.168.105.76')
        image_dataset = mjpeg_collector.collect_many_classes(
            dataset_name='animals', 
            base_folder=base_folder,
            duration=40
        )
    
    print(image_dataset)
    #image_dataset = image_dataset.gray().uint8()
    return image_dataset



def create_arduino_model(image_dataset):

    pipeline = HogPipeline(
        transforms=[
            Resize(width=40, height=30)
        ]
    )

    # Convert images to feature vectors
    feature_dataset = pipeline.fit_transform(image_dataset)
    feature_dataset.describe()
    print(pipeline)
    #feature_dataset.plot.features_pairplot(n=200, k=8)
    feature_dataset.plot.umap()

    clf = RandomForestClassifier(n_estimators=10, max_depth=40)

    # fit on train split and get accuracy on the test split
    train, test = feature_dataset.split(test_size=0.3)
    clf.fit(train)

    print('Score on test set: %.2f' % clf.score(test))

    # now fit on the whole dataset
    clf.fit(feature_dataset)
    print(pipeline.to_arduino_file(
        filename='lure_classifier/lure_classifier/HogPipeline.h',
        instance_name='hog'))

    print(clf.to_arduino_file(
        filename='lure_classifier/lure_classifier/HogClassifier.h',
        instance_name='classifier', 
        class_map=feature_dataset.class_map))

if __name__ == "__main__":
    image_dataset = load_data()
    create_arduino_model(image_dataset)