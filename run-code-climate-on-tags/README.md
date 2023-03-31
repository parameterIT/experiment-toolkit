# code-climate-testing

A utility tool to get code climate results in a format similar to our tool.

## Set-up:

A `.env` file at the project root

```
CODE_CLIMATE_TOKEN="<YOUR-CODE-CLIMATE-ACCESS-TOKEN>"
```

## Running:

Execute through the `run.sh` script:

```sh
./run.sh <GITHUB_SLUG>
```

Where `<GITHUB_SLUG>` is in the format `username/reponame`

## Notes:

Since the results are collected using CodeClimate's API their are some naming inconsistencies with Code Climate's web UI;

- `method_complexity` is the same as Cognitive Complexity

