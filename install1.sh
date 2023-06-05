#!/bin/bash

IDFILE=$'1b0wGO7fyNFyyByL_vdaHqZZZKqDQVDkV'
OFFICE=$'DEBS'
# Check if the user is root
if [[ $EUID -ne 0 ]]; then
    echo "You must be root to run this script."
    echo "Enter the Password: "
    read -s password
fi
echo "Starting"
sudo -S <<< "$password" apt-get update -y
sudo -S <<< "$password" apt-get upgrade -y

sleep 5
rm -rf "$OFFICE.zip" "$OFFICE"

myArray=("git" "python3-pip" "vim" "curl" "wget" "unzip")
for package_name in ${myArray[@]}; do
    if ! dpkg -s "$package_name" >/dev/null 2>&1; then
        echo "Failed to install the package $package_name."
        sudo -S <<< "$password" apt-get install $package_name -y  > /dev/null 2>&1
    else
        echo "Installed the package $package_name."  
    fi
done
sleep 5
myArray1=("gdown" "flask")
for package_name in ${myArray1[@]}; do
    if ! pip3 show "$package_name" &> /dev/null; then
        pip3 install "$package_name"
    fi
done
sleep 5
gdown 'https://drive.google.com/uc?id='"$IDFILE" -O "$OFFICE.zip"

unzip  "$OFFICE.zip" > /dev/null 2>&1
sudo -S <<< "$password" apt autoremove -y 
echo "Install Backages"
package_name=( "libreoffice7.5" "libreoffice")
for package_name1 in ${package_name[@]}; do
    if dpkg -s "$package_name1" >/dev/null 2>&1; then
        # echo "Failed to install the package $package_name1." 
        sudo -S <<< "$password" apt-get remove "$package_name1" -y   > /dev/null 2>&1
    fi
done
sleep 5
cd  "$OFFICE"
sudo -s <<< apt-get install libreoffice -y  > /dev/null 2>&1
sudo -S <<< "$password" apt autoremove -y > /dev/null 2>&1
sleep 5
sudo -S <<< "$password" dpkg -i lib*.deb > /dev/null 2>&1
sudo -S <<< "$password" apt-get install -f
libreoffice7.5 --version > /dev/null 2>&1
cd ..
rm -rf "$OFFICE.zip" "$OFFICE"
echo "Finish"
exit 1