import numpy as np

# Imports for visualization
import PIL.Image

def resizeAsNeeded(img, max_size=(2000,2000), max_fail_size=(2000,2000)):
  if not PIL.Image.isImageType(img):
    img = PIL.Image.fromarray(img) # Convert to PIL Image if not already

  # If image is larger than fail size, don't try resizing and give up
  if img.size[0] > max_fail_size[0] or img.size[1] > max_fail_size[1]:
    return None

  """Resize if image larger than max size"""
  if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
    print("Image too big (%d x %d)" % (img.size[0], img.size[1]))
    new_size = np.min(max_size) # px
    if img.size[0] > img.size[1]:
      # resize by width to new limit
      ratio = np.float(new_size) / img.size[0]
    else:
      # resize by height
      ratio = np.float(new_size) / img.size[1]
    print("Reducing by factor of %.2g" % (1./ratio))
    new_size = (np.array(img.size) * ratio).astype(int)
    print("New size: (%d x %d)" % (new_size[0], new_size[1]))
    img = img.resize(new_size, PIL.Image.BILINEAR)
  return img