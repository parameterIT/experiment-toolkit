# Experiment

This repository contains all the necessary files to recreate an experiment that compares our implementation of Code Climate's quality model against the actual Code Climate tool.
Additionally, it contains the actual data that we have used in our comparison of the two quality models.
It consists of three parts:

1. A bash script to run our tool on all the tags of a given git repository
2. A python program to run code climate on all the tags of a given git repository, outputting in a format compatible with our tool
3. A python program that can visualize the outputs of the two aforementioned parts using bokeh

## Set-up 

The tools use your local installation of git, so make sure that it is set-up available in your PATH.
Second, tool (1) requires that the git repository you wish to execute `byoqm` on is a sibling folder to this folder.
Make sure that you have the following folder structure:

```
<repo>
  .git
experiment-toolkit
```

Where `repo` is a local copy of repository that you wish to execute the experiment on.

To visualize the results you need to follow some set-up related to bokeh.
The following [link](https://docs.bokeh.org/en/latest/docs/user_guide/output/export.html) explains the set-up on their documentation.

## Running

First run `byoqm` on the local repository by executing

```sh
./run-byoqm-on-tags.sh
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

Second run the Code Climate tool pointing referring to the remote of the aforementioned local repository as a github slug in the format `username/repository-name`:

```.sh
cd run-code-climate-on-tags
poetry run python main.py <github-slug>
```


Now move the results of the `byoqm` tool and the Code Climate tool into `visualization/output/byoqm` and `visualization/output/code_climate` respectively.
Then you can run the visualization tool:

```sh
cd visualization
poetry run python main.py
```
