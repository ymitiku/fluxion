#!/bin/bash
# Copied from https://stackoverflow.com/a/28464339/5825953
# Remove all branches that are already merged into the currently checked out branch

git branch --merged >/tmp/merged-branches && \
sed -i '/main/d' /tmp/merged-branches && \
sed -i '/master/d' /tmp/merged-branches && \
sed -i '/gh-pages/d' /tmp/merged-branches && \
sed -i '/release-*/d' /tmp/merged-branches && \

nano /tmp/merged-branches && xargs git branch -d </tmp/merged-branches