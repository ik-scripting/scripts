#!/bin/bash
# https://github.com/claranet/terraform-datadog-scripts/blob/06f6797a48e2e15c9ad4725ade196e4f79a46b96/20_update_global_readme.sh
source "$(dirname $0)/utils.sh"
init
echo "Update global README.md"

# only keep current README from begining to "[Monitors/Integrations] summary" section (delete list)
sed -i "/## ${REPO^} summary/q" README.md
# add a newline after listing section
echo >> README.md
# loop over path of modules tree
for path in $(find -mindepth 1 -type d ! -path '*/.*' ! -path './scripts*' ! -path './common/module' -print | sort -fdbi); do
    # split path in directories
    directories=($(list_dirs $path))
    # loop over directories in path
    for i in $(seq 1 $((${#directories[@]}-1))); do
        ## add tabulation for every subdirectory
        echo -en "\t" >> README.md
    done
    # add link to list of modules
    echo -en "- [$(basename ${path})](https://github.com/claranet/terraform-datadog-${REPO}/tree/master/" >> README.md
    # add path to link
    for directory in "${directories[@]}"; do
        echo -en "${directory}/" >> README.md
    done
    # end of markdown link
    echo ")" >> README.md
done