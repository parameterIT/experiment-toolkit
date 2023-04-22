# Experiment

This repository contains all the necessary files to recreate an experiment that compares our implementation of Code Climate's quality model against the actual Code Climate tool.
Additionally, it contains the actual data that we have used in our comparison of the two quality models.
It consists of four components:

1. A bash script that transforms a local git repository into a folder per tag of that git repository
2. A python program that will run [modu](https://github.com/parameterIT/tool/) on each sub-directory of a given directory (this will be paired with script (1))
3. A python program that runs code climate on each sub-directory of a given directory (this will be paired with script (1))
4. A python program that compares the results of (2) and (3) visually on line graphs

## Requirements

- Many of the provided scripts and programs make use of your local installation of _git_, so make that it is set-up and available in your PATH.
- Component (2) requires a local installation of _modu_. The project's [README](https://github.com/parameterIT/tool/blob/main/README.md) describes how to set it up
- To visualize the results we use [_Bokeh_](https://docs.bokeh.org/en/latest/index.html), which requires [additional set-up](https://docs.bokeh.org/en/latest/docs/user_guide/output/export.html) for exporting the graphs to PNG files
- It requires that you have push access to and a local copy of [parameterIT's testing repository](https://github.com/parameterIT/testing)

## Running

### Preparing the Data

First it will be necessary to transform a git repository into a series of folders each containing that git repository's contents at a specific version.
The following command (from the `experiment-toolkit` folder) executes a bash script which automates this process:

```shell
./explode-git-tags-into-folders.sh <path-to-local-git-repo> <path-to-folder-for-tags> <repo-name-for-tag-folders>
```

Where the first argument is the relative path to the local git repository which you wish to transform into a series of folders for each of its tags.
The second argument is the path to the parent folder you wish to contain all these folders (the script will make the folder if it doesn't exist).
The third argument is the name that each folder representing a tag should have, i.e. this script will name each sub-directory to the `<tags-folder>` `<repo-name-for-tag-folders>-<git-tag>` to help organize the output.


For example:

```shell
./explode-git-tags-into-folders.sh ../flask ../flask-tags flask
```

yields the directory-tree:
```
experiment-toolkit
  \_ explode-git-tags-into-folders.sh
flask
  \_ .git
flask-tags
  \_ flask-0.1
  \_ flask-0.10
  \_ flask-0.10.1
  \_ flask-0.11
  \_ flask-0.11.1
  \_ flask-0.12
  \_ ...
```

### Executing _modu_

First ensure that you are in the `experiment-toolkit` folder.

Then run _modu_ on the local repository by executing

```sh
./run-modu-on-tags.py <relative-path-to-git-root-folder-of-modu> <path-to-folder-containing-tags>
```

For example with the directory tree:
```
experiment-toolkit
  \_ explode-git-tags-into-folders.sh
flask-tags
  \_ flask-0.1
  \_ flask-0.10
  \_ flask-0.10.1
  \_ flask-0.11
  \_ flask-0.11.1
  \_ flask-0.12
  \_ ...
modu
  \_ .git
  \_ README.md
  \_ modu
  \_ ...
```

You can run the command

```sh
./run-modu-on-tags.sh ../modu ../flask-tags
```

This will execute _modu_ on each of the sub-directories in `flask-tags`, saving the results to _modu_'s default output (the output folder in the _modu_ folder)

### Executing Code Climate

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

Now, run the Code Climate tool by using the following command. NOTE: github-slug is in the format `username/repository-name`:

```sh
./run.sh <path to local copy of repository> <github-slug of the remote of the repo> <path to testing repository>
```

For example with the directory structure:
```
experiment-toolkit
  \_ run-code-climate-on-tags
    \_ run.sh
flask
  \_ .git
testing
  \_ .git
```

You can run the command:
```sh
./run.sh ../../flask pallets/flask ../../testing
```

This will produce .csv files that match the format of _modu_ using results gathered through code climate in the `experiment-toolkit/run-code-climate-on-tags/output` folder.

### Visualization

Move the results of the _modu_ tool and the Code Climate tool into `visualization/output/byoqm` and `visualization/output/code_climate` respectively.
Then you can run the visualization tool:

```sh
cd visualization
poetry install
poetry run python main.py <png-file-prefix>
```

Where `<png-file-prefix>` will be prepended to the file name of any PNG file that is generated to help organize the output.
