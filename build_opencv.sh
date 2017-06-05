if [ -n "$(ls -A opencv/build)" ];
then
    cd opencv;
    git init;
    git remote add origin https://github.com/Itseez/opencv.git;
    git fetch origin 2.4;
    git checkout origin/2.4;
    ls;
    cd build;
    ls;
else
    rm -r opencv;
    git clone https://github.com/Itseez/opencv.git;
    cd opencv;
    git checkout 2.4;
    mkdir build;
    cd build;
    cmake -DCMAKE_INSTALL_PREFIX=/usr ..;
    make -j8;
fi
