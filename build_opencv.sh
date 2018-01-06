if [ -n "$(ls -A opencv/build)" ];
then
	# We're using a cached version of our OpenCV build
	cd opencv;
	git init;
	git remote add origin https://github.com/Itseez/opencv.git;
	git fetch origin tags/3.4.0 -b release;
	git checkout release;
else
	# No OpenCV cache – clone and make the files
	rm -r opencv;
	git clone https://github.com/Itseez/opencv.git;
	cd opencv;
	git fetch origin tags/3.4.0 -b release;
	git checkout release;
	mkdir build;
	cd build;
	cmake -D CMAKE_INSTALL_PREFIX=/usr;
	make -j8;
fi
