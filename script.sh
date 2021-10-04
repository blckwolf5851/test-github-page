cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug ../test-github-page
ninja -v
ctest -T Test
ctest -T Coverage