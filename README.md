# Experiment

This repository contains all the necessary files to recreate an experiment that compares our implementation of Code Climate's quality model against the actual Code Climate tool.
Additionally, it contains the actual data that we have used in our comparison of the two quality models.
It consists of three parts:

1. A bash script to run our tool on all the tags of a given git repository
2. A python program to run code climate on all the tags of a given git repository, outputting in a format compatible with our tool (this can also be run through a bash script)
3. A python program that can visualize the outputs of the two aforementioned parts using bokeh

## Set-up 

The tools use your local installation of git, so make sure that it is set-up available in your PATH.
Second, tool (1) requires that the git repository you wish to execute `byoqm` on is a sibling folder to this folder.
Make sure that you have the following folder structure:

```
<repository>
  .git
experiment-toolkit
```

Where `repository` is a local copy of repository that you wish to execute the experiment on.

Furthermore, you will need to have cloned the parameterIT/testing repository as a sibling directory as well. The final folder structure should look something like this: 
```
<repo>
  .git
experiment-toolkit
testing
```

To visualize the results you need to follow some set-up related to bokeh.
The following [link](https://docs.bokeh.org/en/latest/docs/user_guide/output/export.html) explains the set-up on their documentation.

This tool also requires the user to have poetry installed.

## Running
First ensure that you are in the `experiment-toolkit` folder.

Then run `byoqm` on the local repository by executing

```sh
./run-byoqm-on-tags.sh <repository-name>
```
e.g.
```sh
./run-byoqm-on-tags.sh flask
```

This will produce a sibling folder name `<repo>-tags` so that you have the folder structure:

```
<repo>
  .git
experiment-toolkit
<repo>-tags
  <repo>-tagx
  <repo>-tagy
  <repo>-tagz
```

Second, change your working directory to the following directory, and run poetry install:
```.sh
cd run-code-climate-on-tags
poetry install
```
For the following part, you will need a code climate authentication token. You can generate a token on the following website after having connected it to github https://codeclimate.com/profile/tokens.

To run the shell script, you will need a '.env' file with a token export command:
```sh
touch .env
```

Open the .env file and insert the following command:

linux:
```
CODE_CLIMATE_TOKEN="<YOUR-CODE-CLIMATE-ACCESS-TOKEN>"
```
mac:
```
export CODE_CLIMATE_TOKEN=<YOUR-CODE-CLIMATE-ACCESS-TOKEN>
```

Remember to save the file.

Now, run the Code Climate tool by using the following command. NOTE: github-slug in the format `username/repository-name`:

```sh
./run.sh <repo> <github-slug>
```
e.g.
```sh
./run.sh flask pallets/flask
```


Finally, move the results of the `byoqm` tool and the Code Climate tool into `visualization/output/byoqm` and `visualization/output/code_climate` respectively.
Then you can run the visualization tool:

```sh
cd visualization
poetry run python main.py <png-file-prefix>
```

Where `<png-file-prefix>` will be prepended to the file name of any PNG file that is generated to help organize the output.
