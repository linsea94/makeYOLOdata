import fiftyone as fo
import fiftyone.zoo as foz

#
# Load 50 random samples from the validation split
#
# Only the required images will be downloaded (if necessary).
# By default, only detections are loaded
#

dataset = foz.load_zoo_dataset(
    "coco-2017",
    split="train",
    max_samples=1000,
    shuffle=True,
    label_types=["detections"],
    classes=["motorcycle"],
)

session = fo.launch_app(dataset)

#
# Load segmentations for 25 samples from the validation split that
# contain cats and dogs
#
# Images that contain all `classes` will be prioritized first, followed
# by images that contain at least one of the required `classes`. If
# there are not enough images matching `classes` in the split to meet
# `max_samples`, only the available images will be loaded.
#
# Images will only be downloaded if necessary
#

# dataset = foz.load_zoo_dataset(
#     "coco-2017",
#     split="validation",
#     label_types=["segmentations"],
#     classes=["cat", "dog"],
#     max_samples=25,
# )

# session.dataset = dataset