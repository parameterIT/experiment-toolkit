FROM ubuntu:latest

ARG repository_name=default_value
ARG repository_path=default_value
ARG language=default_value

#Install dependencies
RUN apt-get update && apt-get -y install git \
    python3.11 python3-distutils python3-pip python3-apt
RUN pip install poetry
#Create working directory
RUN mkdir app
COPY run-byoqm-on-tags.sh app/run-byoqm-on-tags.sh
#clone needed parameters
ARG username=$GIT_USERNAME
ARG password=$GIT_PASSWORD
RUN cd app 
RUN git clone https://github.com/parameterIT/tool \
    git clone https://github.com/parameterIT/testing \
    git clone $repository_path
 
RUN app/run-byoqm-on-tags.sh $repository_name $language