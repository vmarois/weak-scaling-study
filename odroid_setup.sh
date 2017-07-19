#!/bin/bash
# This script can be used to set up an odroid (xu4 or otherwise)
# to run the stable FEniCS docker image.

echo "Upgrading packages first."
apt-get update && apt-get upgrade
echo "Installing Git."
apt-get install git
echo "Installing Docker.io."
apt-get install docker.io
echo "Fixing Uni.Lu DNS issue : may not be necessary in your case."
echo '{
    "dns": ["10.236.9.10"]
}
' > /etc/docker/daemon.json
echo "Adding a group 'docker', and adding the user to that group. Allows running Docker commands without specifying sudo first." 
sudo groupadd docker
sudo usermode -aG docker $USER
echo "Cloning https://vincentmarois@bitbucket.org/vincentmarois/docker.git"
git clone https://vincentmarois@bitbucket.org/vincentmarois/docker.git
git checkout jackhale/feature-armhf-support
cd docker/dockerfiles/
set -e
RANDOM_TAG=$RANDOM

# Note: These images do need to be built in a particular order!
# dev-env-trilinos takes so long to compile, I have left it out.

# We need to rebuild the phusion/baseimage first
git clone https://github.com/jhale/baseimage-docker.git
cd baseimage-docker
git checkout jhale/feature-armhf-support
cd image
docker build --tag phusion/baseimage:0.9.22-armhf -f Dockerfile .
cd ../../

#We can now build the upper images
for image in base dev-env stable
do
    cd ${image}
    sed -e "s#quay.io/fenicsproject/${LAST_IMAGE}:latest#quay.io/fenicsproject/${LAST_IMAGE}:${RANDOM_TAG}#g" Dockerfile > Dockerfile.tmp
    docker build --tag quay.io/fenicsproject/${image}:${RANDOM_TAG} -f Dockerfile.tmp .
    LAST_IMAGE=${image}
    rm Dockerfile.tmp
    cd ../
done

echo ""
echo "Finished. A stack of images with the tag $RANDOM_TAG has been built, e.g.:"
echo ""
echo "  docker run -ti quay.io/fenicsproject/stable:${RANDOM_TAG}."
echo ""
echo "These images have not been pushed to quay.io."
