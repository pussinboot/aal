### aal - album art learner

creates a ~~feed-forward classification network~~ sparse dictionary for album art pulled from your last.fm's top n albums

allowing you to test images and identify what album they are

![here's a preview](https://raw.githubusercontent.com/pussinboot/aal/master/preview.png)

#### dependencies

you need to install tkdnd from [here](sourceforge.net/projects/tkdnd/)

make sure to get correct version (64-bit or 32-bit), and install it to python directory /tcl/tkdnd2.8/

otherwise you need to add the following line `os.environ['TKDND_LIBRARY'] = # directory where tkdnd is`