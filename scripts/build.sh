#!/bin/bash

# 1. build quartz
cd quartz
npx quartz build --directory ../content

# 2. copy assets
rsync -av ../assets/ public/assets/
rsync -av ../attachment/ public/attachment/