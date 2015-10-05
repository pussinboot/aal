### aal - album art learner

creates a ~~feed-forward classification network~~ sparse dictionary for album art pulled from your last.fm's top n albums

allowing you to test images and identify what album they are

![here's a preview](https://raw.githubusercontent.com/pussinboot/aal/master/preview.png)

#### install

```
git clone https://github.com/pussinboot/aal.git
cd aal
python setup.py install
```

then you can run with `aal`

#### dependencies

you need to install tkdnd from [here](http://www.sourceforge.net/projects/tkdnd/)

make sure to get correct version (64-bit or 32-bit), and install it to python directory /tcl/tkdnd2.8/

otherwise you need to add the following line `os.environ['TKDND_LIBRARY'] = # directory where tkdnd is`

if you get `ImportError: cannot import name _imagingtk` then you need to reinstall pillow with the following command `pip install -I --no-cache-dir Pillow`