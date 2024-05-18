# syntax=docker/dockerfile:1
# this is docker image for executing game in safe envirioment

   
FROM condaforge/mambaforge:23.1.0-1
WORKDIR /tmp
RUN mamba install  -y matplotlib numpy

RUN useradd -ms /bin/bash the-game

USER the-game

WORKDIR /game
