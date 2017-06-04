ls
ls opencv
ls opencv/build
files=(opencv/build/*)
if [ -n "$(ls -A sad)" ]
then
    echo "cache exists"
else
    rm -r opencv
fi
git clone https://github.com/Itseez/opencv.git
cd opencv
git checkout 2.4
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr ..
make -j8
sudo make install
cd ../../
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/site-packages/
ls
ls opencv
ls opencv/build
