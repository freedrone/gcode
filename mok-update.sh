#!/usr/bin/env bash
git stash
git stash clear
git checkout master
git pull origin master
exit
