#!/bin/bash

# Check if the user is root
# if [[ $EUID -ne 0 ]]; then
#     echo "You must be root to run this script."
#     exit 1
# fi
# arrayA=$"https://drive.google.com/file/d/1g-syIE-hJWKX3JLG7wGjNcVaXqGXGu_r/view?usp=sharing"
# arrayA=$"https://drive.google.com/uc?export=download&id=1MIonPSquLkrdzZ5Mhc-fp9MjxBHZCN4v"
arrayA=$"https://drive.google.com/uc?id=1MIonPSquLkrdzZ5Mhc-fp9MjxBHZCN4v&export=download"
# Get the package name from the user
echo "Enter the package name: "
echo $arrayA
curl -L $arrayA > phlat.zip
# read package_name
# myArray=("vim" "libreoffice" "wget")
# for package_name in ${myArray[@]}; do
#     if ! dpkg -s "$package_name" >/dev/null 2>&1; then
#         echo "Failed to install the package $package_name."
#     else
#         echo "Installed the package $package_name."  
#     fi
# done
exit 1
# Check if the package was installed successfully
# if ! dpkg -s "$package_name" >/dev/null 2>&1; then
#   echo "Failed to install the package $package_name."
#   exit 1
# else 
# fi
# Install the package
#sudo apt install "$package_name"

